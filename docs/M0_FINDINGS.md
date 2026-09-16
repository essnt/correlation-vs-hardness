# M0 文献核查与新颖性定位——阶段性发现（第 1 轮）

日期：2026-09-09 ｜ 方法：Crossref / OpenAlex / DBLP 结构化 API + 网页检索交叉验证

## 一、引用验证总表

### 原始对话中的引用（第 1 轮对话已核，此处归档）

| 引用 | 验证结果 | 出处 |
|---|---|---|
| OpenAI 万 Agent 攻克 Navier-Stokes | ✅ 真（有争议） | openai.com/index/navier-stokes-solution/，2026-09，≈10000 Agent×88h，Lean 验证；Buckmaster 公开质疑 |
| Polynomial-Time Reasoning at the Edge of NP | ✅ 真 | Wang, Li, Deng, Wang, Wu, Ramachandran, Roth，ICLR 2026 投稿，openreview.net/forum?id=2yhCEYmeiP |
| 牛津 DNN 内置奥卡姆剃刀 | ✅ 真（对话日期有误） | Nature Communications 2025-01，doi:10.1038/s41467-024-54813-x（对话误作 2026-08） |

### 评审一中提出、本轮验证

| 引用 | 验证结果 | 出处 |
|---|---|---|
| Mull-Fremont-Seshia 社区硬度定理 | ✅ 真（全文已核） | On the Hardness of SAT with Community Structure，SAT 2016，Springer LNCS 9710（doi:10.1007/978-3-319-40970-2_10）；全文经 arXiv:1602.08620 ar5iv 版核验。核心：PCM 类社区度量（含 modularity）好 ⇒ 仍 NP-hard；CA 模型少社区 w.h.p. 指数消解证明；实验示社区规模（非公式规模）主导运行时间。精读笔记：papers/notes/mull2016_community_hardness.md |
| Zulkoski 结构度量研究 | ✅ 真 | **The Effect of Structural Measures and Merges on SAT Solver Performance**，Zulkoski, Martins, Wintersteeger, Liang, Czarnecki, Ganesh，**CP 2018**（LNCS 11008，DBLP conf/cp/ZulkoskiMWLCG18；此前记 LION 2018 系误记，LION 论文集为 LNCS 11331），doi:10.1007/978-3-319-98334-9_29。会议版无 OA（S2 CLOSED、Unpaywall False、无 arXiv 版）；全文以作者博士论文版核实（*Understanding and Enhancing CDCL-based SAT Solvers*, Waterloo 2018, UWSpace，PDF 存档 data/external/papers/zulkoski_thesis2018.pdf）。精读笔记：papers/notes/zulkoski2018_structural.md |
| HCS 层次社区结构 | ✅ 真 | Li et al., On the Hierarchical Community Structure of Practical Boolean Formulas，SAT 2021，Springer LNCS 12831, pp. 359–376（doi:10.1007/978-3-030-80223-3_25；arXiv:2103.14992） |
| KIT 2023 异质性 vs 几何局部性 | ✅ 真 | Bläsius, Friedrich, Göbel, Levy, Rothenberger, The impact of heterogeneity and geometry on the proof complexity of random satisfiability，**SODA 2021**（doi:10.1137/1.9781611976465.4，SIAM 官方 proceedings：2021 ACM-SIAM Symposium on Discrete Algorithms, pp.42-53, 2021-01；【2026-09-12 订正】旧记 SODA 2022 系误读 DBLP 键尾号 22 为年份——该尾号为消歧计数器）+ RSA 2023 期刊版（doi:10.1002/rsa.21168，63(4):885–941），一作 KIT |

### Bläsius et al.（RSA 2023）完整摘要关键结论

> "heterogeneity alone does not make SAT easy as heterogeneous random k-SAT instances have
> superpolynomial resolution size. This implies intractability of these instances for modern
> SAT-solvers. In contrast, modeling locality with underlying geometry leads to small
> unsatisfiable subformulas, which can be found within polynomial time."

即：(1) 异质性 ≠ 易解（超多项式消解规模）；(2) 几何局部性 ⇒ 多项式时间可发现的小
不可满足子公式。**这是 H2 最强的理论支撑——证明复杂度层面的定理，与我们的实证干预
形成"理论—实验"互补。**

## 二、撞车专查结果（M0-3）

Giráldez-Cru & Levy 线确实存在局部性生成器，两条：

1. **Locality in Random SAT Instances（IJCAI 2017，doi:10.24963/ijcai.2017/89）**
   摘要明确：基于 locality 的随机 SAT 生成器，且"first random SAT model that generates
   both scale-free structure and community structure at once"，并展示 CDCL 利用局部性。
   **全文精读结论（PDF 已入库 docs/papers/）**：其 "PS 模型" 基于 Papadopoulos et al. 2012
   的流行度×相似度机制（双曲几何隐空间）——流行度分量 r_s=log(s) **按构造产生幂律度分布**
   （幂指数 β=1+1/τ 模仿工业实例），相似度分量（随机角度 θ + 角距离）产生社区结构，
   Fermi-Dirac 温度 T 调节连接概率。**局部性与异质性在模型中本质耦合**，无 SAT/UNSAT
   可满足性控制，无内容/拓扑分解，难度报告为求解时间观察而非受控曲线。
2. **Popularity-similarity random SAT formulas（AIJ 2021，doi:10.1016/j.artint.2021.103537）**
   即上述 PS 模型的期刊扩展版（同一条线），IJCAI 2017 精读已实质覆盖。

前史补充：Markström, Locality and Hard SAT-Instances（JSAT 2006，doi:10.3233/sat190024）
——欧拉图构造的局部性硬实例，作历史引用。

### 新颖性重定位（收缩预案启动，非致命）

| 维度 | Giráldez-Cru & Levy 2017/2021 | Bläsius et al. 2021/2023 | 本项目 E3a |
|---|---|---|---|
| 局部性旋钮 | ✅（与异质性纠缠） | ✅（几何模型，理论） | ✅（**度分布锁死，纯拓扑**） |
| 可满足性控制 | ✗（随机 SAT/UNSAT 混杂） | ✗（随机模型） | ✅（诱骗解 σ，全 SAT） |
| 内容/拓扑正交分解（2×2） | ✗ | ✗ | ✅ |
| 度保持配对干预（E3b） | ✗ | ✗ | ✅ |
| 难度度量 | 求解时间观察 | 消解规模（证明复杂度定理） | 冲突数/运行时**经验曲线** + 相变扫描 |
| 中介分析 | ✗ | ✗ | ✅（结构→求解器行为→难度） |

**补充（全文精读笔记完成后，见 docs/papers/notes/，2026-09-09）**：
PS 模型的 **Fig. 3 是与 E3a 最近的单篇前驱结果**——固定 m/n=4.25 时难度随温度 T
（局部性旋钮）非单调：强局部易解、T≈1.5 最难、T=10 又变易。但其设计有四项局限，
恰为本项目差异化设计所针对：(1) 无 SAT 率/α_c(T) 控制——SAT 与 UNSAT 实例混杂，
难度曲线混入"距阈值距离"效应（我们 R3b 已证明该混杂可达数量级尺度）；(2) 无匹配 Δ
设计；(3) literal 度分布未锁定（参数上 β 与 T 可分离，但涌现结构随 T 的度分布变化
未受控）；(4) 无内容/拓扑 2×2 分解。行动项：M2 主扫描须主动检验我们的 r-难度曲线
在匹配 Δ 下是否同样非单调（其 CDCL 优势窗口在中等局部性区段的观察与我们的
r=0.15–0.3 中间带难度峰一致），并在论文中将 Fig. 3 作为直接对比基线引用。

**收缩后的新颖性主张**：首个"全条件受控的局部性**经验干预**"——在 n、α、度分布、
子句内容、σ-满足冗余度全部匹配下仅动 r，配 2×2 内容/拓扑分解与配对度保持随机化；
作为 Bläsius et al. 证明复杂度定理的**算法-经验层面对应实验**（理论说几何局部性可解，
我们测量现代求解器实际难度随 r 的完整相变曲线）。

## 三、对计划的更新

1. 理论脊柱新增：Bläsius et al. RSA 2023（H2 核心理论对应物，从"待确认"转正）。
2. 相关工作必须显著引用：Giráldez-Cru & Levy 2017、2021；Mull-Fremont-Seshia 2016；
   Markström 2006。论文叙事按上表重定位。
3. E3a 的度分布锁死设计从"方法论洁癖"升级为"核心差异化"——正是前人未能分离的维度。
4. 相关工作新增：Friedrich, Krohmer, Rothenberger, Sutton, Phase Transition for Scale-Free
   SAT Formulas（AAAI 2017）——无标度 SAT 的相变理论线（从 IJCAI 2017 参考文献中挖出）。

## 四、剩余 M0 任务

- [x] 全文精读队列：Giráldez-Cru IJCAI 2017（其 locality 参数的精确定义）、Bläsius RSA 2023
      （其几何模型定义，确认是否已有连续 r 旋钮及其实验部分）、AIJ 2021（补摘要）。
      ✅ 完成：notes/giraldez-cru-2017-locality.md、blasius2023_geometry.md、li-2021-hcs.md（2026-09-11 勾选订正）。
- [x] 理论脊柱其余引用结构化摘要（OGP/Weitz/Achlioptas-Coja-Oghlan/Atserias-Dalmau/
      Krzakala/Jia-Moore-Strain——先按已知知识写，标注"待全文核对"）。
      ✅ 完成：notes/ogp_phase_transitions.md（Gamarnik／Achlioptas–Coja-Oghlan／Krzakala）、
      notes/width_decay_barrier.md（Atserias–Dalmau／Weitz）、notes/jia2005_hiding.md（2026-09-11 勾选订正）。
- [x] 撰写《审计备忘录》（M0-5）。✅ docs/AUDIT_MEMO.md（2026-09-11 勾选订正）。
- [x] Go/No-Go 判定（M0-6）：当前趋势 **Go**（重定位后无致命撞车）。✅ 判定记录 docs/AUDIT_MEMO.md §五（2026-09-11 勾选订正）。
