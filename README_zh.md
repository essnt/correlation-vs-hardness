> English version: [README.md](README.md)

# Correlation vs. Hardness —— 因果相关结构与计算难度的干预式实证研究

**核心问题**：在密度、规模、度分布、子句内容全部受控的前提下，仅仅改变变量交互的
"局部性半径 r"（相关性衰减程度），是否足以造成 SAT 求解难度的量级变化？

这一设计源自一个流传已久的猜想——现实世界的因果结构是局部的：不存在任意远的强相关，
这可能是世界可计算的前提之一。本项目把这个猜想变成一个可证伪的受控实验：把"局部性"
做成一个可拧的旋钮（r），检验它是否因果地决定 SAT 求解难度。

## 假设（M1 末预注册于 docs/HYPOTHESES.md）

- **H1**（限 CDCL 家族）：控制密度与规模后，结构指标组合对求解时间的解释方差显著优于单一密度指标。
- **H2**（核心）：n、α、literal 度分布、子句内容分布、σ-满足冗余度全受控下，仅 r 变化
  仍产生显著因果效应（2×2 析因 + 配对设计）。
- **H3**（探索性）：LLM 分支排序质量随局部性增强而提升。（**已砍除**：E6 命中
  预注册砍线，负结果记录于 docs/HYPOTHESES.md 与 docs/REPORT_zh.md §10）

## 主结果（M2 完成，2026-09-10）

- **阈值曲线**：α_c(r) 在 r=0.06 处自上而下夹逼于 <2.5（SAT 率在探测网格内
  自 ~0.31 递减至 ~0.13，0.5 交叉不可达），r=0.08→0.22 升至 3.35→4.23，r≥0.3 进入测量
  饱和（近阈值实例在 10⁷ 冲突/300s 内不可判定，pilot 粗测 ~4.4–4.7）——
  局部性移动 sat/unsat 分界线本身。
- **H2 确认**：匹配阈值偏移 Δ 后，已判定实例难度跨 3.4 个数量级
  （1.45→4.86；计删失下界则 ≥4.5）；F(8,216)=2808.5（p≈1e-213），
  JT p≤1e-4（FDR 后 q≤1e-4），partial η²≈0.99。
- **E3b 手术刀**：度保持交换摧毁局部性 ⇒ 难度 ×16–68（p≤7e-10），
  53 对实例 sat/unsat 翻转。
- **中介成立**：modularity ACME 3.06 [2.84,3.37]（占总效应 ~94%）等四通道
  CI 全不含 0。
- **H1 阶梯**：主扫描上结构特征 CV R² 0.66→0.976（随机族对照零增益）；
  GBDT 留一 r 外推 0.76。
- 详见 docs/REPORT_zh.md（中文深度报告）、docs/paper_draft_en.md（英文论文
  v0.2）、docs/PRESPEC_AUDIT.md（预注册审计）、docs/M2_LOG.md（全程记录）。

## 目录结构

```
docs/          预注册、审计、文献笔记、报告
src/cvh/       核心库（生成器 / 指标 / 求解器封装 / 统计分析）
experiments/   实验脚本（E1–E6）
data/          实例与基准（内容寻址，git 忽略大文件）
results/       结果数据库（SQLite）与图表
```

## 里程碑

- **M0** 文献核查与新颖性定位（Go/No-Go 判定）
- **M1** 基础设施 + pilot 校准 + 预注册
- **M2** 核心实验（E1–E4）
- **M3** 预测器（E5）、可选 E6、分析与写作
- **M4** 收尾与投稿包

## 诚实边界

不攻击 P vs NP 本身；不承诺新定理与发表；负结果同样完整报告。

## 复现（Reproduce）

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q           # probSAT 二进制缺失时相关测试自动跳过
cd tools/probsat && make && cd ../..           # 可选：按 tools/probsat/README.md 构建 probSAT
.venv/bin/python experiments/e3a_analysis.py   # 从 results/*.db 确定性再生分析 JSON 与图
bash scripts/status.sh                         # 完成度对账
```

所有图表均由 committed 脚本从 results/*.db 再生；逐实验方法论与完整记录见
docs/REPORT_zh.md（§13 复现指南）。结果数据库随仓库分发：重跑实验脚本会
断点续跑，已判定作业自动跳过（`status.sh` 可对账进度）；整个仓库（代码＋
全部结果数据库＋git 历史）约 7 MB。

平台说明：以上路径在 Linux / macOS / Windows（Python 3.11–3.14）均可运行，
依赖均有三平台预编译轮子，CDCL 求解器随 python-sat 轮子内置；`status.sh`
为 bash 脚本，Windows 请在 WSL/Git Bash 中执行或跳过（仅进度对账）；
probSAT 二进制为可选构建（需 C 编译器），缺失时相关测试自动跳过。

## 引用（Citation）

本仓库的存档版本（论文压缩版 + 完整快照）已在 Zenodo 发布：
**DOI 10.5281/zenodo.22777748**（https://zenodo.org/records/22777748）——
concept DOI，始终指向最新版本；首版（2026-09-15）的版本专属 DOI 为
10.5281/zenodo.22777749。

```bibtex
@misc{jin2026locality,
  author       = {Song Jin},
  title        = {Locality Causes Tractability? An Intervention Study on the
                  Variable-Interaction Radius in Geometric Random Satisfiability},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22777748},
  url          = {https://zenodo.org/records/22777748}
}
```
