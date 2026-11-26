# 关联 Skill 检测与管理

按当前任务选择关联项。每项记录使用时机、来源、升级范围和缺失时可继续的工作。

## technical-writing

在审阅或改写 Docs 正文前，检查当前项目实际解析到的 `technical-writing/SKILL.md`。仅检查结构时可直接使用 Gallery 规则。

- 缺失时，提示用户通过[指定安装页](https://www.skills.sh/cursor/plugins/technical-writing)安装。页面提供的命令是 `npx skills add https://github.com/cursor/plugins --skill technical-writing`。先交付结构检查结果，暂缓具体措辞建议和改写。安装后重新检测，再继续正文工作。
- 已安装时，核对生效副本的安装范围及来源记录。来源为 `cursor/plugins` 时，在原安装范围内用 skills CLI 定向更新 `technical-writing`（支持命名更新的版本使用 `npx skills update technical-writing`，全局安装按 CLI 对应选项指定范围）。有新版直接升级，无需再次确认。更新后重新读取生效的 SKILL.md；同一任务可复用本次结果。
- 来源无法核实或不匹配时，提示用户核对来源，避免覆盖同名副本。升级检查失败时说明具体原因；已有可读的指定来源副本可继续用于正文，并标明更新状态待确认。
