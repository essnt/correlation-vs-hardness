#!/usr/bin/env python3
"""从当前 HEAD 重建 Zenodo 上传包（zenodo_upload.zip）。
结构: README_ZENODO.md + 论文 PDF + correlation-vs-hardness_snapshot.tar.gz
快照排除: EXCLUDE_DOCS 内部文档 10 个、docs/papers/*.pdf、
          zenodo_upload.zip 自身、egg-info、缓存。
"""
import io
import os
import shutil
import subprocess
import tarfile
import zipfile

CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/zenodo_out/zenodo_upload_current.zip"
PDF_NAME = "SongJin_2026_LocalityCausesTractability_CompactVersion.pdf"
EXCLUDE_DOCS = ["SESSION_HANDOFF.md", "POSITIONING.md", "VENUES_ROADMAP.md",
                "RELEASE_CHECKLIST.md", "ZENODO_STEPS.md", "COVER_LETTER.md",
                "VALUE_ASSESSMENT.md", "REVIEW_CHECKLIST.md", "LESSONS_LEARNED.md",
                "BLIND_REVIEW_PROTOCOL.md"]


def main():
    # 1) git archive HEAD → 干净暂存目录
    snap = "/tmp/zfinal"
    shutil.rmtree(snap, ignore_errors=True)
    os.makedirs(snap)
    arc = subprocess.run(["git", "archive", "HEAD"], cwd=CWD, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
        tf.extractall(snap)
    # 2) 排除
    for d in EXCLUDE_DOCS:
        p = os.path.join(snap, "docs", d)
        if os.path.exists(p):
            os.remove(p)
    pdir = os.path.join(snap, "docs", "papers")
    if os.path.isdir(pdir):
        for f in os.listdir(pdir):
            if f.endswith(".pdf"):
                os.remove(os.path.join(pdir, f))
    for junk in ["zenodo_upload.zip", "src/cvh.egg-info"]:
        p = os.path.join(snap, junk)
        shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else (
            os.remove(p) if os.path.exists(p) else None)
    for root, dirs, files in os.walk(snap):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
    # 3) 打快照 tar.gz（输出在暂存目录之外）
    os.makedirs("/tmp/zenodo_out", exist_ok=True)
    targ = "/tmp/zenodo_out/snapshot.tar.gz"
    if os.path.exists(targ):
        os.remove(targ)
    with tarfile.open(targ, "w:gz") as tfo:
        for root, dirs, files in os.walk(snap):
            for f in files:
                full = os.path.join(root, f)
                # 归档元数据匿名化：不携带构建机的 uid/gid/用户名（tar 头即元数据，
                # 文本级隐私扫描覆盖不到；2026-09-12 盲审发现构建用户名经此通道
                # 进入归档头，遂改为写入前清零）
                ti = tfo.gettarinfo(full, arcname="./" + os.path.relpath(full, snap))
                ti.uid = 0
                ti.gid = 0
                ti.uname = ""
                ti.gname = ""
                with open(full, "rb") as fsrc:
                    tfo.addfile(ti, fsrc)
    # 4) 外层 zip
    pdf = open(os.path.join(CWD, "arxiv/main.pdf"), "rb").read()
    readme = open(os.path.join(CWD, "arxiv/ZENODO_README.md"), "rb").read()
    out = OUT
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zz:
        zz.write(os.path.join(CWD, "arxiv/ZENODO_README.md"), "README_ZENODO.md")
        zz.writestr(PDF_NAME, pdf)
        zz.write(targ, "correlation-vs-hardness_snapshot.tar.gz")
    shutil.copy(out, os.path.join(CWD, "zenodo_upload.zip"))
    print("zenodo_upload.zip 重建:", os.path.getsize(out), "字节")


if __name__ == "__main__":
    main()
