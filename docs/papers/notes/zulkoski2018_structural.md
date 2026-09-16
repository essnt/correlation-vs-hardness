# 精读笔记：Zulkoski et al. —— 结构度量与 CDCL 求解性能（E5 baseline 方法学来源）

## 版本与来源定位
- 会议版：Zulkoski, Martins, Wintersteiger, Liang, Czarnecki, Ganesh.【2026-09-12 订正】本行旧记 Ganesh/Czarnecki 顺序颠倒，以 Crossref 与 DBLP 键 ZulkoskiMWLCG18 为准。
  *The Effect of Structural Measures and Merges on SAT Solver Performance*, CP 2018, LNCS 11008,
  DOI `10.1007/978-3-319-98334-9_29`（DBLP `conf/cp/ZulkoskiMWLCG18`；【2026-09-11 订正】旧列表误多列
  Robere——DBLP 键六首字母与 OpenAlex 核验均为 6 作者）。**无任何开放获取版本**
  （Semantic Scholar openAccessPdf=CLOSED；Unpaywall is_oa=False；无 arXiv 预印本——arXiv 站内搜索
  与作者名检索均无结果）。
- 本文所用全文：作者博士论文完整版（比会议版多出理论证明与附录数据）：
  Edward Zulkoski, *Understanding and Enhancing CDCL-based SAT Solvers*, PhD thesis, University of
  Waterloo, 2018. UWSpace bitstream `11122410-2f45-4281-a8ca-682f15448372`（145 页 PDF，
  已存档 `data/external/papers/zulkoski_thesis2018.pdf`）。会议版内容对应论文第 2.3.3、4、5 章；
  本笔记补充引用论文第 6 章（LSR backdoors）。
- 引用规范：正文引 CP 2018 会议版；方法细节（算法、逐类别数值表）可引论文版补充。

## 一、度量的精确定义（论文 Table 4.1 + §2.3.3，E5 特征工程依据）
所有实例先用 MapleCOMSPS 预处理器简化，再在简化后公式上计算度量（预处理时间不计入求解时间）。
除 backbones 外所有度量均为启发式近似值（多为上界），这一点必须写进我们的效度威胁清单：

| 度量 | 计算方法（论文所用工具） |
|---|---|
| Weak backdoor | tabu 局部搜索最小化最终模型中的决策数（Li & Van Beek 2011） |
| Backbone | 重复 SAT 调用 + UNSAT-core 剪枝（Janota et al. 2015） |
| Treewidth (TW) | 残余图启发式计算，最大团作上界（Mateescu 2011） |
| Modularity / Cmtys | Louvain 方法于 VIG（Newsham et al. 2014） |
| Fractal dim (DimV/DimC) | VIG/CVIG 的圆覆盖维数（Ansótegui et al. 2014） |
| 变量流行度 αV | 变量出现次数幂律分布指数（Ansótegui et al. 2009） |
| Resolvability R | 可解析对数：两子句存在互补文字 v∈c1 ∧ ¬v∈c2；公式值 = R/C² |
| Mergeability M | 可合并对数：resolvable 且另共享同极性文字 l∈c1∧l∈c2；一对合并 n 次计 n；公式值 = M/C² |
| LSR backdoor | LaSeR 工具：在 MapleSAT 上重跑并记录出现在证明子句中的变量（上界） |

M/R（mergeability/resolvability 比值）与 Q/Cmtys 为组合特征。

## 二、相关研究方法学（E5 baseline 的复刻规格）
- **语料**：SAT 竞赛 2009–2014 application+crafted 全部 + 2016 agile 轨 + 2007/2009 随机轨中
  MapleCOMSPS 5 分钟内可解的子集；共 6991 实例（逐度量 594–6991 不等，Table 4.2）。
- **依赖变量**：MapleCOMSPS（2016 main track 冠军）的 log(runtime)；超时 5000s（agile 60s）。
- **回归**：线性 + ridge（明言因特征多重共线性）；特征标准化（均值 0 方差 1）；
  ⊕ 记号 = 基特征 + 全部两两乘积交互；报告 adjusted R²。
- **分类**（复刻 Ansótegui et al. 2017）：Weka 默认参数，10-fold CV，随机森林/逻辑回归/IBk/K*。

## 三、核心结论："弱相关"的量化数字（我们论文引言与 baseline 预期直接引用）
1. **没有任何单一参数在异质实例全集上强预测求解时间**（§4.2.1 原文明言）。
2. 最佳 6 基特征组合的 adjusted R²（Table 4.3，linear，log time）：
   **Application ≈ 0.31，Crafted ≈ 0.56，Random ≈ 0.66，Agile ≈ 0.96**。
   异质来源（application）最难解释；agile 全来自 SAGE fuzzer 单一来源所以虚高。
   → 注意其口径警告：各回归所用实例子集不同（度量计算超时导致数据缺失），单元格不可直接互比。
3. **TW（树宽）特征在 application 上 R² 仅 0.05**（crafted 0.07、random 0.28）——
   拓扑结构度量的单独解释力在真实工业实例上几乎为零。这是"树宽≠难度"最直接的实证先例，
   与我们 E1 的发现（受控树宽变化下 unplanted 臂平坦）互相印证。
4. 子类别内部相关强但**符号跨类别翻转**：M/R 在 argumentation 上 Spearman +0.94，
   在 hardware-manolios 上 −0.73；hardware-*/planning/scheduling 几乎与所有度量不相关。
   混合后信号相消——解释了全集回归弱。
5. 与 Newsham et al. 2014（社区特征高 R²）的差异归因：(a) 他们未预简化（社区结构在
   冗余子句上计算）；(b) 他们把三类实例混在一个回归里。**方法学教训：预处理与语料分组
   是结构性度量的敏感性来源——我们 E5 必须双口径报告（预处理前/后）。**
6. 分类任务上度量很强（随机森林 90.9% 正确率；仅 dimVIG+dimCVIG 就 88.1%）：
   **度量能分类来源 ≠ 能解释难度**。这句对比适合写进我们论文的讨论节。

## 四、CDCL 搜索局部性的行为证据（我们"CDCL 机制中介"框架的实证支撑，§4.4）
- **空间局部性**：把每次分支决策记到其 VIG 社区，按社区规模归一后算 Gini 系数：
  VSIDS 0.52 / LRB 0.50 vs 随机分支 0.16（application 均值；agile 上 0.64/0.66 vs 0.18）。
  学习子句同样偏集（"Gini Clauses" 略低于 picks）。重启策略影响小。
- **时间局部性**：窗口 = 1% 社区数，LRB/VSIDS 有 45–55% 的决策落回最近选过的社区，
  随机分支仅 ~12%（Table 4.10/4.11，窗口 1/10/25 单调上升）。
- **Backbone**：application 平均 backbone 占 63% 变量；LRB+Luby 下 68% 学习子句被
  backbone 子sume（"做了本不必做的功"）；极性翻转率 Flips/B 表征求解器在 backbone
  文字上的犹豫。
- **对我们的意义**：CDCL 的决策/学习行为在真实实例上确实高度局部——这正是
  H2（局部性 r 因果地改变难度）的机制合理性来源：r 控制的是"变量交互的物理跨度"，
  而 CDCL 的搜索动力学被证明是"贴着社区走"的。中介路径 r → CDCL 行为 → 难度
  的第一环与第三环都有独立文献证据。

## 五、Chapter 5 mergeability 干预——与我们 E3b 同构的方法先例（重要）
- 构造：贪心极性翻转算法（Algorithm 2），递增可合并对数；**证明/论证保持**：V、C、
  VIG 全部社区结构性质（modularity）、变量/文字出现分布（popularity）、resolvability；
  **不保持**：可满足性、CVIG 上的社区结构。
- 结果（Table 5.2）：UNSAT 公式上 mergeability 与求解时间强负相关——power-law
  （"industrial-like"）系列 Spearman −0.97~−0.98（温度 T=2.5–100 稳定），随机 3-SAT
  n=200 −0.92；高 mergeability → 平均更短的学习子句。
- **与我们的关系（写论文时必须摆正）**：
  - 这是"对真实/随机公式做受控结构干预"的**同领域先例**：证明了我们 E3b
    （度保持随机化破坏局部性）这类操作是可行且被接受的实验范式，不是我们发明的
    无根据方法——引用它是加分的诚实，不是撞车。
  - 但干预对象正交：他们调"子句内容/文字重叠"（语义级），我们调"变量交互空间跨度"
    （拓扑级 r）。他们显式保持社区结构（VIG modularity），恰好说明其信号来自内容
    通道而非拓扑通道——**两篇合起来恰好拼出我们 2×2（拓扑×内容）分解的另一半**。
    我们的新颖性收缩表述（见 M0 撞车专查）应更新为：首个对"局部性半径 r"做受控
    干预扫描、并把拓扑/内容通道正交分解的实证研究；Zulkoski Ch5 是内容通道干预先例。
  - 他们不保 SAT 性（Example 2），靠 UNSAT 子集分析规避；我们 σ-保极性重采样
    恒保 SAT 性——这是我们的技术改进点，值得在 related work 中明确对比。
- 附：§5.2 给出均匀随机 k-SAT 可合并对数的期望值解析式（n, m, k 的函数）——
  若 E3a 的 geo_random 族出现 mergeability 协变量质疑，可用它做解析对照。

## 六、LSR backdoors（论文 Ch6；会议版不含）
- Definition 6：LS backdoor（Dilkina et al. 2009）允许重启的扩展——存在某探索顺序，
  CDCL 只在 B 上分支+叶端子求解器即可判定。学习方案敏感（LSR-1UIP 可指数小于
  LSR-DL）；加子句可能反而增大 LSR（非单调性）。LaSeR 算法算上界。
- 对我们：backdoor 族是"局部性"概念三分法中"解空间几何"一类的代表度量；
  E5 若加 LSR 特征成本高（3h/实例级），仅对 E4 落位子集可行。

## 七、效度威胁（其 §4.5，逐条对照我们自己的清单）
度量近似值（上界）；backdoor 类度量由求解器运行产生→与 runtime 变量可能引入伪相关
（他们用不同求解器缓解）；实例集依赖；随机实例样本小（他们预期加更多只会更差）；
单求解器族（MapleSAT/MapleCOMSPS/Lingeling，预期 MiniSat 系泛化）。
我们的对照：E3a 用受控生成器消除实例集混杂；度保持随机化配对设计消除"度量计算
方式"伪相关；双求解器（CaDiCaL+Glucose）检验泛化。

## 待办落地（状态同步 2026-09-10）
全部落地：E5 baseline 已按本规格实现并验证；related work 段与 M0 更新完成（2026-09-10）
