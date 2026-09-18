# M2 运行日志

## E1+E2（2026-09-09 完成，840/840，零错误行）

### E1 树宽阶梯（k∈{3,5,8,12,16,20} × n∈{300,600} × 双臂 × 20 seeds）

- **planted 对照臂：全零平台**（所有 k、两个 n，中位冲突 = 0）。R1 的"种植易解性"
  偶然观察升级为受控结论：**种植易解性与树宽无关**。
- **unplanted 主臂：全 k 平坦在 ~8-12 次冲突**（logc 0.90-1.08，删失率 0-5%）。
  α=4.0 下即使 tw=20，滑袋 k-树公式也被传播级联秒杀。
- **解读**：与 Atserias-Dalmau 宽度定理一致——tw=20 只保证 exp(20) 上界（不预言
  实际难度），而滑袋构造的局部传播结构使反驳天然局部化。**核心结论：树宽单独
  不制造难度；难度活在局部性×密度的交互里（→ E3a 的地盘）。**
- 遗留选项（M3 视时间）：按 k 匹配阈值的 E1 扩展臂（每 k 找 α_c(k) 再比较），
  可分离"纯树宽效应"与"密度效应"——优先级低于 E3a。

### E2 随机 3-SAT 参照曲线（α 12 点 × 30 seeds，n=400）

教科书级 easy-hard-easy：中位 logc 1.13(α=3.0) → 4.49(4.1) → 5.87(4.26, 47%删失)
→ 6.0 地板(4.4-4.8, 97-100%删失) → 5.97(5.2, 47%) → 5.60(5.6, 0%)。
用途：(1) r=1.5 锚点比对基准；(2) 随机族自己的阈值区刻画。

### 工程记录

- E1 的 planted 臂若在 α=4.0 跑就注定全零——启动前已预见并加入 unplanted 主臂
  （R1 教训的直接应用）。
- 本批次曾因 SimpleQueue.get(timeout=) 参数错误产生 645+124 行错误行，修复后
  全部重算覆盖（INSERT OR REPLACE 幂等性首次实战验证）。

## S0（α_c 精测）——✅ 已完成（832/832；下文为进行时快照，订正于 2026-09-11）

525/720 真实完成。剩余 ~195 个 r≥0.3 近阈值硬格子（300s 墙钟护栏 + 10⁷ 冲突预算），
E1E2 释放的 4 worker 已归还，预计 40-50 分钟收尾。完成后：提取 α_c(r)（附每 r
resolution 率置信标记，AMEND-2 协议）→ 点火 E3a 主扫描。

## E6——内存危机中暂停（后恢复重跑；终局：命中砍线砍除，见 HYPOTHESES 冻结后记录与 results/e6.json）

ollama qwen3:8b（~5GB）与 20 个求解 worker（~6.4GB）在 9.7GB 机器上不可同时驻留。
计划：E3a 主扫描完成后，评估内存余量再决定 E6 重跑时机（或改用 3B 模型——
探索性实验的质量权衡另议）。

## 文献笔记进度

JMS✅（含勘误）｜Bläsius✅（SODA 2022 修正，定理级映射）｜OGP+相变✅（6800 字，
κ-stability/shattering/感知机反例辨析）｜HCS✅｜PS-model✅（Fig.3 最近前驱）｜
**Zulkoski✅**（CP 2018 无 OA 版，以作者博士论文全文核验；E5 baseline 完整规格 +
Ch5 mergeability 干预=我们 E3b 的同领域方法先例 + Table 4.3 弱相关数字）｜
**width/decay✅**（AD 消解宽度-JCSS、B-W 宽度-规模-JACM、AFT-JAIR、BKSS-IJCAI、
Weitz-FOCS 五条 DOI 核验；宽度屏障 √(n log n) 定量表 + "tw≤k ⇒ CDCL 多项式"链
作为 E1 平坦结果的定理级解释）｜**Mull-Fremont-Seshia✅**（arXiv:1602.08620 全文；
PCM 定理=社区度量不可能成易解性证书；CA 模型平均案例指数硬度；**Fig 1 社区规模
主导运行时间=H2 最重要的观察性先例**，我们用 r 干预把它升级为因果主张）。

全部 8 篇笔记在 docs/papers/notes/，M0 引用表同步更新（Zulkoski 行修正 LION→CP 2018）。
教训记录：文献抓取通道本轮多次被后端限流中断——改为直接下载（PDF/ar5iv HTML 后
本地精读）效率反而更高、引用核验更严格（每条 DOI 过 API）。

# M2 主结果总记录（2026-09-10 凌晨，E3a/E3b 完成）

**E3a/E3b 于 19:03 全部完成**（2100 作业 0 错误行；1980 行入库，120 个 E3b 原始臂
同键幂等合并）。已判定 1436 / 删失 544（27.5%，集中 r≥0.3）。分析结果
（results/e3a_analysis.json + figures/fig_e3a_dose.png）：

## H2 确认（主检验）
- RM-ANOVA（Δ 聚合、完全种子子集 n=28）：F(8,216)=2808.5，p≈1.1e-213
- JT 趋势（置换 10⁴）：p=1e-4（分辨率下限），BH-FDR 后 q=1e-4（7 个主检验全族）
- 剂量-响应（Δ=+0.2，CaDiCaL）：r 0.06→0.22 平均 logc 1.45→4.86（**3.4 个
  数量级**，已判定口径。【2026-09-11 勘误：原记"×4.5"混用删失下界口径】）
  ；Δ=+0.8 同格局 1.30→5.77【2026-09-18 订正注：端点终值 1.29（1.2949
  舍入），以论文 §9 与 results/e3a_analysis.json 为准】；r≥0.8 饱和于预算带
- partial η²=0.986–0.988（预注册线 0.14；cadical 子集口径——论文全可算
  臂口径为 0.984–0.988）；端点比 10^4.5（预注册线 10）
- Glucose 交叉验证同格局；JT-bound（删失计上限）p=1e-4 排除删失伪象

## E3b 手术刀（度保持交换）
- Δ=+0.2：1.79→2.99（×16，Wilcoxon p=7.0e-10，n=33 配对）
- Δ=+0.6：3.25→5.08（×68，p=6.0e-13，n=49）
- 53 对状态翻转（局部性摧毁 ⇒ 越过 sat/unsat 边界）
- 与 E1 合并的不对称结论：难度响应**局部几何**，不响应全局拓扑（树宽）概括

## 中介成立（Imai 2011，自助 95% CI，总效应 3.26）
- modularity ACME 3.06 [2.84,3.37]（~94%）
- spectral gap ACME 3.92 [3.68,4.28]（直接效应 -0.66，抑制模式 ⇒ 次级通道）
- mean degree 2.34 [2.15,2.60]；clustering 2.19 [2.02,2.44]
- 全 CI 不含 0 ⇒ 按预注册规则中介成立（机制证据）

## H1 特征阶梯（E5）
- 基线（Zulkoski 规格）主扫描数据：density 阶梯 CV R²=0.664 →
  +structure **0.976**（受控族上结构特征有增量，与随机族 0.90 零增益对照）
- GBDT 留一 r 外推：✅ 已完成（leave_r_out_cv_r2=0.76，results/e5_gbdt.json）【状态订正 2026-09-11】

## 后续队列
- s0_spotcheck（32 作业 10⁸/480s）与 e4_status（59 实例 10⁷）已完成入库
- Tobit 全量拟合收敛不良（loglik=nan）——如实报告，删失敏感性由双口径 JT+KM 承担
- E6 评估：✅ 已决——重跑后命中砍线砍除（qwen3:8b≈JW、无 r 梯度信号）【状态订正 2026-09-11】
- 报告 §6-12 与论文 v0.2 已同步主结果

---

## S0 完成——α_c(r) 最终表（2026-09-09 17:45）

S0 全 720 格判定完毕（0 错误行）；网格下探补 112 行（见下）。判定分布：
sat 190 / unsat 216 / walltimeout 314 / budget 0。

**α_c(r)（AMEND-2 兼容口径，只计已判定格）**：

| r | 0.06 | 0.08 | 0.11 | 0.15 | 0.22 | 0.3 | 0.5 | 0.8 | 1.5 |
|---|---|---|---|---|---|---|---|---|---|
| α_c | 2.60 | 3.35 | 3.82 | 4.20 | 4.23 | 4.40* | 4.70* | 4.60* | 4.60* |

（* = 测量饱和格，取 R3 粗测值，低置信；clean 交叉格 0.06–0.22 零删失）
【2026-09-11 口径注】本表为 S0 阶段历史测量记录：2.60 是当时 [2.5,2.8] 下探的
干净交叉值；2026-09-10 起最终论文口径为 α_c(0.06)=<2.5（夹逼），以论文 Table 1†
与 README 为准。下文"单调理象"等的 2.60 同此口径。
**单调理象**：α_c 从 2.60 升到 ~4.3（+1.6 密度单位），随后进入测量饱和——
r≥0.3 的近阈值实例在 10⁷ 预算 / 300s 内几乎全部无法判定（walltimeout 314 行
集中于此）。饱和本身即"局部性改变难度结构"的证据：小 r 的阈值区域可测量、
大 r 的阈值区域难度塌缩到测量范围之外。

**两处点火前修正**：
1. r=0.06 网格触及下限：S0 发现 α∈[2.9,3.1] 全 UNSAT 侧（SAT 率 ~0.2），
   真实阈值 <2.9 → s0_ext_low.py 下探至 [2.5,2.8]，α_c(0.06)=2.60（干净交叉）。
2. **修复 AMEND-2 违规**：m2_e3a_main.alpha_c_from_s0 原把 walltimeout 计入
   UNSAT 桶（在删失 92–100% 的大 r 处会系统性压低 α_c）→ 改为只计
   sat/unsat；交叉点两侧 resolution<60% 标低置信；测量饱和 r 回退 R3 粗测值
   并入 spot-check 队列（低置信集 {0.3, 0.5, 0.8, 1.5}）。

**E3a 已点火**（17:52）：2100 作业（E3a 1620 + E3b 480），10⁶ 预算 + 300s
护栏，16 worker，断点续跑生效。AMEND-2(3b) spot-check（32 作业 × 10⁸ 预算 ×
480s，s0_spotcheck.py 已就绪）排在 E3a 之后以 4 worker 执行（内存护栏）。
审计：PRESPEC_AUDIT.md（含 AMEND-3 内容臂暂缓决定）。
【2026-09-16 对账注】点火公告按计划口径计 2100 = E3a 1620 + E3b 480（E3b
按原始臂+交换臂两臂计）；最终入库 1980 行 = E3a 主臂 1620 + E3b 交换臂
240（2Δ×4r×30，原始臂与主扫描共享同行集、不重复入库）+ Δ=+0.6 主臂 120
（4 组合×30，cadical-only，点火后补入批次）。

## 可靠性体检与持久化修复（2026-09-09，作者驱动）

作者指出"S0 跑完了不止一次"+"能落盘的不要留内存"。排查结论：

1. **S0 反复跑的根因（设计缺陷）**：m2_s0_alpha_c.py 每次运行都重新提交
   全部 720 作业，无断点续跑过滤——重启后已完成的 525 格也被整轮重算
   （INSERT OR REPLACE 只保证不崩，不保证不浪费）。叠加此前的多次
   bug 修复重启，造成"反复跑完"观感与 1–2 小时算力浪费。
2. **提交攒批风险**：run_batch 每 25 行才 commit，中途 kill 最多丢 24 行
   在途计算（最坏 24×300s）。
3. **修复（commit a26fefd）**：
   - run_batch 增加 resume=True：按 UNIQUE(family,params,seed,solver) 跳过
     已有最终判定（sat/unsat/budget/walltimeout）的作业，error/childerror
     才重算——对全部实验脚本全局生效，此后任何重启只补缺口；
   - 逐行 commit，kill 最多丢 1 行；
   - 注明 conflict_budget 不在唯一键内，换预算必须换 stage 标签
     （S0=m2_s0、主扫描=m2_main，已遵守）。
4. **数据资产入库**：results/*.db 此前被 .gitignore 排除（全部实验数据
   只存于工作目录单文件）→ 修正：4 个结果库（共 ~1.9MB）全部入库，
   每次提交即版本备份；一个被误追踪的 SQLite journal 瞬态文件退出追踪；
   α_c 提取 JSON、E5 基线 JSON、图表全部落盘入库。
5. **体检其余项**：磁盘 9%（873G 空闲）；内存 6.0G 可用（ollama 仅剩空闲
   守护进程，模型已卸载）；无孤儿进程；无其他被追踪瞬态文件；
   requirements.txt 缺失（复现指南引用它）→ 已按 .venv 实测版本补齐。
6. **E4-prime 抓取完成**：59 真实实例落盘 data/external/e4prime/ +
   MANIFEST_prime.csv（sha256/n_vars/n_clauses 清单），待 CPU 空闲后跑
   e4_status.py 状态判定。

## E4 实例源——全面换源决策（2026-09-09）

本网络（WSL2 主机）可达性实测：SATLIB 老站 UBC 404、satlib.org 域名被抢注
（跳 manybackgrounds.com）、web.archive.org/archive.org 全线超时、starexec.org 与
starexec.rnd.muni.cz DNS 不存在、zenodo.org/huggingface.co 连接失败、
gbd.iti.kit.edu DNS 不存在。GitHub（api/codeload/raw/pages）、cs.cmu.edu、
fmv.jku.at、archive.dimacs.rutgers.edu 可达。

处置：
1. **SAT 2024 主轨预选表已完成**——data/external/2024-main/downloads/ 内 meta.csv
   （400 实例 md5/文件名/族/作者）+ detailed_main.csv（15 求解器逐实例运行时+状态）。
   实例字节缺失，但"n∈[10³,10⁵]、基线 1–60s、状态已知"的确定性预选随时可做；
   作者浏览器渠道（Windows 侧代理可能可达 starexec/Wayback）留作补全通道。
2. **E4-prime 换源**（experiments/fetch_e4_prime.py，幂等可续跑）：
   - 源 A marijnheule/benchmarks（GitHub raw 可达）：组合/crafted 真实实例 10 族
     （Green Hat/Steiner/26x26/matrix/mphf/packing/ptn/radio/wap/asias），每族 ≤8、
     尺寸跨度优先，文件名含 SAT/UNK 状态；
   - 源 B msakai/bnn-verification：MSE 2020 BNN 验证真实编码（WCNF→去软子句转
     CNF，附 .sol ⇒ 状态已知），跨尺寸取 40；
   - 源 C archive.dimacs.rutgers.edu/pub/sat-files/benchmarks：DIMACS 经典 as/tm（.Z）。
   产出 data/external/e4prime/ + MANIFEST_prime.csv（sha256/n_vars/n_clauses）。
3. E4 协议不变：只用于落位主张、不进 E5 训练集（选择偏差防火墙）；状态由我方
   基线求解（CaDiCaL 300s）独立确定，预算内未决者按删失处理不进落位图。
4. 局限声明（报告必写）：E4-prime 实例谱偏组合/crafted+BNN，工业多样性不及
   SAT 2024 主轨全集；落位结论的外推边界据此收紧。

## 2026-09-12 修复批（独立审查发现；全程零行为变更的除外项见各条）

1. **E4 DIMACS 解析事故（高危，已修复重跑）**：e4_status.py 旧 parse_dimacs 把
   1996 legacy 方言（as/tm 族：'.N/.M' 声明、'N' 前缀否定、无 0 终止符、as 族
   0-based 含字面 "0"、tm 族 1-based）的 N 前缀文字行当注释跳过，17 个经典实例
   被静默截成 1–21 条子句，DB 误报 "17 个全部 SAT、微秒级"。修复：解析器加
   legacy 分支 + 声明自校验（子句数/字面统计不符即 raise）；17 实例全部重判：
   **15 SAT + 2 UNSAT**（as9-no UNSAT 与 -no 命名一致；as1-yes UNSAT 与 legacy
   标签矛盾，3 求解器稳健），毫秒级全判定。E4 总判定数不变（22/59：sat 17、
   unsat 5、walltimeout 37），论文 §Results V / REPORT_zh §9 / paper_draft_en
   已按真实结果改写。MANIFEST_prime.csv（未入库）的垃圾计数源自
   fetch_e4_prime.py 同源解析。【2026-09-16 处置】fetch_e4_prime.py 计数
   改用 e4_status.parse_dimacs（legacy 分支 + 声明自校验），manifest 已
   重生成，59 行 n_vars/n_clauses 与 m2_e4.db 修正值逐行一致。
2. **度分布口径订正（中危，重测固化）**：初版 Threats 度形态数字
   （mean 1.5α 4.2→7.35、SD 2.23→2.73 ≈22%、max 16→22 ≈37%、CV 0.5→0.37）
   系 2026-09-11 未入库补测且误用"正向文字半口径"——冻结前提口径为全文字
   出现次数（pilot 12=3×4 自证）。以 committed experiments/degree_profile.py
   重测（270/270 inst_id 与 DB 精确一致）：**mean 3α 8.4→14.7、SD 3.76→3.85
   （≈3%，<5% 判据内）、max 24→31（≈29%，超限；全局最大口径）**、
   CV 0.45→0.26；产物 results/degree_profile.json。论文 Threats
   "Literal-degree profile" 段与 PRESPEC_AUDIT §三已按订正口径改写：
   超限项由"SD/max"改为"max（SD 在限内）"，因果归属不变（E3b 交换链保持
   literal occurrence counts 精确不变）。
3. **e5_baseline.json 补 random 族块**：committed 脚本对 m2_e1e2.db 重跑
   （0.9028→0.8975，零结构增益）合并入库；m2_main.db 块逐字段保真
   （含 nested_F_test_H1 块——注意该块无 committed 生产脚本，期刊批补）。
4. **引用勘误**：blasius2022 会议版 SODA 2022→**SODA 2021**（SIAM 官方
   proceedings pp.42-53；DBLP 键尾号 22 系消歧计数器非年份）；marques2009
   改章节 DOI 10.3233/faia200987 并补年份 2021。
5. 措辞订正：spot-check 表述（r≥0.5 为"+0.2 侧全判定 UNSAT、−0.2 侧全超时，
   ±0.2 无法夹逼"，非"±0.2 全部无法判定"）；r=0.06 SAT 率"恒为 ~0.31"改为
   "自 ~0.31 递减至 ~0.13"；η² 区间 0.986–0.988→0.984–0.988；KM 中位
   22,368→20,695（lifelines 口径）；Δ-pooling 集合披露；图 1/2 补 \ref；
   paper_draft_en 清理 [RESULT-TBD]×4 与 queued×2；e3a_analysis.py 删死代码
   行（geo_swap 恒空过滤；e3a 重生成字节一致证明零行为变更）。
6. **打包元数据**：rebuild_zenodo.py tar 写入改 uid/gid=0、uname/gname 空
   （此前 82 成员 tar 头未匿名化、携带构建机侧身份字串，文本扫描结构性盲区）。

## 2026-09-12 修复批二（独立审查发现）

1. **nested_F_test_H1 溯源缺口修复（高危→已清偿）**：论文 H1 嵌套 F 检验
   （原记 F(72,643)=133.8）系早期手算、无 committed 生产脚本且多子集重算
   不可复现。experiments/e5_baseline.py 新增 nested_f()（size+density vs
   +structure 嵌套 OLS、全交互设计、行集按 full 特征 NaN 对齐），对全部
   已判定 geo_random 行（n=1350）重算：**F(60,1283)=297.8, p≈0**——与另一
   独立实现逐位一致（双实现收敛）。随机族对照 F(60,166)=0.9（p=0.63）零
   增益与阶梯结论一致。论文/审计/草稿三处数字更新为 committed 值。
2. **README/AI_DISCLOSURE DOI 措辞软化**（既定策略：publish 前软化、上传
   后硬化）："已发布于 Zenodo"→"已预留、发布后生效"（预留 DOI 在
   DataCite 注册前 doi.org 404 属预期）。
3. **事实性声明订正**：main.tex/paper_draft_en 的 "preselection table
   retained in-repo" 改 "retained in the authors' working archive"（400 表
   不在 git/快照内）；REPORT_zh §11.6 过时状态格勘误（嵌套 F 已完成）；
   R3b 先导统计（F=1284/ACME 2.14/83%）加"早期口径、无 committed 脚本"
   历史注（PRESPEC_AUDIT:46 同步）。
4. 引用/措辞小项：atserias2011 补中间名 J.~K.~Fichte；satcomp 系列
   2002–2024→2002–2026；附录 clone 占位符指向 Zenodo record；附录完成
   日期补 E4 重判注；REPORT_zh §0 "~1.8"→"≥1.7"、E2 峰位表述改
   "达峰后进入删失平台"；paper_draft_en ≈1.6→>1.7、314→313。
5. rebuild_zenodo.py 注释去除构建机身份字面量（修复批一自己引入的泄漏，
   自脚本豁免使文本闸门失效——B1 字面口径下 1 命中）；审查清单 B3
   加"大写精确匹配=凭证式扫描"口径注。
