# 占位文案、数值与媒体

适用于界面需要假文案、假数字、假时间、假链接、假文件名或全局占位资源的情况。

- 写入占位字面量前，先检查 bundle 导出的 `FAKE_DATA` 中本次需要的语义字段；已有同语义字段时直接复用，不得在业务 `fake.ts`、store、view-model 或 JSX 中另造近义值。时间统一使用 `FAKE_DATA.date`、`FAKE_DATA.time` 或 `FAKE_DATA.datetime`，人物、组织、数值和通用 ID 同理。
- 确认缺少所需语义时按 [维护约定](maintenance.md) 处理全局字段与授权，不手改生成文件。演示源码按 [源码消费约定](code-demo.md) 复用 `FAKE_DATA.code`。
- 业务域的一组演示条目放在该域自己的 `fake.ts`，由该域的 data / view-model 消费；展示组件不得在 JSX、CSS 或页面数据中重复定义占位值。
- 业务域 `fake.ts` 只保存可替换内容，不承载 API、权限、store 或持久化逻辑。
- 假数据必须一眼可辨：域名使用 `example.com`，ID 使用 `*_00000042` 这类明显编号；一位数占位使用 `FAKE_DATA.smallNumber`（7），两位数及默认数值使用 `FAKE_DATA.number`（42）。不要编造看似真实的企业、人名、运行结果或错误原因。
- 不虚构倍数、可用性、节省时长或其他未经来源支持的指标；也不使用 lorem ipsum、feature one、sample content 或泛化 testimonial 作为填充内容，正文占位取 `FAKE_DATA.description` 或 `FAKE_DATA.article`。
- 用户可见占位内容使用中性的角色、序号或稳定空值，例如「当前用户」「成员 1」「账号 A」「—」；不要通过来源标签暴露它是假数据，也不要用具体真人、企业、账号或精确时间伪装成真实数据。
- 条目名称说明所覆盖的业务形态或边界，而不是说明其 fake 来源；覆盖有意义的差异，不堆同质样例。
