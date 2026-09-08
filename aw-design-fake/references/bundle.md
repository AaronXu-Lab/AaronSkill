# Bundle 接入与同步

只在初始化、同步或处理异常状态时读取。常规接入先运行 `--check`：

| 状态 | 修改模式下的处理 |
| --- | --- |
| `current` | 直接复用，确认本次所需 adapter 接线可用。 |
| 未初始化 | 沿用已明确共享目录，按下节初始化。 |
| `missing` / `outdated` / `drifted` | 同一命令将 `--check` 换成 `--write`，检查备份和项目扩展。 |
| `newer` | 不降级、不补写文件；检查公开接口，兼容则复用并记录，不兼容则报告缺口。仅在已授权维护 Skill 时合并通用变更，不能回灌项目专有代码。 |

仅审查不执行 `--init` / `--write`。参数或 canonical 数据无效时修复输入；重复标记或版本不能唯一解析时先定位，不能猜测覆盖。中途 I/O 故障可能留下部分同步，核对实际文件与备份后重跑检查，不虚报事务回滚。

## 未初始化

项目还没有 fake bundle 时，使用会话或项目约定中已经明确的共享目标目录；只有目录仍缺失时才询问。目录放在原型工作区共享层，不放进业务页面目录；随后初始化：

```bash
node <本 SKILL 目录>/scripts/fake-bundle.mjs --project-root <项目根目录> --init --target <相对项目根的目录>
```

初始化会写入 `<项目根目录>/.aw-design-fake.json` 记录 `target`，并生成：

```text
<target>/
├── data.ts       # 受管：全局 FAKE_DATA，由 CSV、长文与源码文本生成
├── actions.ts    # 受管：showFakeSonner 等通用 fake action
├── version.ts    # 受管：FAKE_DATA_VERSION 与 FAKE_LOGIC_VERSION
├── index.ts      # 受管：统一导出
└── adapter.ts    # 项目自有：只在缺失时创建一次，之后永不覆盖
```

`adapter.ts` 是唯一的项目耦合点，由执行者在授权范围内接上项目实现后才算完成初始化；模板存在或 `current` 不等于接线已验证：

- `notify(notice)`：把 `{ title, description, actionLabel }` 交给项目真实的 toast / sonner 组件。
- `assetUrl(path)`：把静态资源相对路径转成项目的可访问 URL。

## 同步与文件保护

- 所有调用方只从 bundle 目录入口导入，不直接依赖 `data.ts`、`actions.ts` 或 `version.ts`，也不创建 `fake-main.ts`、`fake-sonner.ts` 这类平铺入口。
- 受管文件由 Skill 资产生成，项目侧不手改。内容不足时按 [维护约定](maintenance.md) 核对全局维护授权与版本要求。
- 同步只替换 `aw-design-fake:managed-start` / `aw-design-fake:managed-end` 之间的内容，保留项目在标记之外的注释和扩展。
- 目标文件缺少有效 managed 标记时，`--write` 会先创建同名 `.aw-design-fake-backup` 再写入；已有备份不会覆盖，新备份加数字后缀。完成后必须检查备份里的项目扩展并按需迁回标记之外，不能静默丢弃。
- 写入前校验参数与项目内相对目标路径，拒绝根目录、越界、符号链接和静默迁移已有 target。重复 managed 标记或不能唯一解析的项目版本必须先定位，不猜测覆盖；中途 I/O 故障需检查实际状态后再同步。
- 同版本但 managed block 不同视为 `drifted`，以 SKILL 为准同步；项目版本高于 SKILL 时视为 `newer`，脚本不会自动覆盖。
