#!/usr/bin/env python3
r"""jair/main.pdf 构建后净化：剥离 pdfTeX 为 PDF 输入记录的绝对源路径。

pdfTeX 对被 \include 嵌入的 PDF（doclicense CC-BY 徽标，jair.cls 官方模板
固有）在 Form XObject 字典写入 /PTEX.FileName (<绝对路径>)——构建机的用户
名与家目录因此进入 PDF 对象字典，文本层扫描（get_text()）不可见，闸门曾
因此漏检（2026-09-20 盲验证 V6 发现）。
本脚本对全部 /PTEX.FileName 字符串做等长原地改写（绝对路径 → "./" + 文件
名 + 空格补位）：字节偏移零位移，xref 与渲染不受影响；重复运行幂等。
用法: .venv/bin/python3 scripts/sanitize_pdf.py jair/main.pdf
重编译 jair/main.tex 后、rebuild_zenodo.py 打包前必须运行本脚本
（rebuild_zenodo.py 嵌入时亦自动调用本净化作兜底；final_verify 对包内
两份 PDF 做原始字节扫描把关）。
"""
import re
import sys
from pathlib import Path

_PTEX = re.compile(rb"/PTEX\.FileName \(([^()]*)\)")


def sanitize_pdf_bytes(data: bytes) -> tuple[bytes, int]:
    """等长改写全部绝对路径 PTEX.FileName；返回 (新字节, 改写处数)。"""
    changed = 0

    def _sub(m):
        nonlocal changed
        path = m.group(1)
        if not path.startswith(b"/"):
            return m.group(0)
        changed += 1
        repl = b"./" + path.rsplit(b"/", 1)[-1]
        pad = b" " * (len(path) - len(repl))
        return b"/PTEX.FileName (" + repl + pad + b")"

    return _PTEX.sub(_sub, data), changed


def main():
    target = Path(sys.argv[1])
    data = target.read_bytes()
    new, n = sanitize_pdf_bytes(data)
    if n == 0:
        print(f"{target}: 无绝对路径 PTEX.FileName（已净化或非 pdfTeX 产物），未改动")
        return
    target.write_bytes(new)
    print(f"{target}: 改写 {n} 处 PTEX.FileName（等长原地，字节偏移不变）")


if __name__ == "__main__":
    main()
