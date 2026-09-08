# 演示源码的唯一入口

## Canonical 资产与版本

- 事实源：[assets/code/conway.ts.txt](../assets/code/conway.ts.txt)。仅保存用户指定的完整 TypeScript 源码，不加 Markdown 围栏、说明、版权头或 managed 标记；`.txt` 后缀表明它不是运行模块。
- 索引：[fake-data.csv](fake-data.csv) 的 `code.source`（`source` 类型，值为相对 `assets/` 的 `code/conway.ts.txt`）与 `code.language`（`typescript`）。代码正文只在事实源维护，不复制进 CSV 或长文。
- 消费字段：`FAKE_DATA.code.source` 与 `FAKE_DATA.code.language`。项目生成的 `data.ts` 是可再生副本，不是第二份 canonical。
- 版本事实源：Skill 版本见 [入口元数据](../SKILL.md)；数据与 action 版本见 [version.ts](../assets/fake/version.ts)。本文不重复维护当前版本号。
- 保真基线：UTF-8，110 行，2080 字节，LF 换行，末尾保留一个 LF；SHA-256 为 `a39f560ee8544281b96eb0c88822472f563dc27e39c1b3cba58c7a23505b12e4`。指纹也由自检锁定，防止格式化或转义误改。

## 已有 bundle 的消费

只从项目声明的 bundle 目录入口导入，组件属性按项目真实 API 映射。以下仅展示接线，不重新定义展示源码：

```typescript
import { FAKE_DATA } from './fake'

const codePreview = {
  source: FAKE_DATA.code.source,
  language: FAKE_DATA.code.language,
}
```

普通、高亮、换行、不换行等适用展示项都复用 `codePreview.source` 或直接引用 `FAKE_DATA.code.source`。调整显示选项或容器宽度，不为各模式构造不同文本，不用 `slice`、`trim`、`repeat`、补空格或拼接制造长行。复制入口始终读取同一份完整原始字符串，不从高亮 DOM 反推源码。

渲染为文本节点，或使用接收文本并安全处理标记的高亮器；不把原始源码当 HTML 直接注入。不求值，不执行脚本，不作为可执行模块导入，也不放进可运行的沙箱预览。源码内的 `console.clear`、`setInterval` 和模拟逻辑必须仍只是字符。

## 尚无 bundle、仅需展示文本

有现成的 Gallery / 原型 fixture 入口时，在该边界内复用 canonical 资产，不为这项文字替换初始化 bundle。可按项目能力以原始文本加载器读取资产，或将资产逐字复制到该边界内的唯一文本文件，再由既有 fixture 统一导出；不要硬编码本机 Skill 绝对路径。

若项目已有 raw-text import 约定，可按其语法由 fixture 导出文本；没有加载器时，在构建期读取 UTF-8 文件并以安全字符串字面量生成唯一 fixture。以上都是**数据接入**，不是执行源码。同步时从 canonical 文件重新生成，不手改项目副本。

展示组件只依赖现有 fixture 入口，不在组件库生产代码中加入 fake action、计时器或运行模拟。交付说明该项目「未初始化 bundle；仅复用源码文本」，记录本次 canonical 数据版本与唯一导出字段，并核对消费字符串的 UTF-8 字节与上述指纹。

## 维护与验证

1. 非用户明确要求替换源码时，不修改 canonical 内容。真实产品实现、单元测试、用户明确指定的其他示例不受此默认规则限制。
2. `source` 类型只读 `assets/` 内 UTF-8 文本，不裁剪、格式化、转义解码、转换 HTML 实体、归一化 Unicode、替换换行或插入 `<br/>`。JSON 字符串转义只改变生成文件的表达形式，回读后的字符串必须与原资产相同。
3. 变更 canonical 数据时更新数据版本；变更 Skill 指令、脚本或测试时更新 Skill 版本和根 README。若用户明确更换源码，同步更新本文指纹与自检基线；不能只改指纹来掩盖非预期内容变化。
4. 修改 canonical 源码或生成链路时，按 [维护验证](maintenance.md#验证) 运行自检。仅项目端接入时检查消费结果，不要求重跑 Skill 全量回归。自检中的合成转义串不是供 UI 选用的另一份演示源码。
5. 项目端验证普通 / 高亮 / 软换行后传入文本和复制结果仍逐字一致，并检查没有模拟副作用。已有 bundle 还需 `--check`；仅 fixture 分支不要求 bundle 检查。
