# 精读笔记：On the Hierarchical Community Structure of Practical SAT Formulas

> 本目录笔记为 correlation-vs-hardness 项目的文献精读记录。原文 PDF 为第三方论文，未随快照分发。

## 1. 书目信息

| 项目 | 内容 |
|---|---|
| 论文全名 | On the Hierarchical Community Structure of Practical SAT Formulas |
| 作者 | Chunxiao Li\*、Jonathan Chung\*（共同一作）、Soham Mukherjee、Marc Vinyals、Noah Fleming、Antonina Kolokolova、Alice Mu、Vijay Ganesh |
| 机构 | University of Waterloo、Perimeter Institute、Technion、University of Toronto、Memorial University of Newfoundland（MapleSAT 组） |
| 年份 | 2021 |
| Venue | SAT 2021 — 24th International Conference on Theory and Applications of Satisfiability Testing（2021-07，Barcelona，线上），Springer LNCS vol. 12831。PDF 元数据无 venue 标注，据 EasyChair Preprint 5949 与 arXiv:2103.14992 确认 |
| 代码/数据 | 实例生成器、数据与全文：https://satcomplexity.github.io/hcs/ |

**认知修正**：该论文与 implicit hitting set 无关（hitting community structure 仅在 related work 中被引用 [Ganian & Szeider, SAT 2015]），也不是"困难组合结构"综述——它是 MapleSAT 组提出的 **层级社区结构（Hierarchical Community Structure, HCS）** 参数族论文：把 SAT 公式变量关联图（VIG）做递归 modularity 最大化分解，用分解树的形态参数（叶社区大小、社区度、层间边数、深度等）解释 CDCL 求解时间。

## 2. 核心研究问题（写给非计算理论背景的读者）

现代 CDCL SAT 求解器能轻松处理数千万变量的工业实例，但 SAT 是 NP 完全问题，理论预期"难"——这个实践与理论的落差是求解器研究的核心开放问题。学界猜想工业实例携带某种可被求解器利用的结构，并为此提出过两类参数：**correlative**（如 modularity/社区结构，与运行时间相关但存在反例：Mull et al. 构造了高 modularity 却需要指数级 resolution 反驳的公式族）与 **rigorous**（如 backdoor、treewidth，有复杂性理论意义但在工业实例上取值范围差或与运行时间不相关）。本文的目标是提出一组**既有强相关性又有较好理论性质**的参数：即 HCS 参数，并按一套明确的方法论（结构区分性 + 运行时间相关性 + 单参数 scaling 实验）来检验它。

## 3. 方法概要

- **图表示**：变量关联图 VIG——每个变量一个顶点，同子句共现则连边（宽 w 子句对应 w-团，大宽度子句需先做 width reduction）。
- **HCS 分解**：在 VIG 上递归做 modularity 最大化的划分（hierarchical multiresolution 方法，底层用 Louvain 算法取顶层划分），得到一棵分解树；不可再分的节点称叶社区（leaf-community）。
- **参数族**：共 49 个特征（附录 A 给出完整清单），含基参数（numVars、numClauses、CVR、dvMean/dvVariance 等）与 HCS 参数（各层社区数/度/大小/深度/modularity/mergeability、rootInterEdges、lvl2InterEdges、leafCommunitySize 等）。
- **基准与求解器**：10 869 个实例，来自 SAT Competition 2016–2018 五个赛道（Agile、Verification、Crypto、Crafted、Random；另用 cnfgen 补造 crafted，用阈值 CVR 生成 3/5/7-CNF random；SHA-1/SHA-256 原像补 crypto；有界模型检验补 verification）。求解器统一为 MapleSAT，超时 5000 s，SHARCNET Broadwell 2.1 GHz。
- **三步实证方法**（Section 3 的方法论贡献）：
  1. 类别区分：多分类器判断参数能否把工业/随机/crafted 区分开；
  2. 难度相关：经验难度模型（EHM）回归预测求解时间；
  3. scaling 实验：用 HCS 生成器单独变动一个参数、固定其余，观察运行时间。
- **理论分析**：expander 嵌入论证 + 反例构造（附录 C）。

## 4. 主要结果（保留关键数字）

- **分类器（Section 5.2，Table 2）**：49 特征 + Random Forest，五分类（verification/agile/random/crafted/crypto）平均 balanced accuracy **0.996 ± 0.001**（SVM 结果相近），说明 HCS 参数足以刻画工业 vs 随机/crafted 的结构差异。
- **经验难度模型 EHM（Section 5.3，Table 2）**：Random Forest 回归预测 log(运行时间)，训练集 1 880 个实例（剔除超时与秒解实例），adjusted **R² = 0.848 ± 0.009**——远强于此前参数（modularity 等）。分赛道：agile **0.94**、crafted 0.85、random 0.81、verification 0.74、**crypto 0.48（最差，作者承认 crypto 为异常类，无参数族能解释）**。
- **Top-5 预测特征（Table 2）**：分类——rootMergeability、maxInterEdges/CommunitySize、cvr、leafCommunitySize、lvl2InterEdges/lvl2InterVars；回归——rootInterEdges、lvl2Mergeability、cvr、leafCommunitySize、lvl3Modularity。收敛到五类参数：mergeability 类、modularity 类、inter-community edge 类、CVR、leaf-community size。
- **rootInterEdges 的跨类 scaling（Section 5.4，Fig. 2，附录 B）**：工业类（verification/agile）根层社区间边数与变量数 n 近似线性增长但比例常数很小；random 3-CNF 的常数至少大一个数量级（5-CNF、7-CNF 分别大两、三个数量级）。
- **生成器 scaling（Section 5.5）**：固定其余 HCS 参数，单独增大 **leaf-community size、depth、community degree** 任一参数，都单调增大生成公式的求解难度 → 这三者是重点 HCS 难度参数。
- **综合判读（Section 5.6）**：工业实例 = 小叶社区、高 modularity、少社区间边；随机/crafted = 大叶社区、低 modularity、极多社区间边；与运行时间的相关性"远强于此前提出的任何参数"。
- **理论结果（Section 6）**：
  - **Theorem 1**：若图族的 HCS 满足——每个大小 ≥ Ω(f(n)) 的社区其社区间边数为 o(f(n))、深度 O(log n)，且 f(n) ∈ ω(poly log n) ∩ O(n)——则该图**不能包含大小为 f(n) 的 expander 作为子图**。由于 resolution 下界证明普遍依赖 expansion（Ben-Sasson–Wigderson），"好 HCS"因此堵住了对工业类公式做指数下界的标准通道。
  - **Theorem 2**：存在图（clique 环，Fortunato–Barthélemy 分辨率极限反例）其自然社区大小为 log n 且恰是 HCS 叶社区，而**扁平** modularity 最优划分只能给出 Θ(√(n/log³ n)) 的大社区——层级分解修复了 modularity 的分辨率极限。
  - **反例（附录 C）**：单独限制 root modularity、smooth modularity、bounded leaf size O(log n)、深度等任意子集，都仍能构造 resolution 复杂度 2^{Ω(n^ε)} 的难公式；只有**同时**限制叶社区大小 + 社区度 + 社区间边数（即 Theorem 1 的条件）才能排除可嵌入 expander。作者据此说明"为什么需要参数组合而非单一参数"。
- **HCS 生成器（贡献 5）**：输入 CVR、幂律参数、hierarchical degree、depth、leaf-community size、社区间边/变量密度、子句宽度，输出满足这些参数值的递归生成公式，可按需造"易/难"实例。

## 5. 与我们项目的关系

我们研究：**SAT 实例变量交互的局部性（半径参数 r）如何因果地决定求解难度**。

- **对 H1（结构指标解释难度）——强支撑，且是当前文献最强证据之一**。本文正是"结构指标 → 运行时间"这条相关路线的标杆：49 个结构特征 + 回归得到 adjusted R² = 0.85（Section 5.3，Table 2），且分类工业/随机准确率 99.6%（Section 5.2）。注意其口径与我们 H1 一致：相关关系，非因果。**同时给出警示**：crypto 类 R² 仅 0.48（Section 5.3），说明任何单一结构族都可能存在失效的实例类别——我们 H1 的评估应按实例类别/生成器分层报告，而不是只报总体拟合。
- **对 H2（匹配密度后，局部性半径对难度的因果效应）——方法论同构、可直接对比**。本文的"生成器 scaling 实验"（Section 5.5）是我们 H2 的前驱设计：用 HCS 生成器**固定其余参数、单独转动一个结构参数**，观察难度单调响应。差别在于：(a) 他们转的是层级社区参数（叶社区大小/深度/社区度），我们转的是显式半径 r；(b) 他们**未控制 mergeability**（Section 5.5 自述），因此其"因果"结论有混杂变量残留——这正是我们"匹配密度后识别因果效应"的改进空间；(c) 他们的结论方向是"社区越大/越深/社区度越大 → 越难"，可与我们的 r-难度剂量响应曲线方向性对比：大叶社区+少社区间边意味着变量交互被局限在局部（类似小 r），而他们观察到**小叶社区+少社区间边反而易解**——注意这与"局部性→难"的朴素预期方向相反，H2 实验设计时要明确区分"社区内局部性"与"跨社区耦合半径"两种口径。
- **对 H3（LLM 启发式成功率随局部性变化）——间接支撑**。本文证明结构参数可被机器学习模型用来预测/分类难度（Table 2），可视为"启发式（广义）成功率随结构变化"的先例；但其特征是全局图统计而非逐变量/逐区域的局部信息，尚无证据表明 LLM 类启发式能从局部邻域信息中获益。我们的 H3 相当于把"Random Forest + 49 全局特征"换成"LLM + 局部交互信息"，本文结果设定了需要打败的 baseline 强度。
- **理论接口**：Theorem 1 把"好 HCS（≈强局部性 + 弱跨社区耦合）"与"不可嵌入 expander（≈缺乏难度的标准来源）"联系起来。若我们的半径 r 参数在小 r 时推出类似 HCS 条件（少跨社区边），可用该定理给"小 r ⇒ 无 expander ⇒ 无经典指数下界通道"提供理论背书；附录 C 的反例提醒我们：局部性参数的任意子集都造得出难公式，故 r 单独不足以保证易解——H2 的预期可能应是非单调或条件性的。

## 6. 值得在 M2/M3 引用的具体结论（标注出处）

1. **M2（结构指标 ↔ 难度的相关性基线）**：引用 Section 5.3 + Table 2："基于 HCS 参数的 Random Forest 回归预测 MapleSAT 运行时间，adjusted R² = 0.848 ± 0.009；五特征为 rootInterEdges、lvl2Mergeability、cvr、leafCommunitySize、lvl3Modularity"。我们的结构指标回归应以此为文献对照线。
2. **M2（跨类别评估）**：引用 Section 5.3 的分赛道 R²（agile 0.94 / crafted 0.85 / random 0.81 / verification 0.74 / crypto 0.48）作为"结构指标解释力依类别而异"的证据，支持我们分层汇报。
3. **M2（工业 vs 随机的结构判别）**：引用 Section 5.2 + Table 2（balanced accuracy 0.996 ± 0.001）与 Section 5.4 + Fig. 2（rootInterEdges 随 n 线性增长但工业常数比 random 小 ≥1 个数量级）。
4. **M3（因果/干预实验设计模板）**：引用 Section 5.5 的生成器 scaling 方法学（固定其余参数、单参数扫描、难度单调响应）作为我们 r-scan 实验的对照设计；并引用其自述局限（未控制 mergeability、假设所有叶社区同大小同深度，Section 5.5）说明我们的"匹配密度后因果效应"设计相对其改进点。
5. **M3（理论预期）**：引用 Section 6 Theorem 1（好 HCS 条件下排除大小 f(n) 的 expander 子图）与 Theorem 2（HCS 修复 modularity 分辨率极限）；引用附录 C 反例集论证"单一局部性参数不足以保证易解"，以限定我们 H2 假设的陈述范围。
6. **M2/M3（基准与工具）**：引用其 10 869 实例五赛道基准构成（Section 5.1，Table 1）与 HCS 生成器（贡献 5，https://satcomplexity.github.io/hcs/），可作为我们 r-参数化生成器的对照生成器/外部效度来源。
