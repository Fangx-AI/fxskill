# SEO、GEO 与转化

## 先判断问题分支

先使用已有上下文，判断当前问题主要是未收录、排名与点击、AI 引用，还是最终转化。缺失信息会改变分支时，只追问其中影响最大的一个；其余使用明确假设或条件分支继续。最多一个问题。不要同时展开所有分支。

## SEO 与 GEO 的共享基础

SEO 与 GEO 共享基础，并不冲突：

- 需要公开传播的页面可被目标搜索引擎和 AI 抓取系统访问；登录内容、隐私数据和不希望公开的页面仍应正确限制。
- canonical、重定向、站点地图和内部链接指向一致的首选 URL。
- 页面解决真实需求，内容准确、原创并及时更新。
- 品牌、产品、作者、组织和地点等实体在站内外保持一致。
- 关键观点有可核验的数据、案例和来源，而不是只有结论。
- 合并或更新重复、过时、相互冲突的页面，避免让系统和用户猜哪个版本可信。

SEO 是 SEO 与 GEO 的共同基础；GEO 另有 AI 发现、理解、引用和归因方面的诊断。两者不是先后互斥的两套工作，也不需要重复制作两套近似内容。

## SEO 分支

目标是让合适页面被收录、出现在合适查询中，并获得点击和转化。按以下顺序判断：

1. 在 Google Search Console、Bing Webmaster Tools 或目标搜索引擎工具中检查抓取与索引；先排除 `robots.txt`、`noindex`、错误 canonical、重定向和站点地图问题。
2. 对齐搜索意图、标题、摘要、正文和内部链接；页面必须真正回答该查询，而不是只放关键词。
3. 检查页面体验、移动端、性能、适用的结构化数据和重复 URL。结构化数据要与可见内容一致，不保证获得增强展示。
4. 联合查看展示、点击、查询、落地页和业务转化，不只看单个关键词排名。

## GEO 与大模型引用分支

目标是让内容更容易被 AI 理解、选择、引用并正确归因。按以下顺序判断：

1. 按训练抓取与回答检索两个维度审计页面的发现和引用情况。
2. 把优先页面改写成一个具体问题的完整答案。
3. 标明关键内容涉及的实体、时间、适用范围和限制。
4. 为关键说法补充原始数据或可靠出处。
5. 使用前核验 Bing Webmaster Tools 等当前能力的指标、覆盖范围和预览限制。2026-07-13 核验时，Bing 已在 AI Performance 基础上以全球逐步推出的 preview 形式增加 Intents、Topics、Citation Share 和 Compare；分类标签、覆盖和精度仍可能变化，Citation Share 也不是排名或流量份额。
6. 统一官网、行业资料和其他可信来源中的品牌事实。

不保证进入 AI 答案。

## 数据与转化

- 先定义业务动作，例如联系、注册、首次成功、付费、续费或复购，再决定事件和漏斗。
- 只收集决策所需的数据，并明确保留期、访问权限、删除方式和负责人。
- 选型前先确认用户与业务所在法域、需要的同意机制、数据处理/存储地区和跨境条件，再结合团队维护能力判断。
- Google Analytics、Plausible、Umami 和 Matomo 只是比较候选池。具体推荐最多两个主要候选和一个备选，并分别说明适用条件、主要成本和限制；不能把四个名称一次列为推荐结果。
- 需求简单、希望少收集时，可优先比较隐私友好的统计方案，但“隐私友好”不等于自动合规；实际收集字段、配置、同意、告知、保留和跨境安排仍需按适用规则核验。自行部署统计工具也会带来更新、备份和安全责任。
- 区分搜索点击、AI 引用、无点击曝光、直接访问和最终转化。平台没有提供的数据要标为未知，不把直接访问全部归因于 AI。

## 输出方式

固定使用一个题为“判断”的纯描述区和一个题为“优先动作”的唯一行动区。“判断”只说明属于未收录、排名与点击、AI 引用或转化中的哪一类、SEO 与 GEO 的共同基础及当前差距；可以写“SEO 是共同基础”，不得写“应先”“再做”或其他未来操作。“优先动作”只给当前分支最重要的三个动作，每项只有一个主要谓语；不能把改写、直接回答、标明实体/时间/范围/限制或补充来源合并为一项。行动区之后不追加判断或操作。

共享基础只说明一次，不重复两套清单；不承诺排名、收录、点击、转化或 AI 引用结果。只解释和推荐，不代用户提交 URL、修改抓取规则或接入分析脚本。`llms.txt`、Schema 或其他搜索产品能力只有在紧邻推荐当日核验的官方来源时才可写入输出，否则删除。

```markdown
**判断**
[纯描述分类、共同基础、当前差距及影响。]

**优先动作**
- [一个原子动作。]
```

搜索与 AI 产品能力变化快，引用前按 [source-policy.md](source-policy.md) 重新核验。官方核验入口（2026-07-13）：

- Google：[Google Search Central](https://developers.google.com/search)、[Google Search Console](https://search.google.com/search-console/about)。
- Bing：[Bing Webmaster Tools](https://www.bing.com/webmasters/about)、[AI Performance 2026-06 能力更新](https://blogs.bing.com/search/June-2026/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare)、[IndexNow](https://www.indexnow.org/documentation)。
- 结构化数据：[Schema.org](https://schema.org/docs/documents.html)。
- AI 发布者与爬虫说明：按目标平台查当前官方文档，例如 [OpenAI 发布者 FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)，不要套用一个平台的规则回答全部 AI 搜索。
- 分析产品：[Google Analytics](https://developers.google.com/analytics)、[Plausible](https://plausible.io/docs)、[Umami](https://docs.umami.is/docs)、[Matomo](https://matomo.org/guide/)。
