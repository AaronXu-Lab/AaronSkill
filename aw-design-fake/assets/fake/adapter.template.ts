// 项目自有适配层：aw-design-fake 只在初始化时创建本文件，之后不再覆盖，可以自由修改。
// 把下面两个函数接到项目真实的提示组件与静态资源上。

/** fake bundle 用到的逻辑资源名 → 项目实际的资源文件。 */
const ASSET_FILES: Record<string, string> = {}

/** 未实现功能的统一占位提示，接项目的 toast / sonner 组件。 */
export function notify(notice: { title: string; description: string; actionLabel: string }) {
  console.warn(`[fake] ${notice.title} — ${notice.description}`)
}

/** 把逻辑资源名解析成可访问 URL，接项目的静态资源工具。 */
export function assetUrl(name: string) {
  return `/${ASSET_FILES[name] ?? name}`
}
