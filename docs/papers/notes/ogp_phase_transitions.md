# 精读笔记（合并）：OGP 与解空间聚类相变——随机结构算法难度的两条几何解释路线

> **覆盖论文**：论文 A = Gamarnik《The Overlap Gap Property: a Topological Barrier to Optimizing over Random Structures》（PNAS 2021 综述，arXiv:2109.14409，下称 **[G]**）；论文 B = Achlioptas & Coja-Oghlan《Algorithmic Barriers from Phase Transitions》（FOCS 2008，arXiv:0803.2122，下称 **[B]**）。
>
> **原文获取说明**：本机对 arxiv.org 族主机的直连（curl 与 WebFetch）TLS 均被重置（多次验证）。实际获取通道：(1) 两篇摘要经 OpenAlex API（`api.openalex.org`，curl 可达）从 abstract 倒排索引逐词重建，为逐字全文；(2) 两篇**正文**经 web_reader 服务端渲染 ar5iv（LaTeXML HTML）**完整取得**：[G] 全部小节 + Table 1 + 参考文献表；[B] 正文 + 附录 0.A/0.B 证明；(3) [G] 另经 **PubMed Central 正式发表版全文**（PMC8521669，含参考文献表 1–69 与补充材料说明）逐字核对——这是 PNAS 排版版，与 arXiv 版内容一致但图表移入 SI Appendix（Fig. S1–S6、Table S1），参考文献改数字编号。**本笔记基于全文精读，非摘要级转述**。注意：PMC 通道的文本抽取会**丢失根号与部分上标结构**（例如 α>1+1/√2 被抽成 "α>1+1/2"、ρ*=2/α−1 一度呈 "ρ<2α−1"），凡涉根号处已按 ar5iv 数学版与上下文还原并标注。定理编号按 arXiv v1（ar5iv 渲染）编号；[G] 两个版本章节均无编号，以小节标题定位。ar5iv 页眉日期（"August 2026"）为转换时间戳，非论文日期。文中方括号键（如 [ART06]）为 arXiv 版参考文献键；对应的 PNAS 数字编号在 §6 末尾给出对照。

## 1. 书目信息

### 论文 A [G]

| 项目 | 内容 |
|---|---|
| 标题 | The Overlap Gap Property: a Topological Barrier to Optimizing over Random Structures（arXiv 版标题；OpenAlex 收录的 PNAS 正式题为 "The overlap gap property: A topological barrier to optimizing over random structures"；arXiv 元数据 citation_title 一处作 "Geometric Barrier"，属元数据不一致） |
| 作者 | David Gamarnik（MIT Operations Research Center & Sloan School of Management） |
| 发表 | PNAS, Vol. 118, No. 41, e2108492118, 2021（OpenAlex 出版日期 2021-10-01）；doi:10.1073/pnas.2108492118；PMID 34599090 |
| 预印本 | arXiv:2109.14409（2021-09 提交，综述/introductory article） |
| 性质 | 综述（基于作者在 Simons Institute 读班系列讲稿），NSF DMS-2015517 资助 |
| 结构 | 四部分：最大团引论；"正确的算法复杂性理论"之检讨；OGP 主体（通用设定 → 定义与变体 → 阻断稳定算法 → 具体模型 → 低阶多项式稳定性 → p-spin 基态 → 感知机案例）；Discussion + Table 1 |

### 论文 B [B]

| 项目 | 内容 |
|---|---|
| 标题 | Algorithmic Barriers from Phase Transitions |
| 作者 | Dimitris Achlioptas（UC Santa Cruz；NSF CAREER CCF-0546900 + Sloan Fellowship）、Amin Coja-Oghlan（时属 University of Edinburgh；DFG CO 646） |
| 会议 | FOCS 2008（第 49 届 IEEE Foundations of Computer Science），pp. 793–802；doi:10.1109/focs.2008.11 |
| 预印本 | arXiv:0803.2122（2008-03 提交；本笔记按该 v1 编号引定理） |
| 性质 | 会议长文（扩展摘要体例，附录含图着色与 k-SAT 的完整证明） |
| 结构 | §1 引言（因子 2 之谜）；§2 结果陈述（Definition 1–3，Theorem 2.1–2.5，Conjecture 1）；§3 背景与相关工作（算法 / planted 模型 / 解空间几何）；§4 方法出发点（对称性、随机性与反演：uniform↔planted 转移定理）；§5 证明梗概（图着色）；附录（着色与 k-SAT 证明） |
| 系谱 | 上承 Achlioptas–Ricci-Tersenghi（STOC 2006，[7]）与 Mézard–Mora–Zecchina（PRL 2005，[21]）的 Θ(2^k) 量级 shattering 结果；统计物理侧对应 Krzakala–Montanari–Ricci-Tersenghi–Semerjian–Zdeborová（PNAS 2007，[20]）的 1-RSB "动力学"相变预言。[G] 明言 OGP 术语由 Gamarnik–Li [GL18] 引入，但性质本身由 [ART06] 与 [MMZ05] 发现——即 [B] 的直接前作。 |

## 2. OGP 精确定义（[G] 第三节 "Topological Complexity Barriers. The Overlap Gap Property"）

### 2.1 通用设定与 overlap

优化问题写作 min_σ L(σ, Ξ_N)：解 σ 属于（通常高维、离散的）解空间 Σ_N，装备度量 ρ_N(σ,τ)；Ξ_N 是问题的随机性（实例分布）。例：最大团取 Σ_N={0,1}^N，Ξ_N 为 𝔾(N,1/2)；数分划（Number Partitioning, NPP）取 Σ_N={−1,1}^N、目标 L(σ,ξ)=|⟨σ,ξ⟩|。"overlap"（重叠）一词来自自旋玻璃：范数空间中距离与内积经恒等式
‖σ−τ‖₂² = ‖σ‖₂² + ‖τ‖₂² − 2⟨σ,τ⟩
直接互换，而解向量范数通常彼此相等或近似相等，故"距离结构"即"内积（overlap）结构"。

### 2.2 OGP / e-OGP / m-OGP 的数学表述

- **OGP（单实例）**：设 c* 为实例 ξ 的最优值。称问题 min_σ L(σ,ξ) 以参数 μ>0、0≤ν₁<ν₂ 满足 OGP，若**任何两个 μ-最优解** σ,τ（即 L(σ,ξ)≤c*+μ 且 L(τ,ξ)≤c*+μ）都满足
  **ρ_N(σ,τ) ≤ ν₁ 或 ρ_N(σ,τ) ≥ ν₂**。
  直觉：所有"近优"解两两之间的距离**要么 ≤ν₁、要么 ≥ν₂，中间的区间 (ν₁,ν₂) 是被禁止的**——近优解的距离集合出现" fundamental topological discontinuity"（拓扑不连通）。随机版：对按 Ξ_N 生成的 ξ 以压倒性概率成立。两个非空洞条件：(i) 确实存在距离 ≥ν₂ 的近优解对（否则可取 τ=σ 平凡满足）；(ii) 参数 μ,ν₁,ν₂ 是问题相关的、通常随 N 变化。
- **e-OGP（ensemble 版）**：对实例族 Ξ：任取 ξ,ψ∈Ξ，σ 为 ξ 的 μ-最优解、τ 为 ψ 的 μ-最优解，则 ρ_N(σ,τ)≤ν₁ 或 ≥ν₂；且当 ξ,ψ **相互独立**时前者不可能。OGP 是 Ξ 只含单实例的特例。e-OGP 由 Chen–Gamarnik–Panchenko–Rahman [CGPR19] 引入。
- **m-OGP（多重版）**：对任意 m 个实例 ξ₁,…,ξ_m 及各自 μ-最优解 σ₁,…,σ_m，**至少一对** (σ_i,σ_j) 满足 ρ≤ν₁ 或 ρ≥ν₂——即**找不到 m 个两两 overlap 全部落入 (ν₁,ν₂) 的近优解**。多数应用中 ν₁≈ν₂。首次把 OGP 用作算法障碍：Gamarnik–Sudan [GS17a]；首次用 m-OGP：Rahman–Virág [RV17]；非对称变体：Wein [Wei20]、Bresler–Huang [BH21]。
- 与"非凸"的区别（原文 Figure 3）：L 可以非凸而无 OGP；解空间离散时凸性概念本身失效。OGP 是比非凸更强的拓扑障碍。

### 2.3 为什么阻断"稳定"算法：证明思路直觉版

被排除的算法类由**稳定性（输入不敏感性）**刻画，这正对应当代最强的一类多项式算法。

- **κ-稳定算法**：算法 A 看作映射 ξ↦σ=A(ξ)。给定参数化实例族 (ξ_t), t∈[0,T]（离散或连续），称 A 对该族 κ-稳定，若每步 ρ_N(A(ξ_{t+1}),A(ξ_t)) ≤ κ：输入的小扰动只引起输出的小变化。
- **阻断定理（e-OGP 版）**：设 e-OGP 对族 (ξ_t) 成立，另加两条件——(a) ξ₀ 的 μ-最优解与 ξ_T 的 μ-最优解之间不存在 ρ≤ν₁ 的配对（端点"远离"；端点通常独立，可用矩方法直接验证）；(b) κ < ν₂−ν₁。则 **A 不可能输出 μ-最优解**。
- **反证（原文完整推理链）**：若每步输出 σ_t=A(ξ_t) 都 μ-最优，则 OGP 强制 ρ(σ₀,σ_t)∈[0,ν₁]∪[ν₂,∞)。由 (a) 端点 ρ(σ₀,σ_T)≥ν₂，而序列从 σ₀（距离 0）出发，必存在某 t 使 ρ(σ₀,σ_t)≤ν₁ 且 ρ(σ₀,σ_{t+1})≥ν₂。由三角不等式
  κ ≥ ρ(σ_t,σ_{t+1}) ≥ |ρ(σ₀,σ_t)−ρ(σ₀,σ_{t+1})| ≥ ν₂−ν₁ > κ，矛盾。
  一句话：**算法无法"跳过"宽度为 ν₂−ν₁ 的 gap，而其每步位移被稳定性限死在 κ 以内**（原文 Figure 4 示意：解序列被迫从 ν₁-圆盘跨到 ν₂-圆外部）。
- **m-OGP 版**：取 m+1 个实例，构造插值族：t=0 时 m 个实例全是 ξ₀ 的拷贝，t=T 时变为 m 个独立实例 ξ₁,…,ξ_m；构造取对称形式使任意两个输出 A(ξ_{i,t}),A(ξ_{j,t}) 的期望距离同为 Δ_t。Δ_t 从 0 连续增大到 >ν₁，而稳定性使其增量 ≤κ，故某 t 处 Δ_t∈(ν₁,ν₂)；再对期望做集中化（[GS17b],[Wei20] 用标准方法；[GK21] 改用 Ramsey 极值组合：生成 M≫m 个实例，Ramsey 定理保证存在 m-子集两两距离全落 gap 内），得所有 m(m−1)/2 个距离同时落入禁区——与 m-OGP 矛盾（原文 Figure 5）。
- **稳定类的覆盖面**：局部/顺序局部算法 [GS17a, GS17b, RV17]；**低阶多项式算法**（low-degree polynomials：解由对实例逐项求值的多变量多项式 p_j(ξ) 给出；与 Sum-of-Squares 的联系使其被视为已知最强多项式类 [HS17, HKP+17, Hop18]）——[GJW20a, Wei20, BH21] 证明其对 p-spin 基态、稀疏随机图最大独立集、随机 K-SAT **即使次数高达 O(N/log N) 仍然稳定**；近似消息传递 AMP [GJ19, GJW20a]；量子 QAOA [FGG20a]；线性时间尺度的 Langevin 动力学 [GJW20b]（经 Grönwall 型界：两条轨迹发散率 ~‖ξ−ξ̃‖e^{κs}，在 s=O(N) 时可控）；MCMC（最大团情形，Jerrum [Jer92] 的混合时间下界）。

### 2.4 两个范例计算（"OGP 如何被算出来"）

- **数分划 NPP**（[G] §"OGP for concrete models"；X_i i.i.d. N(0,1)）：发排版文本口径最优值 ~ N·2^{−N}（多项式前因子在文献间有 N/√N 之别，不影响指数结构；下同）；Karmarkar–Karp [KK82] 达 N·e^{−c log₂²N}（c≈0.721 [BM08]），与最优值的乘性差距 2^{N−O(log₂²N)}。考察目标值 2^{−αN}·poly(N)、内积 N^{−1}⟨σ,τ⟩=ρ 的解对，其期望个数 ~
  **exp(N(H((1−ρ)/2) − 2α log 2))**（H 为二元熵）。
  对每个 α∈(1/2,1) 存在 (ρ₀,1) 使期望指数小 ⇒ 取 μ=2^{−αN}−2^{−N}、ν₁=0、ν₂=N(1−ρ₀)/2 得 OGP：任何 μ-最优解对的归一化内积**要么 =1、要么 ≤ρ₀**（发排版原文逐字："N^{−1}⟨σ,τ⟩ is either one or at most ρ₀"）。对 α<1/2（算法实际所处的尺度），[GK21] 证明对所有严格正 α 有适当常数 m 的 m-OGP，且 m 随 N 增长可推进到 2^{−O(√(N log N))}（注：PMC 文本抽取丢根号呈 "N log N"，此处按 ar5iv 数学版还原）——由此猜测问题在优于该值时难。与独立集对照：后者只需**常数** m=m(ε)。
- **最大团**（𝔾(N,1/2)，最大团 ~2log₂N [AS04]，Karp 1976 [Kar76] 提出朴素算法已达 log₂N（半最优）且再无改进——"the most 'embarrassing' open problem"）：取大小 αlog₂N 的团（α∈(1,2)：存在性已知、算法不可达）。两个团交大小要么 ≥ν̃₁(α)、要么 ≤ν̃₂(α)，其中 ν̃_j(α)=x_j(α)·log₂N，x₁,x₂ 是二次方程 **x²/2 − x + 2α − α² = 0** 的两根，**两根存在 ⟺ α > 1+1/√2**——此即 OGP 成立域 [GS17a, GJW20a]。
- **ensemble 相变（[G] 独有的新现象）**：边重采样插值 G₀→G_{(N choose 2)}（按随机顺序逐条重采样边；相邻实例只差一条边，端点独立）。两图各取 αlog₂N 团、交为 xlog₂N 的期望 ~exp((1+o(1))log₂²N·((1−ρ)x²/2 − x + 2α − α²))，ρ 为重采样边比例。两根存在 ⟺ **ρ < ρ* = 2/α − 1**（α=1.72 时 ρ*≈0.163，发排版原文数值逐字核对）：ρ<ρ* 时 overlap 被 gap 隔开，ρ>ρ* 时 gap 消失。ρ* 是"前所未知的新相变"，与自旋玻璃的 chaos 性质相关但在 p-spin 中 chaos 对应 ρ*=0（任意正比例翻转使新旧基态近正交 [Cha09, CHL18, Eld20]）。注意：**chaos 本身不构成算法障碍**（SK 模型有 chaos 却多项式可解 [Sub18, Mon19]），它是建立 e-OGP 的工具。

### 2.5 OGP 的"紧"性与感知机反例

- **p-spin 基态**：Subag [Sub18]、Montanari [Mon19] 的多项式算法**恰好在模型不呈现 OGP 的区域**工作（按 Parisi 测度分析）；El Alaoui–Montanari–Sellke [AMS20] 推广到有 OGP 的模型，但只达到"OGP 出现前"的最优 μ——"算法给出使 OGP 不成立的最小 μ 对应的 μ-最优解"。反方向，低阶多项式被排除的阈值恰在 OGP 出现点。[G]：对该问题族，"OGP approach provides a tight classification of solvable vs not yet solvable"。
- **Table 1（[G] Discussion）**：10 类问题中 7 类"OGP matches known algorithms"（ER 图团、稀疏 ER 独立集 [GS17a,RV17,GJW20a,Wei20,FGG20a]、随机 K-SAT [GS17b,COHH17,BH21]、自旋玻璃基态、NPP（到亚指数因子）、planted clique [GZ19]、稀疏线性回归（到常数因子））；3 类 Not known（最大子矩阵 [GL18]、随机超图匹配 [CGPR19]、主子矩阵恢复）。原文断言：**迄今不知道任何"呈现明显算法难度却不呈现 OGP"的模型**。
- **感知机反例（[G] §"the curious case of the perceptron model"）**：二元对称感知机（找 σ∈{±1}^N 使 ‖Xσ‖_∞≤κ）。严格阈值 α_SAT(κ) 已知 [PX21, ALS21]； asymmetric κ=0 情形物理预测 0.83 [KM89]、上界严格证实 [DS19]。Kim–Roche 算法 [KR98] 在 α<0.005 找到解。吊诡之处：对称模型在**一切正密度 α>0** 都严格呈现**弱聚类**，且**每个簇都是单点**（"needles in the haystack"，针在干草堆）[PX21, ALS21]；NPP 同样如此 [GK21]（熵型、簇基数亚广泛）。因此**弱聚类 ⇏ 难**——可能存在呈弱聚类却多项式可解的模型；解释是算法的解选择"非均匀"，可绕开按均匀测度定义的聚类图景。而该模型在 α 严格小于 α_SAT(κ) 处**有 OGP**（矩计算，严格 [BDVLZ20]），⇒ 强聚类亦成立，此区域被猜想难、且可望用 OGP 方法排除低阶多项式类。
- 聚类阈值对计数测度的稳健性：把均匀测度换成有偏测度可推迟弱聚类 onset（小 K [BRTS19]），但大 K 到二阶为止阈值仍是 2^K log 2/K [BS20]——"该值标记一个基本性相变点的更稳健证据"。

## 3. [B] 的聚类相变：定义、定理与"barriers"的含义

### 3.1 定义（[B] §2，逐字级）

- 实例 I 的能量函数 H_I: D^n→ℕ 数被违反的约束数；**路径高度** = max_i H(σ_i)（路径上最多同时被违反的约束数）。**Definition 1**：解 = H(σ)=0；S(I) 为解集；"**The clusters of an instance I are the connected components of S(I)**"——S(I) 按汉明距离 1 连边（Remark 1：距离 1 的选择"somewhat arbitrary (but conceptually simplest)"，多数结果允许换成 o(n)）后的连通分支为**簇（cluster）**；**region** = 非空簇并。
- **Definition 2（shattering，破碎）**：称 I_{n,m} 的解集 shatters，若存在常数 β,γ,ζ,θ>0 使 w.h.p. S(I) 可划分为 regions 满足四条：
  1. region 数 ≥ e^{βn}；
  2. 每个 region 含全部解的 ≤ e^{−γn} 比例；
  3. 任意两 region 间汉明距离 ≥ ζn；
  4. **跨 region 的任何路径高度 ≥ θn**（能量/挫折障碍）。
- **Definition 3（rigid / loose）**：解 σ 中变量 v 是 f(n)-rigid，若任何 v 取值不同于 σ 的解 τ 都有 dist(σ,τ)≥f(n)；f(n)-loose，若对每个候选值 j 存在 τ(v)=j 且 dist(σ,τ)≤f(n)。

### 3.2 三大定理与阈值

- **Theorem 2.1（随机图 k-着色）**：存在 ε_k→0，使平均度 d 满足 **(1+ε_k)·k·ln k ≤ d ≤ (2−ε_k)·k·ln k** 时解空间 w.h.p. shatters。
- **Theorem 2.2（随机 k-SAT）**：存在 ε_k→0，使子句密度 r 满足 **(1+ε_k)·(2^k/k)·ln k ≤ r ≤ (1−ε_k)·2^k·ln 2** 时解空间 w.h.p. shatters。即：破碎从"已知算法全部失效点"稍上开始，**一直持续到几乎可满足性阈值**（可满足上界 2^k ln 2 − O(k)，Achlioptas–Peres [6]；存在性由 Ding–Sly–Sun 对大 k 严格化，见 [G] 引 [DSS15]）。
- **Theorem 2.3（随机超图 2-着色）**：(1+ε_k)·(2^{k−1}/k)·ln k ≤ r ≤ (1−ε_k)·2^{k−1}·ln 2。
- **Remark 2**：区间对小子句长度可为空；粗算建议 k≥6（超图）、**k≥8（k-SAT）**、k≥20（着色）。
- **Theorem 2.4（刚性）**：在上述破碎密度区取 uniform instance-solution 对 (I,σ)：w.h.p. **rigid 变量数 ≥ γ_k·n，且 γ_k→1**——过渡点之上，**典型解中几乎每个变量都是刚性的**（Remark 3：紧，因为总有 Ω(n) 个变量不被任何约束触及）。k-SAT 的证明机制（附录 0.B.4，Lemma 31）：存在 ≥(1−δ)n 个变量的集合 U，其中每个变量在 σ 下**支撑（support）γ ln k 条不含 U 外变量的子句**（唯一满足子句）；再配一阶矩排除"小集合张出多对内部子句"，得 U 中变量全部 rigid。
- **Theorem 2.5 + Conjecture 1（过渡点之下的松软性）**：着色 d ≤ (1−ε_k)k ln k、超图 r ≤ (1−ε_k)(2^{k−1}/k) ln k 时，w.h.p. 典型解中**每个变量都 o(n)-loose**（事实上 w.u.p.p. 改任一顶点颜色只需连带改 O(log n) 个）；k-SAT 的相应命题未能证明，列为 **Conjecture 1**（r ≤ (1−ε_k)(2^k/k) ln k）。
- 摘要的定性行话：解集在 k≥2χ 时"looks like a giant ball"，在 k≤(2−ε)χ 时"like an error-correcting code"（纠错码：指数多个、两两远离的码字）。

### 3.3 方法：uniform↔planted 转移定理

[B] 的技术核心（§4 + Theorem 5.1 / 0.A.1 / 0.B.1）是**转移定理**：行/列"well-spread"的 0-1 矩阵中均匀取 1 的两种方式（先列后行 / 先行后列）分布相同；据此，只要解个数围绕期望充分集中（着色/超图用二阶矩 + Friedgut 锐阈值；k-SAT 的解数**不**如 (4) 式集中——二阶矩对任意密度都指数超一阶矩平方——改用 [6] + 锐阈值分析得 w.h.p. |S| ≥ E|S|·exp(−k·2^{3−k}·n)，k≥8，Lemma 22），则"随机实例的随机解"的性质可由"planted 实例的 planted 解"推出（k-SAT 版误差 exp(−k·2^{3−k}·n − f(n))，Theorem 0.B.1）。原文的地貌比喻：planted 解相当于在能量地貌 H 上挖一个"火山口（crater）"；"只要 H_F 本已有指数多个火山口且个数集中，再挖一个不改变什么……密度升高后，新挖的口越来越显眼（从典型值降到 0 需要越来越大的锥），** Hence the ease with which algorithms solve planted instances of high density**"。这也解释了 §3.2 引 Coja-Oghlan–Krivelevich–Vilenchik [12,13]：高密度 planted 模型解空间几何极简单——**恰好一个簇**。

### 3.4 "barriers"具体指什么算法类

必须诚实：**[B] 没有证明"clustering ⇒ 不存在多项式算法"这类不可能性定理**。原文的"barrier"主张是两层：

1. **经验—理论对齐**：对三个问题证明"所有已知多项式算法的失效点"与"解空间几何剧变点（动力学相变）"**精确重合**（摘要原话："its location corresponds precisely with the point were all known polynomial-time algorithms fail"）。具体失效线：k-SAT 单位子句算法 [10]（Chao–Franco）达 O(2^k/k)；已知最好（[G] 引 Coja-Oghlan [CO10]）达 (2^K/K)·log K；**不存在**达 (2^k/k)·ω(k)（任意 ω(k)→∞）的多项式算法（2008 年时点）。着色：简单着色算法 [18,2] 达 d≤k ln k，而可着色到 d~2k ln k（[5]，Nature 2005）——"因子 2"对所有算法顽抗。超图 2-着色同构。
2. **对具体算法的形式化失败**：§3.1 证明在密度 ≥ 2^k ln 2 − k 时，若 SP 能完成其本职（逼近一致解测度的边际），则 BP 也能——故 SP 相对 BP 无附加能力；而 Montanari–Ricci-Tersenghi–Semerjian [23] 证明 **BP 引导的 decimation（Gibbs 采样逐步定变量）在 (2^k/k)·ln k 之上失败**：仅小部分变量被赋值后边际计算即不收敛。SP 的实验表现在 k=5,6 已不稳定，且"强烈提示 SP 不能在解存在性密度处找到解"。

**形式化的"OGP 阻断稳定算法"是后续工作**（GS17a/b、RV17、Wei20、BH21 排除局部与低阶多项式类；Het16 排除 SP；COHH17 排除 WalkSAT 变体），由 [G] 综合为统一方法论——这正是两篇文章的分工：[B] 定位"几何相变发生在算法失效点上"，[G] 给出"相变如何变成对算法类的严格排除"。

### 3.5 阈值速查表（随机 k-SAT，大 k）

| 密度 | 量级/值 | 来源 |
|---|---|---|
| 单位子句算法上限 | O(2^k/k) | [B] §1 引 [10] |
| 已知最好多项式算法 | (2^k/k)·ln k | [G] §2 引 [CO10]；[B] §3.1（BP-decimation 失败线） |
| **shattering 下缘（定理）** | ≥ (1+ε_k)·(2^k/k)·ln k | [B] Thm 2.2 |
| 弱聚类 onset（[G] 口径） | ≈ α_ALG=(2^K/K)·log K（"close to α_ALG"）；同文另一处写 2^K·log 2/K（两处相差 ln K/ln 2，后者与物理文献的冻结转变 α_f 一致；引用以 [B] 定理为准） | [G] §2 |
| 冷凝 α_COND | α_ALG < α_COND < α_SAT；大 K 严格证据 α_COND ~ 2^K·log 2 − C（显式常数，远高于 α_ALG） | [G] §2 引 [KMRT+07] 及严格工作 |
| 可满足阈值 α_SAT | 2^k·ln 2 − O(k)（下界 [6]；大 k 存在性 [DSS15]） | [B] §2；[G] §2 |
| 强聚类 onset（猜想） | ~2^K 量级（已知下界 2^K，非 2^K/K） | [G] §2 |

[KMRT+07] 物理图景（[G] §2 转述）：过 α_COND 时覆盖多数解的簇数从**指数多个骤降为常数个**、最大簇占非平凡比例；自旋磁化出现长程依赖；Gibbs 测度下解对的 overlap 有非平凡极限分布（Parisi 测度）。更早（α<α_COND 前已）每簇含非平凡比例的**冻结变量（frozen variables）**：在给定簇内恒取同值。[MPRT16] 猜想冻结变量是难度主因并构造 Backtracking Survey Propagation（BSP），猜想有效至 α_COND。[G] 的两点保留：(i) 严格证据表明 α_COND ≫ α_ALG，SP 反而在更低处已被排除；(ii) 冻结变量概念只适用于离散自旋，对连续 spin（如球面 p-spin）的优化问题失效——正如可满足性相变解释不了最大团。

## 4. OGP 与解空间聚类：联系与区别

### 4.1 蕴含方向

- **OGP ⇒ 强聚类（单实例，成对 m=2 情形）**：若每对 μ-最优解距离 ≤ν₁ 或 ≥ν₂ 且后者非空洞，则解集强聚类，且每簇直径（尺度上）严格小于簇间距——"In fact this is precisely how the strong clustering property was discovered to begin with in [ART06] and [MMZ05]"。
- ** converse 不必真**：可设想强聚类但簇直径大于簇间距、overlap 填满连续区间；[G] 明言当时不知此类例子。
- **[B] 的 shattering 与 [G] 的弱/强聚类的术语对应**：[G] 自认 weak/strong 二分是作者自己的术语选择。A&CO 的 Definition 2 是对**全部解**的 region 划分（指数多 region、每个 ≤e^{−γn} 比例、两两距离 ≥ζn、路径高度 ≥θn）——比"弱聚类 + 灰色隧道"更强于弱、但不同于 OGP 式强聚类（region 允许内部由多个簇组成，不要求簇内 O(1)-翻转连通）。其证明方式（planted/典型解视角，允许指数小比例例外解存在）对应 [G] 说的 weak clustering 的建立方式；ART06/MMZ05 的并界方法（对**所有**解）反而只能到 Θ(2^k)。[B] 自己强调这是方法上的关键差别：从"对一切解的 union bound"转为"典型解 + 指数小例外"。
- **为什么要区分（[G] 的算法学理由）**：算法产生的解一般**非均匀分布**，可能落入例外集 Σ^c，故基于"簇间线性分离 + 指数大能量障碍"的阻断论证可能失效；强聚类则保证算法的**每个**输出都在某簇中——两个实现落入不同簇即意味着算法能"跳"过 O(N) 距离，这个直觉经 ensemble 化（e-OGP）+ 稳定性才形式化。

### 4.2 区别清单

1. **对象**：聚类是"一个实例内解集的几何"；OGP 直接陈述"近优解对的距离集合"的拓扑，且其算法学用途几乎总是 **ensemble 版**（相关实例族上的 e-OGP/m-OGP）——聚类概念的 ensemble 化（相关实例序列上聚类如何演化）本身是 [G] 列出的 open problem（[BAJ21] 在球面自旋玻璃上有初步进展）。
2. **静态 vs 动态**：m-OGP 本质是关于"m 个近优解不能同时驻留禁区"的动态陈述，正是插值论证所需要的；强聚类尚不清楚如何与 m-OGP 衔接，也未知的还有"哪种聚类定义可用于 refutation 型论证"。
3. **充分性**：强聚类/OGP ⇒（配合算法稳定性）难度证据；弱聚类（甚至单点簇）⇏ 难（感知机反例）。因此"解空间几何腿"的硬度证据应表述为 **OGP+稳定性** 机制，而非朴素的聚类计数。
4. **第三层：condensation/frozen**：聚类（1-RSB 玻璃化）之上还有冷凝与冻结变量，与算法难度的联系目前主要是猜想（BSP）与部分严格证据（α_COND 位置），且不覆盖优化型问题；[G] 把 OGP 的优势归结为：定义问题无关、可严格验证、可直接转成算法排除。

### 4.3 一页对照表

| | [B] shattering / clusters | [G] OGP |
|---|---|---|
| 定义对象 | 解集 S(I) 的连通分支与 region 划分 | 近优解对的距离/overlap 集合 |
| 关键量 | e^{βn} 个 region、距离 ≥ζn、路径高度 ≥θn | (ν₁,ν₂) 禁区；μ-最优；m-重 |
| 适用范围 | 离散 CSP（可满足型）；大 k 渐近 | CSP 与连续优化（p-spin、NPP、团、回归……） |
| 算法学结论 | 与已知算法失效点重合（解释性）+ BP-decimation 失败 [23] | 对稳定算法类（局部/低阶/AMP/QAOA/Langevin）的严格排除 |
| 严格化程度 | 定理（k≥~8/6/20） | 定理（模型逐一验证） |
| 建立方法 | uniform↔planted 转移（典型解） | 一阶矩/二阶矩 + 插值 + 稳定性 |

## 5. 与本项目映射：局部性半径 r 对求解难度的因果效应

我们观察（docs/PILOT_FINDINGS.md）：控制 n、α、度分布、子句内容、σ-冗余度后，仅 r 变化产生单调因果梯度——匹配距阈密度 Δ=+0.2 时，中位 log₁₀(冲突数) 从 r=0.06 的 1.38 到 r=1.5 的 ≥6.00（**跨度 ≥4.6 个数量级**，高端因 10⁶ 冲突预算删失而为下界）；α=5.0 深不可满足区 r=0.08→0 冲突（传播即时反驳）而 r=1.5→2.3×10⁶（六个数量级摆动）；α_c(r) 强非单调（r=1.5→4.20，与随机 3-SAT 理论阈值 4.267 吻合；r=0.11→3.85；r=0.08→3.25；r=0.06→3.00）。

### 5.1 梯度的理论解读：玻璃化/长程关联在大 r 端

- **大 r（弱局部性）端 = 两篇文章理论的领地。** r 大时子句在环面上近乎均匀撒布，实例系综逼近均匀随机 3-SAT，因子图关联长度遍及全图——这正是 OGP/1-RSB 玻璃化需要的"系综级长程耦合"。在 α_c 附近的超临界带，[B] Thm 2.2 的图景（k=3 时由物理文献 [KMRT+07] 预言、α_d≈3.86 属物理值而非本篇定理）适用：解空间 shattering，典型解中几乎全部变量 rigid（Thm 2.4 的 k≥8 定理、k=3 为物理图景），近优/可行解的 overlap 落入禁区（OGP）。CDCL 虽不在被严格排除的稳定类中（见 5.4），但其冲突驱动搜索在刚性解空间中的行为与我们观测的 10⁶ 冲突删失一致：早期赋值承诺遇刚性变量无法在簇内翻转修正，只能靠大量冲突学习回退（这是解释性桥接，非定理）。
- **小 r（强局部性）端 = "giant ball"体制。** 子句被限制在 r-球内，因子图被空间切成近独立区块：解空间不 shatter（对应 [B] Thm 2.5 的 loose 变量图景——改一个变量只需连带改 O(log n) 个），不存在需要全局竞争才能形成的禁区。与直接对口的严格结果是本目录已精读的 Bläsius et al.（RSA 2023，`blasius2023_geometry.md`）：几何局部性 ⇒ 常数大小不可满足子核、O(n log n) 可找到——解释 r≤0.08 即使 Δ=+0.6 也中位 ~20–30 冲突、零删失。
- **关键辨析（写报告时勿混淆）**：决定 OGP 与否的不是"图局部稀疏/树状"，而是**系综关联衰减长度**。稀疏随机图 𝔾(N,c/N) 本身局部树状，其独立集问题照样有 OGP [GS17a, RV17, Wei20]。我们的 r 恰是关联衰减长度的直接旋钮：r 小 ⇒ 实例耦合尺度 O(r)，长程玻璃序无从建立；r 大 ⇒ 平均场式全局竞争 ⇒ OGP。因此我们的"强局部性 ⇒ 极易解"不是 OGP 的平凡推论，而是它的对偶面：**OGP 是长程关联的产物，r 截断了它**。
- **α_c(r) 非单调与提前相变**：强局部性使每个 r-球内有效约束密度升高，局部簇提前互相矛盾 ⇒ α_c 从 4.267 降到 ~3.0。这是"局部玻璃化"现象学，两篇理论均未覆盖（它们只处理均匀随机系综），是受控实验可贡献的新观察。

### 5.2 概念三分法对应

PLAN_v5 的三分法中：

| 我们的腿 | 他们的概念 | 对应文本 |
|---|---|---|
| **解空间几何** | [B] 的 clusters/regions/shattering/rigidity；[G] 的弱/强聚类与 OGP | [B] Def. 1–3, Thm 2.1–2.4；[G] §2 聚类定义、§3 OGP 定义 |
| **推断稳定性** | [G] 的 κ-稳定性：局部算法、低阶多项式、AMP、QAOA、Langevin | [G] §"OGP is an obstruction to stability" 等 |
| **结构局部性** | 两文均无此旋钮（均匀随机系综）；r 决定实例落在哪个几何体制 | 我们的 E3a 生成器 + Bläsius 温度式局部性 |

即：r 是三分法中的"因"，解空间几何与算法稳定性是两个中介层——这正是中介分析（树宽/HCS 深度作中介变量）的假设结构。R3b 中 r=0.15 vs r=0.30 同 α_c 同 α 的 ≥2.7 个数量级对比，是"纯拓扑效应"的最干净单点证据。

### 5.3 受控经验能补充理论之处

1. **有限 n、k=3 的定量效应量**：[B] 定理是大 k 渐近（其 Remark 2 自认 k-SAT 需 k≳8），[G] 的 OGP 计算也以渐近为主；我们给出 k=3、n 数百–数千尺度上 4.6+ 个数量级的剂量—响应曲线，理论不提供此数。
2. **因果方向**：理论给出"系综几何 ↔ 算法表现"的关联与机制；我们做干预（保持度分布/内容/冗余度，只动 r）+ E3b 度保持交换链的"结构破坏"对照，把"几何是原因"从理论假设变成受控检验——这是对 [B]–[G] 路线的实验化补全。
3. **CDCL 机制中介**：OGP 排除的是稳定算法类；CDCL 的子句学习是自适应过程，不在被证排除之列，两文对 CDCL 只能给出机制性解读。我们的中介分析（局部性→树宽→难度）恰好为这一缺口提供经验对应物（H1）。
4. **planted 侧观察的理论呼应**：pilot R1 发现"planted 实例对 CDCL 平凡且易解性对 r 不敏感"。[B] §4 的 crater 比喻与 [12,13]（高密度 planted 解空间恰一簇）给出理论解释：planted 火山口几何主导难度，局部性不破坏它——"locality can't save planted formulas"由此获得文献定位（SAT 侧局部性失效、UNSAT 侧局部性主导的可报告结构）。
5. **转述红线**：(i) 不得把 [B] 表述为"证明了 clustering ⇒ 难/NP-hard"——它证明的是相变点与已知算法失效点重合 + BP-decimation 形式化失败；(ii) 不得把 [G] 的排除范围扩大到 CDCL；(iii) "聚类 ⇒ 难"必须表述为"OGP+稳定性 ⇒ 特定算法类失效"，感知机反例（弱聚类+单点簇+可能有低密度多项式算法）应作为反例记忆；(iv) [G] 中弱聚类 onset 的两处口径（(2^K/K)log K 与 2^K log 2/K）相差 ln K/ln 2，引用一律以 [B] Thm 2.2 的 (1+ε_k)(2^k/k)ln k 为准；(v) k=3 的具体聚类/冷凝数值（如 α_d≈3.86）属物理方法结果，标注"物理预测，非本两篇定理"。

## 6. 可引用结论清单（标注原文位置）

**论文 A（Gamarnik, arXiv:2109.14409；章节按 arXiv 版小节标题）**

- A1（OGP 定义）：min_σ L(σ,ξ) 以 (μ,ν₁,ν₂) 满足 OGP ⟺ 任意两个 μ-最优解 ρ_N(σ,τ)≤ν₁ 或 ≥ν₂；随机版以高概率成立。——§"The OGP and its variants"。
- A2（e-OGP / m-OGP）：e-OGP 定义（独立实例对禁近距配对）[CGPR19 引入]；m-OGP 定义（m 个近优解不能两两同落禁区）[GS17a 首用 OGP 阻断、RV17 首用 m-OGP；Wei20/BH21 非对称变体]。——同上小节。
- A3（阻断定理）：κ-稳定算法 + e-OGP + (a) 端点解远离 + (b) κ<ν₂−ν₁ ⟹ 无法输出 μ-最优解；证明为三角不等式反证，"算法无法跳过 gap"。——§"OGP is an obstruction to stability"。
- A4（低阶多项式稳定性）：度 d=O(N/log N) 的低阶多项式算法对 p-spin、稀疏独立集、随机 K-SAT 仍稳定，故被 OGP 排除。[GJW20a, Wei20, BH21]。——§"Stability of low-degree polynomials"。
- A5（NPP 计算与 m-OGP 极限）：解对期望 exp(N(H((1−ρ)/2)−2α log 2))；α∈(1/2,1) 有 OGP；m 随 N 增长的 m-OGP 达 2^{−O(√(N log N))}，猜测此为难度边界。[GK21]。——§"OGP for concrete models"。
- A6（最大团 OGP）：α>1+1/√2 处 OGP（二次方程 x²/2−x+2α−α²=0 两根）；ensemble 相变 ρ*=2/α−1。[GS17a, GJW20a]。——同上。
- A7（p-spin 紧对应）：Subag/Mon19 算法恰在无 OGP 区域最优；AMS20 达 OGP onset；低阶多项式失败点恰在 OGP onset；Langevin 线性时间尺度被排除 [GJW20b]。——§"OGP and the problem of finding ground states of p-spin models"。
- A8（弱/强聚类定义与 onset）：弱聚类=除指数小例外集外按 O(1)-翻转连通簇划分、簇间 O(N) 距离 + 指数大能量障碍（"energetic barrier"）；**α_ALG 之下解集主体是一个连通块**（发排版逐字："Below α_ALG, the bulk of the set of satisfying assignments constitutes one connected subset"，即 [B] 摘要的 "giant ball"）；onset ≈ α_ALG=(2^K/K)log K；强聚类=无例外，onset 猜想 ~2^K，由 OGP 蕴含而发现 [ART06, MMZ05]；弱聚类经 planting 建立；有偏测度不改变大 K onset 到二阶 [BS20]。——§"In Search of the 'Right' Algorithmic Complexity Theory"。
- A9（冷凝与冻结）：α_ALG < α_COND < α_SAT [KMRT+07]；过 α_COND 簇数从指数骤降为常数、Parisi 测度极限出现；冻结变量与 BSP 猜想 [MPRT16]；严格证据 α_COND~2^K log 2 − C ≫ α_ALG；两个概念均不适用于优化型问题。——同上。
- A10（感知机反例）：对称二元感知机在一切 α>0 弱聚类且簇为单点 [PX21, ALS21]，但 Kim–Roche [KR98] 在 α<0.005 给出算法；OGP 在 α 严格低于 α_SAT(κ) 处成立 [BDVLZ20]（且该 α 严格高于 0.005）⇒ 强聚类成立、该区被猜想难。发排版的总结金句可引："the weak clustering property is provably not an obstruction to polynomial time algorithms, but OGP and its implication, the strong clustering property, likely is, at least for the case of stable algorithms."——§"OGP, the clustering property, and the curious case of the perceptron model"。
- A11（总括）：Table 1 十类问题七类 OGP 与已知算法匹配；"不知道任何有明显算法难度而无 OGP 的模型"。——§"Discussion"。

**论文 B（Achlioptas & Coja-Oghlan, arXiv:0803.2122）**

- B1（Def. 1 + Remark 1）：cluster = S(I) 在 1-翻转（或 o(n)）邻接下的连通分支；region = 簇的非空并；路径高度 = max 违反约束数。——§2。
- B2（Def. 2 shattering）：≥e^{βn} 个 region、每个 ≤e^{−γn} 解比例、两两汉明距离 ≥ζn、跨 region 路径高度 ≥θn。——§2.1。
- B3（Thm 2.1，着色）：(1+ε_k)k ln k ≤ d ≤ (2−ε_k)k ln k 处解空间 shatters。
- B4（Thm 2.2，k-SAT）：**(1+ε_k)(2^k/k) ln k ≤ r ≤ (1−ε_k)2^k ln 2 处解空间 shatters**——下缘与已知算法失效点 (2^k/k)ln k 重合，上缘达可满足阈值。核心可引。
- B5（Thm 2.3，超图 2-着色）：(1+ε_k)(2^{k−1}/k) ln k ≤ r ≤ (1−ε_k)2^{k−1} ln 2。
- B6（Remark 2）：k≥6/8/20（超图/k-SAT/着色）粗算建议；区间对小子句长度可能为空。
- B7（Def. 3 + Thm 2.4）：破碎区典型解中 rigid 变量 ≥γ_k n、γ_k→1（k-SAT 证明经支撑子句计数，Lemma 31）。
- B8（Thm 2.5 + Conjecture 1）：过渡点之下每变量 o(n)-loose（着色/超图定理；k-SAT 为猜想）；连带改动 O(log n)。
- B9（转移定理）：uniform instance-solution 对的性质由 planted 对推出（着色 Thm 5.1/0.A.1；k-SAT Thm 0.B.1，误差 exp(−k·2^{3−k}n−f(n))，基于 Lemma 22 的解数下界）。——§4–5、附录。
- B10（算法失效定位）：单位子句 O(2^k/k) [10]；BP-decimation 在 (2^k/k)ln k 之上失败 [23]；密度 ≥2^k ln 2 − k 时 SP 的任务若可完成则 BP 亦可；无多项式算法达 (2^k/k)ω(k)。——§1、§3.1。
- B11（planted 几何）：高密度 planted 模型解空间恰一簇 [12,13]；"hence the ease with which algorithms solve planted instances of high density"。——§3.2、§4。
- B12（重叠禁区，着色版 OGP 前身）：典型着色 σ 的 Frobenius 相关 f_σ(τ) 存在禁区 [y₁,y₂]（无 H≤λn 的解落在其中），region C_σ={f>y₂} 被线性汉明距离分离；一阶矩在 planted 模型中证明（Lemma 3/4、20/21）。——§5.4、附录 0.A.9。
- B13（方法声明）：证明严格化 1-RSB 假设的"很大一部分"；定性图景（giant ball → error-correcting code）对二值约束 k 元变量与 k 元约束二值变量两族问题普适，支持"动力学相变是 CSP 普遍现象"的猜想。——摘要、§1。

**[G] 的 PNAS 数字编号对照（部分，仅列本笔记用到且已经 PMC 发排版核对者）**：27=ART06、28=MMZ05、26=Coja-Oghlan 更好算法（α_ALG=(2^K/K)log K）、36=Coja-Oghlan BP-guided decimation 分析（有效至 α≤2^K/K）、40=KMRT+07、41=MPRT16（Marino–Parisi–Ricci-Tersenghi, Nat. Commun. 2016, BSP）、45=GL18、46=GS17a、47=RV17、48=Wei20、49=CGPR19、50=GK21、51=GJW20a、63/64=PX21/ALS21、65=KR98、68=BDVLZ20、69=BAJ21、4–6=QAOA 系列。arXiv 键未经逐一核对全名者（如 [BM08]、[Cha09]、[CHL18]、[Eld20]、[GS17b]、[COHH17]、[Het16]、[Sub18]、[Mon19]、[AMS20]、[HS17]、[HKP+17]、[Hop18]、[GJ19]、[GJW20b]、[Sel20]、[Kar76]、[AS04]、[GM75]、[KK82]、[Jer92]、[KM89]、[DS19]、[BAJ21]）按 arXiv 版原样保留。图号对应：arXiv 版 Figure 2–6 ↔ PNAS 版 SI Appendix Fig. S2–S6（Figure 1 仅 arXiv 版有）；arXiv 版 Table 1 ↔ SI Appendix Table S1。

## 7. 存疑与核对记录

- **[G] 弱聚类 onset 双口径**：发排版正文先说 α_Clust "close to α_ALG"（=(2^K/K)log K），后又写 "onset of weak clustering occurs near 2^K log 2/K"——两处相差 ln K/ln 2 因子，后者与物理文献的冻结转变 α_f 一致，属综述表述层面的出入；引用一律以 [B] Thm 2.2 的 (1+ε_k)(2^k/k)ln k 为准。
- **Kim–Roche 引文已核实**：Kim & Roche, "Covering Cubes by Random Half Cubes, with Applications to Binary Neural Networks", J. Comput. Syst. Sci. 56(2): 223–252, 1998（[G] 发排版编号 [65]；发排版正文误拼作 "Rouche"）。
- **PMC 文本抽取丢根号**：证据链——同一文本中 α>1+1/√2 呈 "α>1+1/2"、ρ*=2/α−1 一度呈 "ρ<2α−1"（但 ρ*=2/α−1=0.163@α=1.72 的数值逐字可核对）、NPP 最优值多项式前因子无法区分 N 与 √N。凡涉根号处已按 ar5iv 数学版还原。
- **m-OGP 推进值**：笔记取 2^{−O(√(N log N))}（ar5iv 数学版口径；与 [GK21] 一致），非 PMC 扁平化的 "N log N"。
- **[B] 的 FOCS 页码**（793–802）与 doi 取自 OpenAlex；arXiv v1 提交月份（2008-03）由编号推断。
- **[B] Remark 2 的 k≥8 等数值**为原文"quick calculations suggest"，非定理条件；k=3 的 α_d≈3.86 为物理文献值（[KMRT+07] 一系），本两篇原文未给出，引用需另行核对原始出处。
- **[G] 另一处引 Karp 猜想与复杂度下界的表述**（log²N/polyloglog N 下界 [RS17]、c>1/2 常数的 log N/loglog N 团 [DM15b]）保留原文转述，未展开核对 [RS17]/[DM15b] 全名。
