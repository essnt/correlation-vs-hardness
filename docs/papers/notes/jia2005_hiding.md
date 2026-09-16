# 精读笔记：Generating Hard Satisfiable Formulas by Hiding Solutions Deceptively（Jia–Moore–Strain, q-hidden 诱骗构造）

> 本目录笔记仅为本项目（correlation-vs-hardness）内部使用。
> **原文获取记录**：已成功获取全文，无虚构。论文有两个版本：AAAI-05 会议版（arXiv:cs/0503044，6 页 7 图）与 **JAIR 期刊扩展版**（12 页）。arXiv PDF 直连在本环境被 SSL 重置（重试 3 次失败），改从 **JAIR 官网下载期刊版全文 PDF**（`/tmp/jms.pdf`，pdfminer 提取为 `/tmp/jms.txt`，32 KB，逐字核对），AAAI 版元数据经 arXiv API 确认。**本笔记以内容更全的 JAIR 版为准**（两版构造定义一致）。
> 与既有笔记（giraldez-cru-2017、li-2021）格式一致；因本文与 M1 pilot 的 R2 负结果直接相关，第 5 节为本次精读的重点产出。

## 1. 书目信息

| 项目 | 内容 |
|---|---|
| 论文全名 | Generating Hard Satisfiable Formulas by Hiding Solutions Deceptively |
| 作者 | Haixia Jia、Cristopher Moore、Doug Strain（均为 University of New Mexico, Computer Science Department；moore 兼 Santa Fe Institute） |
| 会议版 | Proc. AAAI-05（20th National Conference on Artificial Intelligence, Pittsburgh），pp. 384–389, 2005 |
| 期刊版（本笔记依据） | Journal of Artificial Intelligence Research (JAIR), Vol. 28 (2007), pp. 107–118；Submitted 9/05, published 2/07 |
| 预印本 | arXiv:cs/0503044 [cs.AI]，2005-03-18（对应 AAAI 版；arXiv API 确认题名/作者一致） |
| 谱系 | 上承 naive 1-hidden 种植（Asahiro et al. 1996; Van Gelder 1993 mkcnf.c）、2-hidden 双种植（Achlioptas, Jia & Moore, AAAI-04, pp. 131–136）、Achlioptas & Peres (STOC 2003) 的解重加权思想；下启后续 planted-hardness 一系工作。JAIR 页面显示被引 85+（2026-09 检索） |
| 资助 | H.J.：NSF Graduate Fellowship；C.M./D.S.：NSF CCR-0220070, EIA-0218563, PHY-0200909（JAIR 版致谢节） |
| 术语约定（原文） | 1-hidden = naive 种植；2-hidden = AJM 双种植；0-hidden = 无种植的普通随机 3-SAT；q-hidden = 本文构造 |

## 2. 核心研究问题

为 WalkSAT、Survey Propagation（SP）这类**不完全**算法提供"难但保证可满足"的基准。难点在于：随机 3-SAT 在 r = m/n ≈ 4.27 以上几乎必然 UNSAT，无法"生成后过滤"；而现有可满足生成器各有缺陷（拟群完成问题非 3-SAT 原生；naive 种植有吸引偏置）。具体地：

- **1-hidden 的病根（§1）**：从 A 满足的 7 类子句中均匀采样，会导致文字分布失衡——"on average a literal will agree with its value in the hidden assignment **4/7** of the time"（原文逐字，§1）。子句越多，多数投票或局部搜索越快找到 A。
- **2-hidden（AJM 2004）只解决了一半（§1）**：同时隐藏 A 与其补 ᾱ，DPLL 上看起来与 0-hidden 一样难，但 WalkSAT 在**多项式**时间内可解——部分变量与某个隐藏赋值一致后，邻居变量的相关性会把整片"拉"出来（引 Barthel et al. 2002, PRL 88:188701）。
- **本文问题**：只隐藏**一个**赋值 A，但对子句极性分布做 q^t 重加权（受 Achlioptas & Peres 2003 在阈值证明中的重加权技巧启发），能否在**完全算法（DPLL）、消息传递（SP）、局部搜索（WalkSAT）三类算法上同时制造指数难度**，且难度可通过 q 连续调节、甚至让公式"指离" A？

## 3. q-hidden 构造的精确定义（逐字级；本笔记最重要一节）

### 3.1 原文构造（JAIR 版 §1, p.108，逐字）

> "**1.** Predefine a constant q < 1 and generate a random truth assignment A ∈ {0,1}^n
> **2.** Do rn times: choose a random k-tuple of variables, and choose from among the clauses in which t > 0 literals are satisfied by A with probability proportional to q^t."

即：固定密度 r = m/n、参数 q < 1；随机生成隐藏赋值 A；重复 m 次——每次随机取 k 个变量（k=3 为正文默认），在**所有被 A 满足的极性模式**中，以**正比于 q^t** 的概率选取子句，其中 t = 该子句中与 A 一致（被 A 满足）的文字数，t ≥ 1（保证 A 可满足该子句）。

归一化的显式形式（JAIR 版 §2, p.109，逐字）：

> "By symmetry, we can take A to be the all-true assignment. In that case, a clause with t > 0 positive literals is chosen with probability **q^t/((1+q)^k − 1)** (here we normalize the probabilities by summing over the C(k,t) clauses for all t > 0)."

所以精确的极性选择规则是：**t 个 A-一致文字的子句被选中的概率 = C(k,t)·q^t / ((1+q)^k − 1)，t = 1..k**（7 种 A-满足模式上按 q^t 加权，分母是 (1+q)^k − 1 = Σ_{t≥1} C(k,t)q^t）。三个交叉验证：(a) §3 UC 微分方程初始条件 s_{3,j} = C(3,j)·q^j/((1+q)^3 − 1)（0<j≤3，s_{3,0}=0），必须对 j 求和为 s_3 = r；(b) 原文明确"the naive formulas discussed above amount to the case **q = 1**"——q=1 必须退化为 uniform-7，即分母 = 7 = 2^3 − 1；(c) 我们用 Python 复算 max_{α≤1/2} f(α) = 1 的交点：q=0.5 得 r ≈ 5.56，与原文"rc(0.5) ≤ 5.6"吻合（若用 (1+q)^{k−1} 作分母只得 ≈4.9）。（注：arXiv AAAI 版的文本层把 (1+q)^k − 1 折行渲染成 (1+q)k−1 易误读；JAIR 版版面清晰无歧义。）

### 3.2 关键澄清：原文**没有** decoy 赋值 β，也**没有** flip 概率 p

任务框架与本仓库 M1 pilot 描述中的"decoy 赋值 β、flip 概率 p"**均不出自本文**。原文自始至终只有**单一**隐藏赋值 A；其"诱骗"（deceptive）是**统计/边际**意义上的：变量出现极性整体偏向"与 A 相反"，**不存在任何一个被逐子句证伪的第二赋值**。与 β 概念最接近的原文对象是 AJM 2004 的 2-hidden——那里 β 恰为 A 的补（相当于 p_flip = 1 的极端），且 2-hidden 的子句是"被 A 与 ᾱ 同时满足"（均匀采样），而非"被 β 证伪"。**我们 pilot 的 σ/β 双赋值构造属于自创变体**（详见第 5 节），不忠实于本文定义。

### 3.3 q 参数的含义与取值

- **含义**：对"更被 A 满足"的子句（t 大）的惩罚指数。"This penalizes the clauses which are 'more satisfied' by A"（§1）。q 控制**边际吸引度**：单个文字与 A 一致的概率 = Σ_t (t/k)·C(k,t)q^t/((1+q)^k − 1) = q(1+q)^{k−1}/((1+q)^k − 1)，从 q=1 的 4/7 ≈ 0.571 单调降到 q→0 的 1/k（t=1 子句为主）。
- **平衡点 q\*（§2, Eq. (1)，逐字）**："if q is the positive root q\* of **1 − (1−q)(1+q)^{k−1} = 0** then f′(1/2) = 0. We call the resulting q\*-hidden formulas **balanced**; for k = 3, q\* is the **golden ratio (√5−1)/2 = 0.618...**"。在 q\* 处每个文字与 A 一致/不一致概率各 1/2。
- **deceptive 区（§2）**：q < q\*（如 q=0.5, 0.4, 0.3, 0.2）时 f′(1/2) < 0，f(α) 的局部最大值移到 α < 1/2，公式整体"指离"A——"we can even cause the formula to 'deceptively' point away from A"（摘要）。**q 越小越 deceptive，实验上越难（q=0.2 最难）**。
- **取值汇总**：q=1 → 1-hidden（最易）；q=q\*≈0.618 → balanced（对三类算法都像 0-hidden）；q<q\* → deceptive（难度峰随 q 减小移向更高密度）；q→0 → 每个 A-满足子句恰有 1 个 A-一致文字。

### 3.4 α 的含义与取值（注意与本项目记号冲突！）

原文 α ∈ [0,1] 是**解与 A 的一致率**："let X_α be the number of satisfying truth assignments ... that agree on a fraction α of the variables with the hidden assignment A; that is, their Hamming distance from A is **(1−α)n**"（§2）。分析聚焦 α ≤ 1/2（"左半超立方"）：q ≥ q\* 时 f 在 α=1/2 取最大；q < q\* 时最大值在 α < 1/2，那里存在"alternate solutions"，在密度 rc(q) 以上指数消失。**原文的密度记号是 r = m/n**——而我们项目用 α 表密度、r 表环面球的半径。**代码/笔记互译时务必换算：论文 (r, α) ↔ 项目 (α, 一致率)**，R2 记录里的"α∈{4.3..7.5}"是密度。

### 3.5 解密度函数与 WalkSAT 漂移（deception 的操作化定义）

- **解密度（§2）**：E[X_α] ∼ f(α)^n，其中 f(α) = [1/(α^α(1−α)^{1−α})]·(1 − [(q(1−α)+α)^k − α^k]/((1+q)^k − 1))^r（推导假设"the selection of the literals in each clause **with replacement**"，即变量有放回——分析近似；pilot 的 `rng.sample` 无放回 + 度封顶与此有微小差异，论文实验未明说）。设 max{f(α) | α ≤ 1/2} = 1 得 rc(q) 的解析上界；"For instance ... **rc(0.5) ≤ 5.6**"（§2, Fig. 1 右图在 r=5.6 处对所有 α ≤ 1/2 有 f(α) < 1）。
- **WalkSAT 漂移（§2）**：随机赋值 B 下各子句等概率违反，翻转随机文字带来的 Hamming 距离期望变化 E[Δd(A,B)] = Σ_t C(k,t)q^t(2t/k − 1)/((1+q)^k − 1) = **[1 − (1−q)(1+q)^{k−1}]/((1+q)^k − 1)**。Eq. (1) 成立时为零——WalkSAT 对 A 的方向**零信息**（论证只适用前 o(n^{1/2}) 步）；q < q\* 时为正——**WalkSAT 的贪心梯度被诱骗着远离 A**。这就是"deceptive"一词的精确含义。

### 3.6 与 2-hidden 的机制对比

2-hidden 用"隐藏补赋值"对消吸引（WalkSAT 可借相关性逐片恢复，多项式可解）；q-hidden 用"重加权"对消吸引，不引入可被相关性利用的对称第二解。§4.2 的 SP 实验直接证实后者骗得更狠（见 4.3 节）。

## 4. 主要结果（哪些参数组合产生难度、对谁难、难度数字）

难度由 **(q, r)** 二元组控制（无 p 参数）。测试对象是 **2002–2004 年代求解器**：DPLL/CDCL 前身 **zChaff**（Zhang 2002；OKsolver 行为类似）、**SP**（Mézard–Zecchina 2002）、**WalkSAT**（每步以等概率 random/greedy 翻转，即噪声 0.5；每公式至多 10^4 次重启 × 每次 10^4 步）。**没有任何现代 CDCL（CaDiCaL/Kissat 等 2015+ 求解器当时不存在）**。

- **理论/UC（§3）**：UC（纯单元传播 + 随机决策）在 balanced q\*-hidden 上与 0-hidden 完全同行为——"UC succeeds ... with constant probability if and only if **r < 8/3**, just as for 0-hidden formulas"（正/负文字期望全程相等，对称性使然）。q < q\* 时 UC 能在**略高**密度成功（抓到 alternate 解）。由此猜想简单 DPLL 在与 0-hidden 相同的密度处开始指数时间。
- **DPLL/zChaff（§4.1, Fig. 2；49 trials 中位数）**：n=200、r∈[4.0, 8.0] 扫描（纵轴中位决策数 10^1–10^5）：balanced q\*-hidden "about as hard as 0-hidden ones, **including above the satisfiability threshold r ≈ 4.27**"（即把难度延伸进保证可满足区）；naive 1-hidden **远更易**。deceptive（q<q\*）呈两阶段：低密度较易 → 难度峰在 rc(q) → 其上指数时间（系数随 r 增大而减小）；**固定 r > rc(q) 时 q 越小越难**。r=5.5、n∈[50,300] 扫描（纵轴至 10^6）：0-hidden、2-hidden、q\*-hidden 同档，1-hidden 容易得多，**q=0.3 的 deceptive 更难一点**。
- **SP（§4.2, n=10^4）**：0-hidden 成功到 r=4.25；**q\*-hidden 同样在 4.25 失败**（尽管保证可满足）；1-hidden 易到 r=5.6；2-hidden 到 r ≈ 4.8。结论逐字："the reweighting approach of q-hidden formulas does a **better job of confusing SP** than hiding two complementary assignments does"。q < q\* 时 SP 成功密度恰好**逼近 zChaff 峰值密度 rc(q)**（SP 被梯度推向 alternate 解，rc(q) 以上子句消息反向）。
- **WalkSAT（§4.3, Fig. 3；49 trials 中位数）**：n=200、r∈[4,8]：**三个最 deceptive 的 q（0.2, 0.3, 0.4）都存在一个密度，中位翻转数跳到 10^8（截断）**；"q-hidden formulas with q = 0.4 appear to be **unfeasible for WalkSAT for, say, r > 5**"。r=5.5、n∈[50,600]：1-hidden 与 2-hidden **多项式**；**q\*-hidden 已是指数**，且"the slope of this exponential increases dramatically as we decrease q"。这与摘要的论断一致：q-hidden 对 DPLL 与 WalkSAT **同时**指数难——这正是相对 2-hidden（DPLL 难/WalkSAT 易）的核心卖点。
- **阈值汇总（§5, Fig. 4）**：zChaff 峰值密度、WalkSAT 跳变/10^8 截断密度、SP 失效密度三条经验 rc(q) 曲线**相当吻合**，解析上界 max{f(α)|α≤1/2}=1 位于其上方；横轴 q∈[0.2, 0.6+]，纵轴 rc(q) 从 q=0.2 处的 ~11–12 单调降到 q→q\* 处的 ~4.3–5（图轴读数）。猜想：单一阈值 = alternate solutions（α<1/2）消失的密度。
- **难度速查表（依 §4–5）**：1-hidden：三类算法全易。2-hidden：DPLL 难（≈0-hidden）、SP 到 4.8、WalkSAT 多项式易。q\*-hidden：DPLL/SP/WalkSAT 全部 ≈ 0-hidden（含 r>4.27 的可满足区；WalkSAT 指数）。q<q\*（如 0.2–0.5）：r 低于 rc(q) 各算法找到 alternate 解（较易）；r ≈ rc(q) 全体最难；r > rc(q) 指数且 q 越小越难（WalkSAT 直接 10^8 不可行）。

## 5. 与本项目映射（M1 pilot 的 JMS 臂：实现保真度审查）

### 5.1 我们实际实现的构造（`src/cvh/generators.py::planted_hidden`）

σ（种植解）+ **decoy β**：β 逐变量独立以 `p_flip` 概率翻转 σ；`q_hidden` 比例的子句取"decoy 极性"——在 σ≠β 的 diff 位置强制 σ-true（自动 β-false），在 σ=β 的 agreement 位置强制 β-false（即 σ-false）——整条子句被 σ 满足且被 β 证伪（无 diff 位置时回退 uniform-7）；其余 1−q_hidden 子句取 uniform-7 σ-满足极性。R2 记录（`docs/PILOT_FINDINGS.md`）：q_hidden=1、p_flip∈{2/3, 0.8}、α（=密度）∈{4.3..7.5}，**对 CaDiCaL（2026 年版）全部 0 冲突**；R1 的 uniform-7 种植（α=4.3）亦 121/121 零冲突。

### 5.2 与原始定义的一致性判定：**不一致**（四点差异，一点恰好重合）

1. **机制不同**：原文无 β、无 p_flip、无子句级混合参数（§3.2）；pilot 的 decoy 子句（被特定 β 逐条证伪、极性由 (σ,β) 唯一确定）在原文分布族中不存在。pilot 构造在精神上更接近 **AJM 2-hidden 的部分翻转推广**，而非 q^t 重加权。
2. **"q" 语义冲突（最危险的一条）**：pilot 的 `q_hidden` 是**混合比例**（q_hidden=1 = 全部子句为 decoy 子句 = pilot 以为的最难端）；论文的 q 是**极性重加权指数**（**q=1 = naive 1-hidden = 全族最易端**，难度在 q ≤ 0.618）。两个 "q" 在参数轴上指向相反方向——凡引用 R2 结果写"q=1"处必须注明是 pilot 语义。
3. **难度区间从未被采样**：论文的全部难度结果位于 paper-q ∈ [0.2, 0.618] × r ∈ [4.3, 12]；pilot 采到的只有 paper-q=1 的同族变体（`_sat_polarity` 基数均匀抽样，非严格 uniform-7，见本节条 5）与自创 decoy 变体。**R2 负结果不构成对论文结论的反驳或复现**。
4. **边际吸引方向相反**：按论文自己的吸引度量（文字与隐藏解一致的概率），pilot 的 decoy 子句每位置以 ≈p_flip 概率为 σ-true，即 2/3 或 0.8 > 4/7 ≈ 0.571（1-hidden 水平）> 1/2——**比 naive 种植更吸引 σ**，与论文 deceptive 区（一致率 < 1/2）方向相反。pilot 实例里唯一的"反吸引"装置是全局 β-证伪结构，而对 CaDiCaL 无效。
5. **相近的一点**：pilot 的 `_sat_polarity`（基数均匀抽样：先均匀抽基数 1..3、再均匀抽该基数的满足位置子集，实测冗余 2.14–2.23）**属论文 q=1 情形的同族变体**——两者支撑集相同（7 种 A-满足模式），但分布不同（q=1 严格对应 uniform-7 等概率；【2026-09-11 订正】旧文"uniform-7、期望冗余 12/7 正是 q=1 情形"有误）；R1 的"种植公式 CDCL 平凡"结论因此与原文 q=1 端定性一致。

### 5.3 他们报告的难度对现代 CDCL 是否还存在？

- **论文实测的求解器与年代**：zChaff（2002）、OKsolver（2002）——VSIDS/学习型 DPLL 的第一代；SP（2002）；WalkSAT（1996）。规模：DPLL n≤300（Fig. 2 右）、WalkSAT n≤600（Fig. 3 右）、SP n=10^4。难度量级：zChaff 中位决策数在 r=5.5、n=300 处约 10^5–10^6（图轴），WalkSAT 在 rc(q) 以上 10^8 flips 截断。**这是 2005 年的水平**。
- **我们未测 canonical q-hidden**：pilot 的 0 冲突结果只覆盖"q=1 同族（基数均匀抽样）+ decoy 混合变体"。因此准确的表述是：**"naive 1-hidden 与我们的 σ/β decoy 混合变体对 2026 年 CaDiCaL 平凡；论文的 canonical q-hidden（q≤0.618, r≈rc(q)≈5–8）在 modern CDCL 上未被任何一方测量"**。间接证据（更强结构化的 decoy 变体仍零冲突；R1 表明吸引型种植对 CDCL 全域平凡；q-hidden 的难度机制明确针对 majority splitting/SP 消息/WalkSAT 梯度这三类 2005 年启发式）都指向"现代 CDCL 大概率也能轻易攻破"，但这是**先验判断而非测量**——写报告时不得升格为结论。
- **若未来要复活 SAT 难度臂**，正确实现只需约十行：对每条子句先按 C(3,t)q^t/((1+q)^3−1) 采 t∈{1,2,3}，再在 3 个位置中均匀选 t 个放 σ-正文字、其余放 σ-负文字（A≡σ；无需 β、无 p_flip、无混合），扫描 q∈{0.2,0.3,0.4,0.5,0.618} × r∈[4.3, 8]；这同时是检验"2005 难度是否幸存于 CDCL"的最小实验。

### 5.4 对"planted 臂降级为稳健性观察"决策的意义

1. **降级决策维持且更稳健**：冻结版 HYPOTHESES v1.0（主载体 = geo_random UNSAT 臂）不受影响；本笔记反而加固了它——三类种植型构造（1-hidden、σ/β 变体）在现代 CDCL 下全零冲突，且文献难度机制与 CDCL 的搜索方式（冲突学习 vs 多数投票）不同源。
2. **必须修正结果表述（action item）**：PILOT_FINDINGS.md R2 与任何外宣文本中的"JMS 诱骗隐藏全部 0 冲突"应改写为"**JMS 风格 σ/β decoy 混合变体**（非原文 canonical q-hidden）全部 0 冲突；原文难度区间 q≤0.618 未测"。同理，planted 稳健性观察的准确措辞是"1-hidden 与 decoy 变体易解"，而非"q-hidden 易解"。
3. **文献引用姿势**：引用本文时应引用其正面结论（q-hidden 对 2005 年三类算法同时指数难、rc(q) 三算法吻合），并把它定位为"planted-hardness 谱系的经典基准 + 2005 年代难度"——用于说明**为什么**需要 decoy/防泄漏设计，而不是作为"对现代 CDCL 有效"的依据。
4. **记号警告入项目规范**：论文 r = 密度、α = 一致率；项目 α = 密度、r = 球半径。任何把论文参数直接填进 `planted_hidden` 的后续实验都会因 q 语义冲突 + 记号冲突而静默跑错（R2 即是此类事故的实例——虽被 pilot 及时捕获为负结果）。

## 6. 可引用结论清单（标注原文 section；均基于 JAIR 28(2007) 版页码/章节）

1. （§1, p.108）q-hidden 两步构造定义逐字版；"naive formulas ... amount to the case q=1"——q=1 即 1-hidden，构成各家族公共对照点。
2. （§1, p.108）1-hidden 的病灶：平均每个文字以 4/7 概率与隐藏赋值一致 → 多数启发式/局部搜索速胜。
3. （§1, p.108）2-hidden（AJM 2004）对 DPLL 与 0-hidden 同难，但 WalkSAT 多项式可解（引 Barthel et al. 2002）——"只骗过完全搜索"是不够的。
4. （§2, p.109）极性分布显式定义：t 个 A-一致文字的子句概率 = C(k,t)q^t/((1+q)^k − 1)；分析假设变量有放回。
5. （§2, p.110, Eq.(1)）balanced q\*：1 − (1−q)(1+q)^{k−1} = 0 的正根；k=3 时 q\* = golden ratio ≈ 0.618；q\* 处文字与 A 一致/相异各半。
6. （§2, p.110）WalkSAT 漂移公式 E[Δd] = [1 − (1−q)(1+q)^{k−1}]/((1+q)^k − 1)：q<q\* 时局部搜索被贪心梯度诱离 A（deceptive 的操作化定义；仅前 o(n^{1/2}) 步成立）。
7. （§2, p.110）解密度 f(α) 显式式 + 上界方法（max{f(α)|α≤1/2}=1）；数值锚点 rc(0.5) ≤ 5.6（Fig. 1）。
8. （§2 末, p.111）猜想：对每个 q ≤ q\* 存在阈值 rc(q)，其上 w.h.p. 只剩靠近 A 的解；三类算法的最难点都在 rc(q) 附近。
9. （§3, p.111–112）UC 微分方程 + 初始条件 s_{3,j} = C(3,j)q^j/((1+q)^3 − 1)；balanced 情形 UC 成功 ⟺ r < 8/3，与 0-hidden 相同；q<q\* 时 UC 借 alternate 解在略高密度成功。
10. （§4.1, p.112–113）zChaff（OKsolver 类似），n=200、r∈[4,8]、49 trials：balanced ≈ 0-hidden（含 r>4.27 可满足区）；1-hidden 远易；deceptive 峰在 rc(q)、其上指数且 q 越小越难；r=5.5 处 0/2/q\*-hidden 同档、q=0.3 更难。
11. （§4.2, p.113–114）SP（n=10^4）：0-hidden 失败于 4.25；q\*-hidden 同；1-hidden 到 5.6；2-hidden 到 ≈4.8；q<q\* 时 SP 失效密度与 zChaff 峰值 rc(q) 吻合——重加权比双隐藏更"骗"SP。
12. （§4.3, p.114–115）WalkSAT（噪声 0.5，≤10^4 重启 × 10^4 步，49 trials）：q∈{0.2,0.3,0.4} 在 rc(q) 以上中位翻转数达 10^8 截断（q=0.4 在 r≳5 不可行）；r=5.5 时 1/2-hidden 多项式 vs q\*-hidden 指数，斜率随 q 减小陡增。
13. （§5, p.115, Fig. 4）zChaff 峰值 / WalkSAT 跳变 / SP 失效三条 rc(q) 经验曲线相互吻合（q∈[0.2,0.6]，rc(q) 约 11–12 → 4.3–5），解析上界在其上方；猜想单阈值 = alternate 解消失密度。
14. （§6, p.116）三条公开问题：证实单阈值 rc(q)；证明简单 DPLL 在 r > rc(q) 指数；计算解数方差以收紧上下界——均可作为我们 related-work 的"未决"引用点。
