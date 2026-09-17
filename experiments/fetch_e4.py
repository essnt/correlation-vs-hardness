"""E4 data acquisition: SATLIB archives + SAT Competition 2024 repo.

Network-only work (no CPU contention with solver pools).  Downloads into
data/external/ with a manifest; caps total download at ~2 GB per the frozen
budget.  Failures are logged, never fatal — E4 proceeds with whatever lands.
"""
import os
import re
import socket
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "data", "external")
CAP_BYTES = 2_000_000_000
MANIFEST = os.path.join(DEST, "MANIFEST.md")

SATLIB_PAGE = "https://www.cs.ubc.ca/~hoos/SATLIB/"
SATCOMP_REPO = "https://codeload.github.com/satcompetition/2024/tar.gz/refs/heads/main"

# Verified 2026-09-09: the ~hoos/SATLIB index pages carry no direct archive
# links; the working hosts are www.satlib.org/<path>.tar.gz (200) and the
# codeload tarball for the SAT-2024 repo (117 MB, includes downloads/meta.csv
# with 400 hash-identified instances; instance bodies still need a source).
ARCHIVES = [
    "https://www.satlib.org/Benchmarks/SAT/uniform/uniform.tar.gz",
    "https://www.satlib.org/Benchmarks/SAT/uniform/uf200-860.tar.gz",
    "https://www.satlib.org/Benchmarks/SAT/bmc/bmc.tar.gz",
    "https://www.satlib.org/Benchmarks/SAT/bmc/ibm-bmc.tar.gz",
    "https://www.satlib.org/Benchmarks/SAT/structural/structural.tar.gz",
]

ALLOWED_HOSTS = {"www.satlib.org", "codeload.github.com"}


def _guard(url: str) -> None:
    u = urllib.parse.urlparse(url)
    assert u.scheme == "https" and u.netloc in ALLOWED_HOSTS, f"blocked host: {u.netloc}"


def _safe_name(url: str) -> str:
    name = os.path.basename(urllib.parse.urlparse(url).path)
    assert re.fullmatch(r"[A-Za-z0-9._-]+", name), f"unsafe filename: {name}"
    return name


def fetch_satlib() -> list[str]:
    got = []
    total = 0
    for url in ARCHIVES:
        name = _safe_name(url)
        _guard(url)
        dest = os.path.join(DEST, name)
        if os.path.exists(dest):
            print(f"skip (exists): {name}")
            got.append(dest)
            continue
        try:
            urllib.request.urlretrieve(url, dest)
            total += os.path.getsize(dest)
            print(f"downloaded: {name} ({total/1e6:.0f} MB cumulative)")
            got.append(dest)
            if total > CAP_BYTES:
                print("cap reached; stopping SATLIB downloads")
                break
        except Exception as e:
            print(f"failed: {name}: {e}")
    return got


def fetch_satcomp() -> str | None:
    dest = os.path.join(DEST, "satcomp2024")
    if os.path.exists(dest):
        print("skip (exists): satcomp2024")
        return dest
    tmp = os.path.join(DEST, "satcomp2024.tar.gz")
    if not os.path.exists(tmp):
        _guard(SATCOMP_REPO)
        try:
            urllib.request.urlretrieve(SATCOMP_REPO, tmp)
            print(f"downloaded satcomp2024 tarball ({os.path.getsize(tmp)/1e6:.0f} MB)")
        except Exception as e:
            print(f"satcomp2024 download failed: {e}")
            return None
    import tarfile
    with tarfile.open(tmp) as t:
        t.extractall(DEST, filter="data")
    out = os.path.join(DEST, "2024-main")
    return out if os.path.exists(out) else None


def main() -> None:
    socket.setdefaulttimeout(600)
    os.makedirs(DEST, exist_ok=True)
    lines = ["# E4 data manifest", f"# fetched 2026-09-09", ""]
    lines += [f"- {p}" for p in fetch_satlib()]
    sc = fetch_satcomp()
    if sc:
        lines.append(f"- {sc} (git)")
    Path(MANIFEST).write_text("\n".join(lines) + "\n")
    print(f"manifest -> {MANIFEST}")


if __name__ == "__main__":
    main()
