# 测试与上线质量

## 测试顺序

先使用已有上下文；缺失信息会改变风险排序时，只追问其中影响最大的一个；其余使用明确假设或条件分支继续。最多一个问题。先过条件式风险门槛：

- 存在支付时，先验证成功、失败、取消、重复提交、异步回调、退款和订阅状态变化，确认页面、订单、支付平台与权益状态一致。
- 存在用户权限或私密数据时，先验证服务端授权，确认用户不能读取或修改无权访问的数据。
- 存在数据库、文件或其他持久化数据时，先做实际恢复验证，确认备份能够恢复到可接受的时间点。

没有这些能力，或风险门槛通过后，再按以下顺序检查：

1. 核心流程：注册、登录、找回密码、购买、退款、上传和主要功能。先确认用户能完成任务，也能从失败中恢复。
2. 安全补充：检查账号、权限、密钥、输入、上传、依赖和后台入口。自动扫描只能提供线索，不能证明安全。
3. 移动端与兼容性：优先用真实手机检查主流浏览器、键盘和触控，再补足目标用户需要的组合。
4. 性能：在真实页面和真实设备上检查加载、交互和布局稳定，覆盖关键流程，而不只测首页。

不要先追 Lighthouse 满分，再测试用户能否付款或找回账号。支付、权限和数据丢失风险高于装饰性问题和单次跑分。

## 上线最低检查

- 每个用户只能访问其角色和资源范围内有权限的数据；不能只验证菜单是否隐藏，还要验证服务端拒绝越权请求。
- 密钥不出现在前端包、代码仓库或公开日志中，并具备轮换方法。
- 支付结果以服务端验证和可信回调为准，不能以跳转页面或前端参数直接发放权益。
- 关键写操作具备幂等或重复提交保护，尤其是下单、扣款、退款、发信和创建资源。
- 错误信息清楚、可恢复且不泄露密钥、内部路径、堆栈、用户数据或权限细节。
- 数据库和文件都有可恢复的备份；“已开启备份”不等于“能够恢复”。
- 404、500、空状态、慢网络和无 JavaScript 时有合理结果；无法继续时应说明状态和下一步，而不是空白或无限加载。

这些是最低检查，不是上线后必然安全、无故障或达到某个性能分数的保证。

## 工具方向

- 性能：Lighthouse 适合本地诊断，PageSpeed Insights 适合对照实验室与可用的真实用户数据，WebPageTest 适合控制页面、地点、浏览器和网络条件。记录测试条件，不把一次结果当结论。
- 兼容性：真实设备优先；自有设备覆盖不足时，再比较 BrowserStack 等云真机服务，并按目标用户的设备与浏览器选择范围。
- 安全：用 OWASP Top 10 识别常见风险，用 ASVS 形成较完整的验证要求；Mozilla Observatory 和 Security Headers 只能检查部分外部配置，不能代表整站安全。
- 风险控制：按滥用概率和损失判断是否需要限流、验证码、WAF、上传类型/大小限制和告警，不默认购买昂贵产品。
- 无障碍：结合 Accessibility Tree、仅键盘操作、axe 和 WAVE。自动工具无法判断全部语义、焦点顺序、提示可理解性和真实辅助技术体验，必须人工检查关键流程。

## Core Web Vitals

使用 LCP、INP、CLS 观察加载、交互响应和布局稳定。优先结合真实用户数据、页面目标与关键流程定位问题，再用实验室测试复现；真实用户数据不足时，要明确数据缺口。

引用分数或指标时写明时间、设备、地区和页面，必要时补充网络、登录状态与工具版本。分数不能等同于用户体验，更不能等同于安全；优化也不承诺达到固定分数。

## 输出方式

先指出当前最高风险，再按风险给最多三个检查项。默认优先级是支付、权限、数据丢失；没有这些能力时，再转向核心流程、兼容性、无障碍或性能。每项说明要检查什么、失败意味着什么，以及需要用户返回的证据，不倾倒完整清单。只解释检查与修复方向，不代用户运行扫描、触发支付或修改生产配置。

具体工具与易变能力遵循 [source-policy.md](source-policy.md)。官方核验入口（2026-07-13）：

- 性能：[Lighthouse](https://developer.chrome.com/docs/lighthouse/overview)、[PageSpeed Insights 说明](https://developers.google.com/speed/docs/insights/v5/about)、[WebPageTest](https://www.webpagetest.org/)、[Core Web Vitals](https://web.dev/articles/vitals)。
- 兼容性：[BrowserStack Live 文档](https://www.browserstack.com/docs/live/get-started/test-websites)。
- 安全：[OWASP Top 10](https://owasp.org/www-project-top-ten/)、[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)、[Mozilla Observatory](https://developer.mozilla.org/en-US/observatory)、[Security Headers](https://securityheaders.com/)。
- 无障碍：[Chrome Accessibility Reference](https://developer.chrome.com/docs/devtools/accessibility/reference/)、[axe](https://www.deque.com/axe/)、[WAVE](https://wave.webaim.org/)。
