# 精读笔记：The Impact of Heterogeneity and Geometry on the Proof Complexity of Random Satisfiability

> **原文获取说明**：本机网络对 arxiv.org / export.arxiv.org 的 TLS 连接被重置、Wiley 全文页被 Cloudflare 拦截，任务指定的 curl + pdfminer 通道不可用（重试 3 次以上）。全文改经 web_reader 服务端通道获取，得两份相互校对的完整文本：arXiv v2 PDF（2021-11-23，53 页，对应 RSA 期刊版排版）与 ar5iv HTML（基于 v1，LaTeX 数学完整）。**本笔记基于全文精读，非元数据级信息**。定理陈述以 arXiv v2 / RSA 期刊版编号为准（v1 的重述编号一并注出）；PDF 文本抽取会丢失希腊字母（Δ、β、ε、Φ 等），凡经 ar5iv 数学版核对还原处均已标注，无法完全确定之处以脚注显式标明，不含任何虚构。

## 1. 书目信息

| 项目 | 内容 |
|---|---|
| 论文全名 | The Impact of Heterogeneity and Geometry on the Proof Complexity of Random Satisfiability |
| 作者 | Thomas Bläsius（Karlsruhe Institute of Technology）；Tobias Friedrich、Andreas Göbel、Ralf Rothenberger（Hasso Plattner Institute, University of Potsdam）；Jordi Levy（IIIA-CSIC, Bellaterra/Barcelona） |
| arXiv | arXiv:2004.07319（v1 2020-04-15；v2 2021-11-23，53 页） |
| 会议版 | SODA 2021（SIAM 官方 proceedings 元数据：Proceedings of the 2021 ACM-SIAM Symposium on Discrete Algorithms, pp. 42-53, 2021-01；doi:10.1137/1.9781611976465.4）。【2026-09-12 订正】旧记"SODA 2022"系误读 DBLP 键 conf/soda/Blasius00LR22 的尾号 22 为年份——该尾号是消歧计数器，与年份无关 |
| 期刊版 | Random Structures & Algorithms, Vol. 63(4), pp. 885–941, 2023 年 12 月（在线 2023-06-28），doi:10.1002/rsa.21168，混合开放获取 |
| 资助 | DFG 项目 "Scale-Free Satisfiability"（416061626） |
| 系谱 | 上承 Ansótegui–Bonet–Levy 的 scale-free SAT（IJCAI 2009）幂律模型与 Giráldez-Cru–Levy（IJCAI 2017，本目录已有笔记 `giraldez-cru-2017-locality.md`）的温度式局部性模型——原文模型一节明言其连接权重"coincides with the temperature model used by Giráldez-Cru and Levy [40]"；证明工具承 Ben-Sasson–Wigderson（宽度–规模翻译）与 Ben-Sasson–Galesi（expander → clause space / tree-like size） |

## 2. 核心研究问题（写给非理论背景读者）

工业 SAT 实例比经典随机实例好解许多个数量级，主流解释归结为两个结构特征：**异质性**（变量出现次数服从幂律，少数"热门"变量）与**局部性**（变量–子句连接在某种"距离"下抱团）。本文问：这两个特征**各自**对证明复杂度——resolution 宽度/规模，CDCL 类求解器绕不开的最坏情形下界度量——的因果贡献是什么？答案干脆：**只加异质性、不加几何，不可满足的实例仍是超多项式难（Theorem 5.8）；加上几何局部性，实例里 a.a.s. 藏着一个常数大小的不可满足子核，且多项式时间 O(n log n) 就能找到（Theorem 7.12）**。摘要原话："heterogeneity alone does not make SAT easy … In contrast, modeling locality with underlying geometry leads to small unsatisfiable subformulas, which can be found within polynomial time." 这是第一批把"局部性 ⇒ 易解"做成可证定理的工作之一。

## 3. 模型定义（Section 3；最重要，逐字级精确）

### 3.0 基座：non-uniform 模型（带权非均匀随机 k-SAT）

n 个变量、m 个子句，变量赋权 w_1..w_n。独立采样 m 个子句；每个子句**按权重成比例、无放回**抽 k 个变量；然后每个变量独立以 1/2 概率取负。原文："Each clause is sampled by drawing k variables without repetition with probabilities proportional to their weights. Then each of the k variables is negated independently at random with probability 1/2."

### 3.1 异质性旋钮：power-law 模型（Section 3.1）

幂律指数 **β > 2**；离散幂律权重：第 i 个变量 **w_i = i^{−1/(β−1)}**（由此变量出现次数服从尾指数 β 的幂律分布）。密度 **Δ = m/n**。背景结果（原文引其前作 [34]）：β > (2k−1)/(k−1) 时可满足性阈值位于 Δ ∈ Θ(1)；β < (2k−1)/(k−1) 时常数密度实例 a.a.s. 平凡不可满足。**此模型无几何、无距离、无局部性——是"纯异质性"对照臂。**

### 3.2 局部性旋钮：weighted geometric 模型（Section 3.2/3.3）

1. **地面空间**：d 维环面 T^d = R^d/Z^d = [0,1]^d（对边粘合），装备 p-范数（p ∈ N⁺ ∪ {∞}）；同维度两点之差取环面圆距离 |p_i − q_i|_∘ = min{|p_i − q_i|, 1 − |p_i − q_i|}。
2. **位置**：每个变量、每个子句各赋 T^d 上**均匀随机**位置。
3. **权重**：变量权重归一化使最小权重为 1；总权重 W = Σ_v w_v。
4. **连接权重**（核心定义）：子句 c（位置 s_c）与变量 v（位置 s_v、权重 w_v）之间
   **X(c,v) = (w_v / ‖s_c − s_v‖_p^d)^{1/T}**，
   即"加权距离"倒数再取 d/T 次幂；**加权距离 = ‖s_c − s_v‖_p / w_v^{1/d}**（权重 w_i 的位点影响域体积正比于 w_i）。
5. **抽样**：每子句按 X(c,v) 成比例、无放回抽 k 个变量；否定符号在 2^k 种组合中**均匀、尽量无重复**抽取——原文："we only get the same clause twice if we have more than 2^k clauses with the same variable set"（该细节是"常数大小 UNSAT 核 = 同一 k 变量集的 2^k 个全符号子句"论证的前提）。
6. **温度 T 的语义**：T → 0：子句取连接权重最高的 k 个变量（= 加权距离最小的 k 个，确定性阈值）；T → ∞：所有变量等可能，几何模型退化为 non-uniform 模型。**T 是局部性强度的连续旋钮，T 越小局部性越强。**
7. **分布函数**（证明用）：半径 x 的 d 维 p-范数球体积 F_dist(x) = vol(B_p(x)) = Π_{d,p}·x^d（0 ≤ x ≤ 0.5），Π_{d,p} = (2Γ(1/p+1))^d/Γ(d/p+1)（Π_{2,2} = π）；连接权重 CDF：F_X(x) = 1 − Π_{d,p}·w_v·x^{−T}（x ≥ (2^d·w_v)^{1/T}）。

### 3.3 有没有类似我们"半径 r"的连续旋钮？

**有连续旋钮，但参数化不同。** 他们的旋钮是**温度 T**：软阈值、幂律长尾——任何变量被抽中的概率都非零，随距离按 ‖c−v‖^{−d/T} 幂律衰减。我们的旋钮是**硬半径 r**：子句在以自身位置为中心的 r-球内**均匀**抽 k 个变量（紧支撑，r 外概率恒 0）。对应关系：T→0（确定性 k 近邻）⟺ r→0（球内期望变量数 ≈ k 的临界半径之下被迫取近邻）；T→∞（均匀随机）⟺ r 超过环面空间尺度。可用的标定桥是"期望可达变量数"（2D 欧氏 r-球内期望 n·πr²），但两者不是同一分布族，故其定理条件 T < 1 **不能**机械翻译成临界 r，只能序数对应（见 §6.2）。另注意：其几何模型允许异质权重进入 X，是"异质性 × 局部性"二维参数化；但 Theorem 7.12 只要求 W ∈ O(n)、单变量 w_v ∈ O(n^{1−ε})——**近均匀权重（含等权 W = n 的特例）也在覆盖范围内**，作者刻意把"起作用的是几何而非权重"做成定理而非猜想。

### 3.4 两个模型的生成流程

- power-law：定 β → 赋权 w_i = i^{−1/(β−1)} → 重复 m 次：按权无放回抽 k 变量、独立 1/2 定符号 → 输出。
- geometric：定 (d, p, T, {w_v}) → 变量/子句各赋均匀随机位置 → 每子句按 X(c,v) ∝ 无放回抽 k 变量 → 2^k 符号组合均匀无重复（可能时）→ 输出。

## 4. 主要定理与证明思路

（编号以 arXiv v2 / RSA 版为准；v1 把 §2 的主定理重述为 Theorem 2.1/2.2。以下陈述的希腊字母均按 ar5iv 数学版还原。）

### 4.1 工具箱（Section 5 开头 + Appendix A）

- 双部图 G(Φ)＝变量–子句关联图。**(w, 0)-bipartite expanding**：任一 ≤ w 子句的集合 S 含 ≥ |S| 个不同变量；**(r, c)-bipartite expander**：任一 ≤ r 子句的 S 含 ≥ c|S| 个不同变量；**unique variable**：在 S 中恰出现一次的变量。
- Ben-Sasson–Wigderson 框架（Theorem 5.3，引 [11]）：若存在 w ∈ Ω(n) 使 (1) 每个 ≤ w 子句集合含 ≥ |S| 个不同变量，且 (2) 每个 w/3 ≤ |S| ≤ 2w/3 的集合含 ≥ ε|S| 个 unique variables，则 resolution 宽度 = Ω(w)。配合 [11] 的翻译：k-CNF 的 resolution 证明规模 ≥ exp(Ω((w−k)²/n))，tree-like 规模 ≥ 2^{w−k}。
- Ben-Sasson–Galesi（Theorem 5.10，引 [14]）：G(Φ) 为 (r, c)-expander（c > 0 常数）时，任何 resolution 证明的 clause space ≥ Ω(cr/(2+c))，tree-like 规模 ≥ exp(Ω(cr/(2+c)))。
- 装箱：Raab–Steger（引 [52]）及其非均匀加权版（Theorem A.5/A.6）：m ∈ Ω(n/polylog n) 个球入 n 桶，a.a.s. 最大负载 Ω(log n / log log n)。

### 4.2 方向一（异质性、无几何 ⇒ 难）：Theorem 5.8（v1 编号 Theorem 2.1；Section 2.1 重述、Section 5 证明）

> **Theorem 5.8.** Let Φ be an unsatisfiable random power-law k-SAT formula with n variables, m ∈ Ω(n) clauses, k ≥ 3, and power-law exponent β > (2k−1)/(k−1). Let Δ = m/n be large enough so that Φ is unsatisfiable at least with constant probability. Let ε, ε₁, …, ε₃ be constants with ε > 0, ε₁ = (k−ε)/2 − 1 > 0, ε₂ = (k−ε)·(β−2)/(β−1) − 1 > 0, and 0 < ε₃ < (k/2 − 1)·(β−2)/(β−1) − 1. For the resolution width w of Φ, a.a.s.
> **(i)** If β ∈ ((2k−1)/(k−1), 3) and Δ ∈ o(n^{ε₂}), then w ∈ Ω(n^{ε₂/ε₁}·Δ^{−1/ε₁}).
> **(ii)** If β = 3 and Δ ∈ o(n^{ε₁}/log^{1+ε₁} n), then w ∈ Ω(n·Δ^{−1/ε₁}/log^{1+1/ε₁} n).
> **(iii)** If β > 3 and Δ ∈ o(n^{ε₁}), then w ∈ Ω(n·Δ^{−1/ε₁}).
> **(iv)** If β > (2k−2)/(k−2) and Δ ∈ o(n^{ε₃}/log^{ε₃} n), then w ∈ Ω(n·Δ^{−1/ε₃}).

[^注1]: (i) 的指数 n^{ε₂/ε₁}·Δ^{−1/ε₁}：PDF 文本抽取吞掉 Δ 后正文形如 "n^{ε2/ε1} 1/ε1"；本文按三重证据校订：(a) β=3 时 ε₂ = (k−ε)/2 − 1 = ε₁，故 (i) 的公式在 β→3⁻ 恰好连续过渡到 (ii) 的 n·Δ^{−1/ε₁}；(b) 各条假设（Δ ∈ o(n^{ε₂})、o(n^{ε₁}/log^{1+ε₁} n)…）恰好都是使宽度下界 → ∞ 的充要条件；(c) (iii)(iv) 均含 Δ^{−1/·} 因子。ε₂、ε₃ 定义式按 ar5iv 原样（含 "−1"）。另注：Theorem 5.8(iv) 的 ε₃ 上界两份文本一致为 (k/2 − 1)·(β−2)/(β−1) − 1，而其证明依赖的 Corollary 5.7 用略宽的 (k/2)·(β−2)/(β−1) − 1（该式 > 0 恰等价于 β > (2k−2)/(k−2)）；故 (iv) 仅在 (k/2−1)·(β−2)/(β−1) > 1 的参数区（较大 k）非平凡，k = 3,4 的线性宽度由 (ii)/(iii) 覆盖。

要点：
- 假设是"Φ **至少以常数概率**不可满足"而非 a.a.s. 不可满足——原文明确说该界"does not only hold above the satisfiability threshold, but also at the threshold"（Section 2.1），**在阈值处成立**。
- β < 3：宽度 n^{ε₂/ε₁} 多项式（β→3⁻ 时指数 →1）；β = 3：n/polylog；β > 3：线性 n·Δ^{−1/ε₁}；(iv) 对较大 k 在 β < 3 区也给线性宽度。Δ = Θ(1)（常数密度/阈值处）时各条均给出 n^{Ω(1)}～Ω(n) 宽度，经 Ben-Sasson–Wigderson 翻译即**超多项式乃至指数的 resolution 规模**（Section 2.1 开头："random power-law k-SAT formulas have superpolynomial resolution size when unsatisfiable"）。
- **证明思路**：异质性不破坏 expansion。Lemma 5.1：β ∈ ((2k−1)/(k−1), 3) 时 G(Φ) a.a.s. 直到 w = n^{Θ(1)} 是 (w,0)-expanding——核心计算是抽样分布的二阶矩 Σ_v p_v²：β < 3 时 = Θ(n^{−2(β−2)/(β−1)})，β = 3 时 = Θ((ln n)/n)，β > 3 时 = Θ(1/n)（Appendix A.1）。Lemma 5.2：直到某个 W = n^{Θ(1)}，每个 w/3–2w/3 规模子句集含常数比例 unique variables（按权抽样的"生日悖论"阈值由 Σp² 决定）。两者代入 Theorem 5.3 得宽度下界（Corollary 5.4）。另一路：Lemma 5.5 直接证 (r, c)-bipartite expansion——β > (2k−3)/(k−2)、ε ∈ (0, (k−1)·(β−2)/(β−1) − 1)、Δ ∈ o(n^ε/log^ε n) 时存在 r = Θ(n·Δ^{−1/ε}) 使 G(Φ) a.a.s. 是 (r, c)-expander，c = (k−1) − (1+ε)·(β−1)/(β−2) > 0；经 Corollary 5.6（(r, (k+ε)/2 − 1)-expander ⇒ 宽度 Ω(r)）与 Theorem 5.10 得 **Corollary 5.9：β > (2k−3)/(k−2)、0 < ε < (k−1)·(β−2)/(β−1) − 1、Δ ∈ o((n/log n)^ε) 时 tree-like resolution 规模 a.a.s. ≥ exp(Ω(n·Δ^{−1/ε}))**。中间结论 **Corollary 5.7：β > (2k−2)/(k−2)、0 < ε < (k/2)·(β−2)/(β−1) − 1、Δ ∈ o(n^ε/log^ε n) ⇒ w ∈ Ω(n·Δ^{−1/ε})**。

### 4.3 方向二（几何 ⇒ 易）：Theorem 7.12（v1 编号 Theorem 2.2；Section 2.2 重述、Section 7 证明）

> **Theorem 7.12.** Let Φ be a formula with n variables and m ∈ Θ(n) clauses drawn from the weighted geometric model with ground space T^d equipped with a p-norm, temperature **T < 1**, W ∈ O(n), and w_v ∈ O(n^{1−ε}) for every v ∈ V and any constant ε > 0. Then, Φ contains a.a.s. **an unsatisfiable subformula of constant size, which can be found in O(n log n) time**.

即：只要温度 T < 1（局部性足够强）、总权重近线性、无超级热门变量，常数密度的几何实例 **a.a.s. 含常数大小（2^k 个子句、k 个变量）的不可满足子公式，且 O(n log n)（字典序排序）即可找到**。对 CDCL 而言这近乎"易解"的代名词：冲突驱动搜索很快撞上该核。

**证明思路**（Section 4 → 6 → 7 递进）：
1. **T = 0 鸽笼核心论证**（Section 4）：等权 2D 时 T = 0 子句取 k 近邻，"子句属于哪个变量 k 元组"由 order-k Voronoi 图（按"k 近邻集合相同"剖分空间）决定；order-k Voronoi 图至多 2k(n−k) 个区域（原文引 Bohler 等的 abstract Voronoi 理论），故 m ≥ 2^k·2k(n−k) = O(n) 时鸽笼保证某个 k 变量集被 ≥ 2^k 个子句占据；符号组合无重复 ⇒ 这 2^k 个子句遍历全部符号组合 ⇒ 常数大小 UNSAT 子公式。
2. **Voronoi 复杂度**（Section 6）：**Theorem 6.9**：n 个加权位点（最小权 1、总权 W）随机落在常维环面（或超立方体 [0,1]^d）上时，order-k 加权 Voronoi 图的**期望**区域数 O(W)。**Theorem 6.2**：order-k 图有 ℓ 个顶点 ⇒ order-(k+d) 图有 Ω(ℓ) 个非空区域。**Corollary 6.3/6.4**（最坏情形警示）：3D 无权 order-4 / 2D 加权 order-3 的区域数最坏可达 Ω(n²)——"随机位置"假设不可去。
3. **一般 T < 1 与低密度**（Section 7）：**nice clause** 定义——子句 c 是 nice 的，若第 i 个被抽中的变量恰是 c 的连接权重第 i 高的变量（i ∈ [k]，即包含 k 个最近变量且按降序抽出）。**Theorem 7.2**：T < 1 且 w_v/W ∈ o(1) 时每个子句以 Ω(1) 概率 nice；**Corollary 7.3**：nice 子句期望 Θ(m)。技术核心是控制远距离连接质量：定义 **δ_v = w_v^{1/(1+T)}·n^{T/(1+T)}·log^{2/(1+T)} n**（使距离 ≤ δ_v 内的期望连接权重和 ≤ 1 的标尺），**Lemma 7.4**：δ_v ∈ O(√(w_v·n)/log n)；**Lemma 7.1**：T < 1、x̄ ∈ Ω(W^{1/T}) 时小于 x̄ 的连接权重期望总和 O(x̄)（温度 < 1 保证幂律尾可和）。**Theorem 7.11**：m = Θ(n)、0 < T < 1、W ∈ O(n)、单权 O(n^{1−ε}) ⇒ a.a.s. Θ(m) 个子句 nice。最后（Section 4.2 "Lower Density Via Random Clause Positions"）：**子句位置是均匀随机的**，Θ(m) 个 nice 子句近似均匀落进 O(n) 个 Voronoi 区域 = 装箱；由 Raab–Steger（即使球数略低于线性仍成立），最大负载 a.a.s. Ω(log n/log log n) ≥ 2^k，鸽笼得 2^k 个子句共 k 变量 → UNSAT 子公式；字典序排序 O(n log n) 定位。
4. **与"社区结构局部性"的对照**（Section 2.2 末段）：Mull 等的 community attachment 模型虽有"局部性"却仍难解；本文解释：该模型的相似度是**二元等价关系**（同社区 = 最大相似、异社区 = 最大不相似），而几何距离给出**连续、多尺度**的相似性——只有后者能产生"常数大小 UNSAT 核"这一易解机制。

## 5. 实验部分

**本文无实验**（会议版与期刊版均纯理论，53 页全为定义/定理/证明）。但引用并回应了两类经验研究，留档：
- **Bläsius et al. [13]**（SAT 2019）：scale-free 3-SAT 在阈值密度、n 最大至 2^15 的 CDCL 实验**观察不到理论预期的指数恶化**。本文由此完成理论–经验闭环：Theorem 5.8 证明"异质性（无几何）确实难" ⇒ [13] 的"实践快"不能归功于异质性 ⇒ Theorem 7.12 证明局部性确实带来易解 ⇒ 工业实例好解的功臣是局部性（Abstract、Section 1、2.1/2.2）。
- 另引 Newsham et al. [51]（scale-free SAT 求解器难度测量）、Zulkoski et al. [62, 63]（工业样例结构实验）、Giráldez-Cru & Levy [40]（局部性度量/生成器）作背景。
- 对我们的含义：**"局部性 ⇒ 易解"在本文是渐近定理而非实测**；有限 n 的实测（正是本项目做的）在其覆盖之外。

## 6. 与本项目映射

我们研究：SAT 实例变量交互局部性半径 r 对求解难度的因果效应——2D 环面 r-球采样子句、n = 400、k = 3、操作阈值 α_c(r) 匹配设计（Δ = α − α_c(r)），已观察到匹配后难度随 r 单调上升 ≥ 4.6 个数量级（PILOT_FINDINGS Round 4，log10 冲突数）。

**6.1 逐条对应（他们的定理 ↔ 我们的实验臂）**

| 我们的组件 | 他们的对应物 | 精确出处 |
|---|---|---|
| 2D 环面地面空间；变量/子句均匀随机位置 | weighted geometric model 的 ground space T^d（取 d = 2）与均匀随机位置 | Section 3 |
| 子句在 r-球内均匀抽 k 变量（硬阈值、紧支撑、等权） | X(c,v) = (w_v/‖c−v‖^d)^{1/T} 软幂律抽样；等权 = w_v ≡ 1 特例（W = n，恰在 Theorem 7.12 的 W ∈ O(n) 内） | Section 3；Theorem 7.12 |
| 小 r 臂（强局部性；匹配 Δ 后极易解） | **Theorem 7.12：T < 1 ⇒ a.a.s. 常数大小 UNSAT 子公式（2^k 子句、k 变量），O(n log n) 可发现**——"局部 ⇒ 易解"的理论对应物 | Section 2.2、Section 7 |
| 大 r 臂（近均匀随机；难） | **Theorem 5.8：无几何 power-law k-SAT 在常数密度下宽度 n^{Ω(1)}～Ω(n)、tree-like 规模 exp(Ω(n^c))**；且 T → ∞ 时几何模型精确退化为无几何模型 | Section 2.1、Section 5；Section 3（T→∞ 退化） |
| α_c(r) 匹配设计（条件在常数概率不可满足上比较） | Theorem 5.8 的假设恰是 "Δ large enough so that Φ is unsatisfiable at least with constant probability"，且**在阈值处也成立**；相变位置 Δ = Θ(1) | Section 2.1；引 [34] |
| 难度–局部性梯度的候选中介机制 | nice clauses（Theorem 7.2/7.11）→ order-k Voronoi 期望区域数 O(W)（Theorem 6.9）→ 装箱最大负载 Ω(log n/log log n) → 同一 k 变量集被 ≥ 2^k 全符号子句覆盖 | Section 4、6、7 |
| α_c(r) 大 r 锚定 4.20≈4.267（随机 3-SAT 理论阈值） | T → ∞ / r → ∞ 退化为经典随机模型 ⇒ 阈值回归 4.267；互为一致性锚点 | Section 3；PILOT_FINDINGS R3 |

**6.2 "局部性"定义的异同（重点）**

- **同**：都是度量几何局部性——变量/子句嵌入同一空间、连接概率随嵌入距离单调衰减；都在 2D 环面上；都有"完全无局部性"极限（T→∞ / r→∞），两旋钮都是局部性强度的连续刻度；原文并把自己与 Giráldez-Cru–Levy [40] 的温度模型对齐（Section 3）——即本文与我们的既有笔记 `giraldez-cru-2017-locality.md` 属同一温度范式，本文是该范式的**证明复杂度定量化**。
- **异 1（软 vs 硬）**：T 是幂律软尾（任意变量都可能入选，概率随距离幂律衰减），我们的 r 是硬截断均匀球采样。故 "T < 1" 不能直接译成临界 r；标定桥用"期望可达变量数"：T = 0 的 k 近邻 ↔ 球内期望变量数 ≈ k 的半径 r* = Θ(√(k/(πn)))（2D），T < 1 区间大致对应"球内期望变量数从 k 到多项式量级"。
- **异 2（单尺度 vs 多尺度 + 权重）**：其连接结构 = 幂律权重 × 幂律距离，天然多尺度；我们等权 + 单一半径 = 单尺度。其对 Mull 等 [47] 的评论（二元等价关系 vs 连续相似度，Section 2.2 末段）提示：**"局部性"口径本身影响易解性结论**——我们 r-球口径的难度梯度不能自动外推到社区结构口径（对照 `li-2021-hcs.md`：层级社区参数造出的可以是难实例）。
- **异 3（渐近 vs 有限 n）**：两条定理都是 a.a.s. 渐近陈述；原文自注 Theorem 7.12 是渐近结果、"小密度下 n 必须非常大才实际变易"（Section 2.2，紧随定理重述）。我们 n = 400、跨 4.6 个数量级的观测落在渐近机制尚未接管的前渐近区——既说明我们测的是其理论不能直接预言的现象，也意味着我们的数据可反向检验"常数大小 UNSAT 核"机制在 n = 400 是否已主导。
- **异 4（refutation vs search）**：两条定理只谈 refutation（宽度 / UNSAT 核）。我们若把 SAT 相搜索难度混入同一指标，则无理论对应物；按 Δ = α − α_c(r) 分层后，Δ > 0 的 UNSAT 臂（我们当前主难度载体，HYPOTHESES.md）才是与其定理同构的实验。

**6.3 可操作的后续检验（由其证明结构直接给出）**

1. **核中介检验**：Theorem 7.12 机制预言小 r 实例中"同一 k 变量集被 ≥ 2^k 个全符号组合子句覆盖"计数显著升高。可在各 r 臂统计：(a) 最大 k-集覆盖数；(b) 最小 UNSAT 子公式大小；(c) CDCL 首个学习子句/冲突是否即该核。若小 r 的难度塌缩由此机制主导，三者应与 r 强相关，且 (b) 在小 r 臂为常数。
2. **异质性对照臂**：加 w_i = i^{−1/(β−1)} 加权、无几何对照臂。Theorem 5.8 预言其不带来易解性——把"局部性是唯一因果因子"补成双臂对照。
3. **温度版生成器**：把硬 r-球换成同款 X(c,v) 温度抽样扫 T，与其定理条件 T < 1 逐点对齐，检验实测难度转折是否出现在 T ≈ 1 附近。
4. **解释力定位**：Theorem 7.12 解释的是 UNSAT 侧"易"的下界机制（好解的原因之一是存在多项式可发现的短 refutation）；我们 ≥ 4.6 数量级梯度中 SAT 相的部分，本文不提供定理，需引用 Giráldez-Cru–Levy 的实验侧证据（决策轨迹聚集、冲突率）补足。

## 7. 可引用结论清单（标注原文 section/theorem 编号）

1. 异质性不能使 SAT 变易：不可满足的 power-law k-SAT（β > (2k−1)/(k−1)、m ∈ Ω(n)、常数概率不可满足，含阈值处）a.a.s. 具有超多项式 resolution 宽度/规模，四条情形 (i)–(iv) 全式见 §4.2 抄录——**Theorem 5.8**（v1: Theorem 2.1；Section 2.1 重述，Section 5 证明；Abstract/Section 1 概括）。
2. 宽度→规模翻译：resolution 规模 ≥ exp(Ω((w−k)²/n))、tree-like ≥ 2^{w−k}（Ben-Sasson–Wigderson [11]；经 Theorem 5.3/5.8 使用）。
3. 线性宽度：β > (2k−2)/(k−2)、0 < ε < (k/2)·(β−2)/(β−1) − 1、Δ ∈ o(n^ε/log^ε n) ⇒ w ∈ Ω(n·Δ^{−1/ε})——**Corollary 5.7**。
4. 指数 tree-like 规模：β > (2k−3)/(k−2)、0 < ε < (k−1)·(β−2)/(β−1) − 1、Δ ∈ o((n/log n)^ε) ⇒ tree-like resolution 规模 exp(Ω(n·Δ^{−1/ε}))——**Corollary 5.9**（配 Lemma 5.5 + Theorem 5.10）。
5. 相变位置：β > (2k−1)/(k−1) 时阈值 Δ ∈ Θ(1)；β < (2k−1)/(k−1) 时常数密度 a.a.s. 平凡不可满足——Section 2.1 引 [34]。
6. "局部 ⇒ 易解"主定理：geometric 模型、T < 1、m = Θ(n)、W ∈ O(n)、w_v ∈ O(n^{1−ε}) ⇒ a.a.s. 常数大小 UNSAT 子公式、O(n log n) 可发现——**Theorem 7.12**（v1: Theorem 2.2；Section 2.2 重述，Section 7 证明）。
7. 机制组件：每子句以 Ω(1) 概率 nice（T < 1、w_v/W → 0）——**Theorem 7.2**；nice 期望 Θ(m)——**Corollary 7.3**；a.a.s. Θ(m) 个 nice——**Theorem 7.11**；δ_v = w_v^{1/(1+T)}·n^{T/(1+T)}·log^{2/(1+T)} n、δ_v ∈ O(√(w_v n)/log n)——Section 7.2（Lemma 7.4）；低密度版经随机子句位置 + Raab–Steger 装箱——Section 4.2。
8. Voronoi 复杂度：随机加权位点 order-k 加权 Voronoi 期望区域数 O(W)（含超立方体版本）——**Theorem 6.9**；order-k 图 ℓ 顶点 ⇒ order-(k+d) 图 Ω(ℓ) 非空区域——**Theorem 6.2**；最坏情形 2D 加权 order-3 / 3D 无权 order-4 达 Ω(n²)——**Corollaries 6.3/6.4**。
9. T = 0 鸽笼论证：2D 等权、order-k Voronoi ≤ 2k(n−k) 区域，m ≥ 2^k·2k(n−k) ⇒ 常数大小 UNSAT 子公式——Section 4（引 Bohler 等的 abstract Voronoi 理论）。
10. 局部性口径评论：几何局部性（连续相似度）≠ 社区结构局部性（二元等价关系）；后者不产生本文易解机制——Section 2.2 末段。
11. 渐近性提醒：Theorem 7.12 为渐近结果，小密度下需 n 极大才实际变易——Section 2.2。
12. 理论–实践裂缝消解：[13] 在 n ≤ 2^15 未观察到异质性实例的指数恶化；本文证明异质性理论上难、局部性理论上易 ⇒ 工业实例好解的功臣是局部性——Abstract、Section 1、2.1/2.2。
13. 模型对接点：本文几何模型的连接权重与 Giráldez-Cru–Levy [40] 温度模型一致——Section 3（可直接作为我们 PS/geometric 两套生成器互证的文献桥梁）。
