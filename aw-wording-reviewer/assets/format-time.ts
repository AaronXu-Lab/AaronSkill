/**
 * 日期时间显示的规范实现。
 *
 * 本文件是 aw-wording-reviewer 的内置资产，同时充当两个角色：
 *
 * 1. **格式契约的事实源**。审查日期文案时按本文件判定，不需要读目标项目的实现。
 * 2. **可迁移的实现**。目标项目缺少统一时间格式化器时，经用户许可后可整份复制进去，
 *    再把散落的手写格式替换为 `formatTimeDisplay`。
 *
 * 无依赖、无框架绑定，可直接放进任意 TypeScript 项目。
 *
 * 三种模式对应用户要回答的两类问题——「距离基准时间多久」与「具体何时发生」：
 *
 * - `relative`  以时间距离描述，如「刚刚」「3 分钟前」。用于用户首先关心新旧与是否
 *               需要立即处理的场景（消息列表、活动动态）。不单独承担精确引用。
 * - `absolute`  以固定日历时间标记，如「2026-07-31 14:30」。显示结果不随查看时刻
 *               变化，用于需要准确定位、跨人沟通、回溯复核的场景（交易记录、审计日志）。
 * - `hybrid`    邻近基准时间时用自然日称谓「昨天 14:30」，超出前天至后天的窗口后
 *               切换为绝对日期「07-28」。通用记录的默认候选。
 *
 * 同一信息流中的同类时间点必须使用同一模式，不按页面局部偏好变化。
 */

export type TTimeDisplayMode = 'relative' | 'absolute' | 'hybrid'
export type TTimePrecision = 'auto' | 'day' | 'time'
export type TTimeValue = number | string | Date

/** 自然日称谓与相对时长的文案。默认简体中文，可覆盖以适配其他语言。 */
export interface ITimeDisplayLabels {
  /** 相对基准时间的自然日称谓，键为日期差（-2 到 2）。 */
  dayOffsets: Record<number, string>
  justNow: string
  soon: string
  minutesAgo: (n: number) => string
  minutesLater: (n: number) => string
  hoursAgo: (n: number) => string
  hoursLater: (n: number) => string
  daysAgo: (n: number) => string
  daysLater: (n: number) => string
  /** 时间不可用时的占位符。 */
  empty: string
}

export interface ITimeDisplayOptions {
  mode: TTimeDisplayMode
  precision: TTimePrecision
  /** `relative` 与 `hybrid` 模式必填，缺失时返回占位符。 */
  baseTime?: number
  /** 默认 24 小时制。12 小时制应来自用户偏好，不要在文案里硬写。 */
  hour12?: boolean
  labels?: Partial<ITimeDisplayLabels>
}

const MINUTE = 60_000
const HOUR = 3_600_000
const DAY = 86_400_000

/**
 * 数字与中文单位之间保留一个半角空格（「3 分钟前」而不是「3分钟前」），
 * 与中英混排的空格规则一致。
 */
export const DEFAULT_TIME_LABELS: ITimeDisplayLabels = {
  dayOffsets: { [-2]: '前天', [-1]: '昨天', 0: '今天', 1: '明天', 2: '后天' },
  justNow: '刚刚',
  soon: '即将',
  minutesAgo: (n) => `${n} 分钟前`,
  minutesLater: (n) => `${n} 分钟后`,
  hoursAgo: (n) => `${n} 小时前`,
  hoursLater: (n) => `${n} 小时后`,
  daysAgo: (n) => `${n} 天前`,
  daysLater: (n) => `${n} 天后`,
  empty: '—',
}

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function dateKey(time: number): number {
  const date = new Date(time)
  return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())
}

function calendarDayDiff(targetTime: number, baseTime: number): number {
  return Math.round((dateKey(targetTime) - dateKey(baseTime)) / DAY)
}

/** 24 小时制补零；12 小时制仅在用户偏好开启时使用。 */
function clock(time: number, hour12: boolean): string {
  const date = new Date(time)
  if (!hour12) return `${pad(date.getHours())}:${pad(date.getMinutes())}`

  const hours = date.getHours()
  const period = hours < 12 ? 'AM' : 'PM'
  return `${hours % 12 || 12}:${pad(date.getMinutes())} ${period}`
}

function resolveTime(value: TTimeValue): number | null {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null
  if (value instanceof Date) {
    const time = value.getTime()
    return Number.isFinite(time) ? time : null
  }

  const trimmed = value.trim()
  if (!trimmed) return null
  // 'YYYY-MM-DD HH:mm' 在部分运行时不被 Date 解析，补成 ISO 形态。
  const normalized = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?$/.test(trimmed)
    ? trimmed.replace(' ', 'T')
    : trimmed
  const time = new Date(normalized).getTime()
  return Number.isFinite(time) ? time : null
}

function relativeDayText(dayDiff: number, labels: ITimeDisplayLabels): string {
  const nearLabel = labels.dayOffsets[dayDiff]
  if (nearLabel) return nearLabel
  return dayDiff < 0 ? labels.daysAgo(Math.abs(dayDiff)) : labels.daysLater(dayDiff)
}

/** 绝对日期：`YYYY-MM-DD`，需要钟点时追加一个半角空格与 `HH:mm`。 */
function formatAbsoluteDate(time: number, includeTime: boolean, hour12: boolean): string {
  const date = new Date(time)
  const day = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  return includeTime ? `${day} ${clock(time, hour12)}` : day
}

/** 融合日期：同年省略年份写作 `MM-DD`，跨年补全为 `YYYY-MM-DD`。 */
function formatHybridDate(
  time: number,
  baseTime: number,
  includeTime: boolean,
  hour12: boolean,
): string {
  const date = new Date(time)
  const base = new Date(baseTime)
  const dateText =
    date.getFullYear() === base.getFullYear()
      ? `${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
      : `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  return includeTime ? `${dateText} ${clock(time, hour12)}` : dateText
}

function formatRelativeTime(
  time: number,
  baseTime: number,
  hour12: boolean,
  labels: ITimeDisplayLabels,
): string {
  const dayDiff = calendarDayDiff(time, baseTime)
  if (dayDiff !== 0) return `${relativeDayText(dayDiff, labels)} ${clock(time, hour12)}`

  const diff = time - baseTime
  const absoluteDiff = Math.abs(diff)
  if (absoluteDiff < MINUTE) return diff > 0 ? labels.soon : labels.justNow

  const ago = diff < 0
  if (absoluteDiff < HOUR) {
    const minutes = Math.max(1, Math.floor(absoluteDiff / MINUTE))
    return ago ? labels.minutesAgo(minutes) : labels.minutesLater(minutes)
  }
  const hours = Math.max(1, Math.floor(absoluteDiff / HOUR))
  return ago ? labels.hoursAgo(hours) : labels.hoursLater(hours)
}

/** 产品中所有时间戳都应经本函数输出，不要在页面里手写格式。 */
export function formatTimeDisplay(value: TTimeValue, options: ITimeDisplayOptions): string {
  const { mode, precision, hour12 = false } = options
  const labels: ITimeDisplayLabels = { ...DEFAULT_TIME_LABELS, ...options.labels }

  if ((mode === 'relative' || mode === 'hybrid') && !Number.isFinite(options.baseTime)) {
    return labels.empty
  }
  const baseTime = options.baseTime ?? Date.now()
  const time = resolveTime(value)
  if (time === null) return labels.empty

  if (mode === 'absolute') {
    return formatAbsoluteDate(time, precision === 'time', hour12)
  }

  const dayDiff = calendarDayDiff(time, baseTime)
  if (mode === 'relative') {
    if (precision === 'day') return relativeDayText(dayDiff, labels)
    return formatRelativeTime(time, baseTime, hour12, labels)
  }

  if (Math.abs(dayDiff) <= 2) {
    const dayText = relativeDayText(dayDiff, labels)
    return precision === 'day' ? dayText : `${dayText} ${clock(time, hour12)}`
  }

  return formatHybridDate(time, baseTime, precision === 'time', hour12)
}

/** 活动记录时间戳：近处显示钟点，远处收敛为日期。 */
export function formatHistoryTime(time: number, hour12 = false, now: number = Date.now()): string {
  if (!time) return ''
  return formatTimeDisplay(time, { mode: 'hybrid', precision: 'auto', baseTime: now, hour12 })
}

/** 消息时间戳：始终保留具体钟点。 */
export function formatMessageTime(time: number, hour12 = false, now: number = Date.now()): string {
  if (!time) return ''
  return formatTimeDisplay(time, { mode: 'hybrid', precision: 'time', baseTime: now, hour12 })
}
