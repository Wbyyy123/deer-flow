#!/usr/bin/env python3
"""GitHub source snapshot helper for github-project-brief.

Resolves a branch's commit SHA through GitHub's git smart-HTTP refs
advertisement (official, unauthenticated, and *not* the REST API that
rate-limits unauthenticated clients), downloads files pinned to that SHA,
and emits a JSON manifest with per-file byte size, line count and SHA-256
so report citations can point at an immutable snapshot instead of a moving
branch.

Security: never reads or prints GITHUB_TOKEN or any other secret. All
fetches are unauthenticated public endpoints. Downloaded paths are validated
before writing: absolute paths, ``..`` traversal, and anything that resolves
outside the snapshot directory are rejected.

Network failures (HTTP 403/404, timeouts, URLError) are converted into
structured ``SnapshotError`` exceptions with an explicit kind/status. They
never crash the process with a bare traceback, and an unresolved SHA is never
labelled as pinned.
"""

import argparse
import hashlib
import json
import os
import ntpath
import re
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import quote

USER_AGENT = "deerflow-github-snapshot/1.1"

# Known candidate files used when the caller does not supply an explicit list
# (e.g. when the REST ``tree`` endpoint returns 403 and the agent falls back to
# README + well-known official files).
DEFAULT_FILES = [
    "README.md",
    "README",
    "README.rst",
    "README.txt",
    "README.markdown",
    "readme.md",
    "readme.rst",
    "readme.txt",
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Makefile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "docker-compose-dev.yml",
    "docker-compose-dev.yaml",
    "docker/docker-compose.yml",
    "docker/docker-compose.yaml",
    "docker/docker-compose-dev.yml",
    "docker/docker-compose-dev.yaml",
    "docs/ARCHITECTURE.md",
    "docs/architecture.md",
    "docs/INSTALL.md",
    "docs/install.md",
    "docs/deployment.md",
    "docs/guide/deployment.md",
]


class SnapshotError(Exception):
    """A structured, human-readable failure with a kind and numeric status.

    kind is one of: http, timeout, url, network, parse.
    """

    def __init__(self, kind, status, detail=""):
        self.kind = kind
        self.status = status
        self.detail = detail
        super().__init__(f"{kind} status={status} {detail}".strip())


class BranchNotFoundError(Exception):
    """Raised when a caller-specified branch does not exist on the remote."""

    def __init__(self, branch, available):
        self.branch = branch
        self.available = available
        super().__init__(f"branch '{branch}' not found")


def _validate_repo_part(value, label):
    """Reject GitHub path segments that could alter URLs or output paths."""
    if not isinstance(value, str) or value in ("", ".", ".."):
        raise argparse.ArgumentTypeError(f"invalid GitHub {label}")
    if len(value) > (39 if label == "owner" else 100):
        raise argparse.ArgumentTypeError(f"GitHub {label} is too long")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise argparse.ArgumentTypeError(
            f"invalid GitHub {label}: use only letters, numbers, '.', '_' and '-'"
        )
    return value


def _http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        raise SnapshotError("http", e.code, f"HTTP {e.code} for {url}")
    except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
        reason = getattr(e, "reason", e)
        text = str(reason).lower()
        if isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in text or "timeout" in text:
            raise SnapshotError("timeout", 0, f"timeout for {url}: {reason}")
        raise SnapshotError("url", 0, f"URL/network error for {url}: {reason}")
    except Exception as e:  # pragma: no cover - defensive
        raise SnapshotError("network", 0, f"unexpected network error for {url}: {e}")


def _parse_pkt_lines(data):
    """Yield (length, payload) pkt-lines from a git protocol advertisement."""
    i = 0
    n = len(data)
    while i + 4 <= n:
        hexlen = data[i:i + 4].decode("ascii", "replace")
        i += 4
        if hexlen == "0000":
            continue  # flush-pkt
        try:
            length = int(hexlen, 16)
        except ValueError:
            break
        if length < 4:
            continue
        payload = data[i:i + length - 4]
        i += length - 4
        yield length, payload


def resolve_refs(owner, repo, timeout=30):
    """Return (refs, symref_branch) from the git smart-HTTP refs advertisement.

    Raises SnapshotError on any network or parse failure.
    """
    url = f"https://github.com/{owner}/{repo}.git/info/refs?service=git-upload-pack"
    status, body = _http_get(url, timeout=timeout)
    if status != 200:
        raise SnapshotError("http", status, f"refs endpoint returned HTTP {status}")

    refs = {}
    symref_branch = None
    for _length, payload in _parse_pkt_lines(body):
        if b"\x00" in payload:
            line, caps = payload.split(b"\x00", 1)
        else:
            line, caps = payload, b""
        text = line.decode("utf-8", "replace").rstrip("\n")
        parts = text.split(" ")
        if len(parts) < 2:
            continue
        sha, refname = parts[0], parts[1]
        if len(sha) == 40 and all(c in "0123456789abcdefABCDEF" for c in sha):
            refs[refname] = sha
        if refname == "HEAD" and caps:
            for cap in caps.decode("utf-8", "replace").split(" "):
                if cap.startswith("symref=HEAD:refs/heads/"):
                    symref_branch = cap.split("refs/heads/", 1)[1]

    if not refs:
        raise SnapshotError("parse", status, "no refs parsed from advertisement")
    return refs, symref_branch


def pick_commit_sha(refs, symref_branch, branch=None):
    """Choose an explicitly requested branch or a reliably advertised default.

    Returns (sha, source_label, branch). Never silently chooses an unrelated
    branch when the server did not advertise which branch is the default.
    """
    if branch is not None:
        key = f"refs/heads/{branch}"
        if key not in refs:
            available = sorted(k for k in refs if k.startswith("refs/heads/"))
            raise BranchNotFoundError(branch, available)
        return refs[key], f"git-refs {key}", branch

    if symref_branch:
        key = f"refs/heads/{symref_branch}"
        if key not in refs:
            raise SnapshotError(
                "parse", 0, f"HEAD points to {key}, but that ref was not advertised"
            )
        return refs[key], f"git-refs {key}", symref_branch

    main_key = "refs/heads/main"
    if main_key in refs:
        return refs[main_key], f"git-refs {main_key}", "main"

    if "HEAD" in refs:
        return refs["HEAD"], "git-refs HEAD", "unknown (HEAD; branch name not advertised)"

    raise SnapshotError(
        "parse", 0, "default branch was not advertised; pass --branch explicitly"
    )

def _line_count(data):
    text = data.decode("utf-8", "replace")
    if not text:
        return 0
    n = text.count("\n")
    return n if text.endswith("\n") else n + 1


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _safe_target(snapshot_dir, path):
    """Validate and join a repository-relative path inside snapshot_dir."""
    if not isinstance(path, str) or not path or not path.strip():
        return None, "empty path"
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in path):
        return None, "path contains a control character"
    if os.path.isabs(path) or ntpath.isabs(path) or ntpath.splitdrive(path)[0]:
        return None, f"absolute path rejected: {path!r}"

    norm = path.replace(chr(92), "/")
    if norm.startswith("/"):
        return None, f"absolute path rejected: {path!r}"
    parts = norm.split("/")
    if any(part == ".." for part in parts):
        return None, f"path traversal rejected: {path!r}"
    cleaned = [part for part in parts if part not in ("", ".")]
    if not cleaned:
        return None, "empty path"

    base_real = os.path.realpath(os.path.abspath(snapshot_dir))
    target = os.path.normpath(os.path.join(snapshot_dir, *cleaned))
    target_real = os.path.realpath(target)
    try:
        common = os.path.commonpath([base_real, target_real])
    except ValueError:
        return None, f"path escapes snapshot dir: {path!r}"
    if os.path.normcase(common) != os.path.normcase(base_real):
        return None, f"path escapes snapshot dir: {path!r}"
    return target, None

def download_file(owner, repo, ref, path, timeout=30):
    """Download one file pinned to ``ref``.

    Returns a manifest entry dict. On failure it returns ok=False with a
    structured ``error`` field instead of raising, so one bad file never
    aborts the whole snapshot.
    """
    _, path_error = _safe_target(os.getcwd(), path)
    if path_error:
        return {
            "path": path,
            "ok": False,
            "error": {"kind": "path", "status": 0, "message": path_error},
            "http_status": 0,
            "bytes": 0,
            "lines": 0,
            "sha256": None,
        }
    url = (
        "https://raw.githubusercontent.com/"
        f"{quote(owner, safe='')}/{quote(repo, safe='')}/"
        f"{quote(ref, safe='/')}/{quote(path, safe='/')}"
    )
    try:
        status, body = _http_get(url, timeout=timeout)
    except SnapshotError as e:
        return {
            "path": path,
            "ok": False,
            "error": {"kind": e.kind, "status": e.status, "message": e.detail},
            "http_status": e.status,
            "bytes": 0,
            "lines": 0,
            "sha256": None,
        }
    if status != 200:
        return {
            "path": path,
            "ok": False,
            "error": {"kind": "http", "status": status, "message": f"HTTP {status}"},
            "http_status": status,
            "bytes": 0,
            "lines": 0,
            "sha256": None,
        }
    return {
        "path": path,
        "ok": True,
        "http_status": status,
        "bytes": len(body),
        "lines": _line_count(body),
        "sha256": _sha256(body),
        "content": body,
    }


def _run(args):
    try:
        refs, symref_branch = resolve_refs(args.owner, args.repo, timeout=args.timeout)
    except SnapshotError as e:
        print(f"ERROR: could not resolve commit SHA ({e.kind} status={e.status}): {e.detail}", file=sys.stderr)
        print("  No manifest written; commit_sha left unresolved and not marked pinned.", file=sys.stderr)
        return 2

    sha, sha_source, branch = pick_commit_sha(refs, symref_branch, args.branch)
    ref = sha if sha else branch
    pinned = sha is not None

    manifest = {
        "repo": f"{args.owner}/{args.repo}",
        "branch": branch,
        "commit_sha": sha,
        "commit_sha_source": sha_source,
        "pinned": pinned,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_ref_used": ref,
        "files": [],
    }

    branch_component = re.sub(r"[^A-Za-z0-9._-]+", "_", branch or "unresolved")
    if branch_component in ("", ".", ".."):
        branch_component = "unresolved"
    snapshot_component = sha[:12] if sha else branch_component
    snapshot_dir = os.path.join(
        args.out_dir, f"{args.owner}__{args.repo}__{snapshot_component}"
    )
    os.makedirs(snapshot_dir, exist_ok=True)

    files = args.files if args.files else DEFAULT_FILES
    for path in files:
        target, perr = _safe_target(snapshot_dir, path)
        if perr:
            manifest["files"].append({
                "path": path,
                "ok": False,
                "error": {"kind": "path", "status": 0, "message": perr},
                "http_status": 0,
                "bytes": 0,
                "lines": 0,
                "sha256": None,
            })
            continue
        entry = download_file(args.owner, args.repo, ref, path, timeout=args.timeout)
        if entry["ok"]:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as fh:
                fh.write(entry["content"])
            entry.pop("content", None)
            entry["written_to"] = target
        manifest["files"].append(entry)

    manifest["snapshot_dir"] = snapshot_dir
    manifest_path = os.path.join(snapshot_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    print(f"snapshot_dir: {snapshot_dir}")
    print(f"branch: {branch}")
    print(f"commit_sha: {sha}  (source: {sha_source})")
    print(f"pinned: {pinned}  fetched_at_utc: {manifest['fetched_at_utc']}")
    for f in manifest["files"]:
        status = "OK " if f["ok"] else "FAIL"
        detail = f["error"]["kind"] if f.get("error") else ""
        print(f"  [{status}] {f['path']} bytes={f['bytes']} lines={f['lines']} sha256={f['sha256']} {detail}".rstrip())

    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owner", type=lambda value: _validate_repo_part(value, "owner"))
    parser.add_argument("repo", type=lambda value: _validate_repo_part(value, "repo"))
    parser.add_argument("--branch", default=None, help="branch name; auto-detected if omitted")
    parser.add_argument("--files", nargs="*", default=None, help="repo-relative file paths")
    parser.add_argument("--out-dir", default="snapshots", help="directory to write files+manifest")
    parser.add_argument("--timeout", type=int, default=30, help="per-request timeout in seconds")
    parser.add_argument("--json", action="store_true", help="also print manifest JSON to stdout")
    args = parser.parse_args()

    try:
        code = _run(args)
    except BranchNotFoundError as e:
        avail = ", ".join(e.available) if e.available else "(none)"
        print(f"ERROR: branch '{e.branch}' does not exist on the remote.", file=sys.stderr)
        print(f"  Available branches: {avail}", file=sys.stderr)
        print("  No manifest written; did not fall back to HEAD.", file=sys.stderr)
        code = 3
    except SnapshotError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("  No manifest written.", file=sys.stderr)
        code = 2
    except Exception as e:  # pragma: no cover - defensive
        print(f"ERROR: unexpected failure: {e}", file=sys.stderr)
        code = 1

    sys.exit(code)


if __name__ == "__main__":
    main()
