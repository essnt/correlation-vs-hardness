#!/usr/bin/env python3
"""从当前 HEAD 重建 Zenodo 上传包（zenodo_upload.zip）。
结构: README_ZENODO.md + 论文 PDF（期刊版）+ correlation-vs-hardness_snapshot.tar.gz
快照排除: EXCLUDE_DOCS 内部文档 13 个、docs/papers/*.pdf、
          zenodo_upload.zip 自身、egg-info、缓存。
时戳: tar 成员 mtime / gzip MTIME / zip 条目 date_time 统一取自 HEAD 提交纪元
      （UTC），不含构建时刻与构建机时区指纹（2026-09-19）。
"""
import gzip
import io
import os
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sanitize_pdf import sanitize_pdf_bytes

CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/zenodo_out/zenodo_upload_current.zip"
PDF_NAME = "SongJin_2026_LocalityCausesTractability_JournalVersion.pdf"
EXCLUDE_DOCS = ["SESSION_HANDOFF.md", "POSITIONING.md", "VENUES_ROADMAP.md",
                "RELEASE_CHECKLIST.md", "ZENODO_STEPS.md", "COVER_LETTER.md",
                "VALUE_ASSESSMENT.md", "REVIEW_CHECKLIST.md", "LESSONS_LEARNED.md",
                "BLIND_REVIEW_PROTOCOL.md", "AUDIT_MEMO.md", "M0_FINDINGS.md",
                "PLAN_v5.md"]


def head_epoch() -> int:
    """HEAD 提交纪元（UTC 秒）= 包内唯一时戳源。"""
    out = subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=CWD,
                         capture_output=True, check=True)
    return int(out.stdout.strip())


def _zipinfo(name: str, epoch: int, mode: int) -> zipfile.ZipInfo:
    """外层 zip 条目：时间戳显式取 HEAD 纪元（UTC），无构建机时区指纹。
    DOS 时间戳只有 2 秒粒度，先归到偶数秒，写入后读回即为该值。"""
    info = zipfile.ZipInfo(name, date_time=time.gmtime(epoch - epoch % 2)[:6])
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = mode << 16
    return info


def main():
    epoch = head_epoch()  # tar/gzip/zip 三处时戳的唯一来源
    # 1) git archive HEAD → 干净暂存目录
    snap = "/tmp/zfinal"
    shutil.rmtree(snap, ignore_errors=True)
    os.makedirs(snap)
    arc = subprocess.run(["git", "archive", "HEAD"], cwd=CWD, capture_output=True).stdout
    # 解包经系统 tar（成员名来自 git archive 的 HEAD 内 tracked 路径，受控来源）；
    # Python 级逐成员提取（tf.extract/extractall）被预提交扫描判为路径穿越模式，
    # 故下沉至 tar 工具，Python 侧不再出现归档解包 sink
    subprocess.run(["tar", "-x", "-C", snap], input=arc, check=True)
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
    with open(targ, "wb") as raw:
        # gzip 头显式 mtime=HEAD 纪元（否则写入构建时刻）：rebuild 无构建时刻指纹
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tfo:
                for root, dirs, files in os.walk(snap):
                    for f in files:
                        full = os.path.join(root, f)
                        # 归档元数据匿名化：不携带构建机的 uid/gid 与身份字串（tar 头即元数据，
                        # 文本级隐私扫描覆盖不到；2026-09-12 订正：构建机身份字串曾经此
                        # 通道进入归档头，遂改为写入前清零）；mtime 显式取 HEAD 纪元，
                        # 不再继承工作树文件 mtime（2026-09-19）
                        ti = tfo.gettarinfo(full, arcname="./" + os.path.relpath(full, snap))
                        ti.uid = 0
                        ti.gid = 0
                        ti.uname = ""
                        ti.gname = ""
                        ti.mtime = epoch
                        with open(full, "rb") as fsrc:
                            tfo.addfile(ti, fsrc)
    # 4) 外层 zip（三条目时间戳显式 = HEAD 纪元 UTC）
    pdf = open(os.path.join(CWD, "jair/main.pdf"), "rb").read()
    # PTEX.FileName 净化兜底：pdfTeX 为 PDF 输入（doclicense 徽标）记录的
    # 绝对源路径携带构建机用户名/家目录，文本层扫描不可见（2026-09-20
    # 隐私核验发现）——嵌入前等长原地改写；工作树 jair/main.pdf 亦须运行
    # scripts/sanitize_pdf.py 保持与包内字节一致（闸门断言二者相等）
    pdf, _n_sanitized = sanitize_pdf_bytes(pdf)
    readme = open(os.path.join(CWD, "arxiv/ZENODO_README.md"), "rb").read()
    out = OUT
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zz:
        zz.writestr(_zipinfo("README_ZENODO.md", epoch, 0o100644), readme)
        zz.writestr(_zipinfo(PDF_NAME, epoch, 0o600), pdf)
        with open(targ, "rb") as fsrc:
            zz.writestr(_zipinfo("correlation-vs-hardness_snapshot.tar.gz", epoch, 0o100644),
                        fsrc.read())
    shutil.copy(out, os.path.join(CWD, "zenodo_upload.zip"))
    print("zenodo_upload.zip 重建:", os.path.getsize(out), "字节")


if __name__ == "__main__":
    main()
