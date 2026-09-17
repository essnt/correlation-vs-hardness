#!/usr/bin/env python3
"""E4-prime: 抓取可达网络中的真实 SAT 实例（SATLIB/SAT竞赛主轨在本网络不可达，见 M2_LOG 换源记录）。

源 A: github.com/marijnheule/benchmarks —— 组合/ crafted 真实实例（Green Hat/Steiner/26x26/matrix/
       mphf/packing/ptn/radio/wap/asias），文件名带 SAT/UNK 状态标记。每族取 ≤8 个、优先跨度覆盖。
源 B: github.com/msakai/bnn-verification —— MSE 2020 BNN 验证实例（真实工业编码，WCNF，
       附 .sol 最优值 ⇒ 状态已知）。硬子句保留、软子句丢弃 ⇒ 纯 SAT 实例。
源 C: archive.dimacs.rutgers.edu/pub/sat-files/benchmarks —— DIMACS 经典（as/tm，.Z 压缩）。

产出: data/external/e4prime/<source>/<family>/xxx.cnf
      data/external/e4prime/MANIFEST_prime.csv (source,family,file,sha256,bytes,n_vars,n_clauses,note)
幂等: 已存在且大小一致的文件跳过。
"""
import hashlib
import io
import json
import csv
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from e4_status import parse_dimacs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/external/e4prime"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
RAW = "https://raw.githubusercontent.com/{repo}/master/{path}"
UA = {"User-Agent": "cvh-research/1.0"}
ALLOWED_HOSTS = {"api.github.com", "raw.githubusercontent.com",
                 "archive.dimacs.rutgers.edu"}


def http(url, binary=False, retries=3):
    u = urllib.parse.urlparse(url)
    assert u.scheme == "https" and u.netloc in ALLOWED_HOSTS, f"blocked host: {u.netloc}"
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def tree(repo):
    d = json.loads(http(API.format(repo=repo)))
    return [(t["path"], t.get("size") or 0) for t in d.get("tree", []) if t.get("type") == "blob"]


def save(rel: Path, data: bytes, rows, source, family, name, note=""):
    rel = Path(rel)
    assert rel.resolve().is_relative_to(OUT.resolve()), f"path escapes OUT: {rel}"
    rel.parent.mkdir(parents=True, exist_ok=True)
    if rel.exists() and rel.stat().st_size == len(data):
        pass
    else:
        rel.write_bytes(data)
    # 计数走 e4_status.parse_dimacs（legacy 方言感知 + 声明自校验，不符即
    # raise）——旧版 parse_nv/parse_nc 只认 p 行，as/tm legacy 族曾产出
    # 垃圾计数（M2_LOG 2026-09-12 修复批记录，2026-09-16 修复）。
    n_vars, clauses, _declared = parse_dimacs(rel)
    rows.append({
        "source": source, "family": family, "file": str(rel.relative_to(OUT)),
        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        "n_vars": n_vars, "n_clauses": len(clauses), "note": note,
    })


def fetch_heule(rows):
    repo = "marijnheule/benchmarks"
    blobs = [(p, s) for p, s in tree(repo) if p.endswith(".cnf")]
    fams = {}
    for p, s in blobs:
        fam = p.split("/")[0]
        fams.setdefault(fam, []).append((p, s))
    for fam, items in sorted(fams.items()):
        items.sort(key=lambda x: x[1])
        take = items[:3] + items[len(items) // 2:len(items) // 2 + 2] + items[-3:]
        seen = set()
        for p, s in take:
            if p in seen:
                continue
            seen.add(p)
            try:
                data = http(RAW.format(repo=repo, path=p), binary=True)
            except RuntimeError as e:
                print(f"  skip {p}: {e}", flush=True)
                continue
            status = "sat" if "-SAT" in p else ("unk" if "-UNK" in p else "?")
            save(OUT / "heule" / p, data, rows, "heule", fam, p, f"status_in_name={status}")
        print(f"heule/{fam}: {len(seen)} files", flush=True)


def fetch_bnn(rows):
    repo = "msakai/bnn-verification"
    blobs = tree(repo)
    inst = [(p, s) for p, s in blobs if (p.endswith(".wcnf.gz") or p.endswith(".cnf.gz")
                                        or p.endswith(".wcnf.bz2") or p.endswith(".cnf.bz2"))]
    inst.sort(key=lambda x: x[1])
    # 跨尺寸取 40 个：小 10 + 中 10 + 大 10 + 最大 10
    k = max(1, len(inst) // 4)
    pick = inst[:10] + inst[k:k + 10] + inst[2 * k:2 * k + 10] + inst[-10:]
    for p, s in pick:
        fam = "bnn-" + p.split("/")[0]
        try:
            data = http(RAW.format(repo=repo, path=p), binary=True)
        except RuntimeError as e:
            print(f"  skip {p}: {e}", flush=True)
            continue
        if p.endswith(".gz"):
            raw = subprocess.run(["gzip", "-dc"], input=data, capture_output=True).stdout
        else:
            raw = subprocess.run(["xz", "-dc"], input=data, capture_output=True).stdout \
                if False else subprocess.run(["bzip2", "-dc"], input=data, capture_output=True).stdout
        # WCNF -> CNF：保留硬子句（weight>=top），去权重；纯 CNF 原样
        head, hards = [], []
        top = None
        for line in raw.decode("utf-8", "replace").splitlines():
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                head.append(line)
                parts = line.split()
                if "wcnf" in parts:
                    top = int(parts[-1])
                continue
            if top is None:
                hards.append(line)
            else:
                toks = line.split()
                w = int(toks[0])
                if w >= top:
                    hards.append(" ".join(toks[1:]))
        if top is not None:
            nvars = head[0].split()[2]
            ncls = len(hards)
            head = [f"p cnf {nvars} {ncls}"]
            raw = ("\n".join(head + hards) + "\n").encode()
        name = p.rsplit("/", 1)[-1].rsplit(".", 2)[0] + ".cnf"
        save(OUT / "bnn" / fam / name, raw, rows, "msakai-bnn", fam, name, f"orig={p}")


def fetch_dimacs(rows):
    base = "https://archive.dimacs.rutgers.edu/pub/sat-files/benchmarks/"
    import re
    listing = http(base)
    names = re.findall(r'href="([^"?][^"]*\.cnf\.Z)"', listing)
    for nm in names:
        fam = nm.split("-")[0]
        try:
            data = http(base + nm, binary=True)
        except RuntimeError as e:
            print(f"  skip {nm}: {e}", flush=True)
            continue
        raw = subprocess.run(["uncompress", "-c"], input=data, capture_output=True).stdout
        save(OUT / "dimacs" / fam / nm[:-2], raw, rows, "dimacs", fam, nm[:-2])


def main():
    rows = []
    t0 = time.time()
    for step in (fetch_heule, fetch_bnn, fetch_dimacs):
        try:
            step(rows)
        except Exception as e:  # noqa: BLE001
            print(f"[{step.__name__}] FAILED: {e}", file=sys.stderr, flush=True)
    assert (OUT / "MANIFEST_prime.csv").resolve().is_relative_to(OUT.resolve())
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    (OUT / "MANIFEST_prime.csv").write_text(buf.getvalue())
    print(f"done: {len(rows)} instances in {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
