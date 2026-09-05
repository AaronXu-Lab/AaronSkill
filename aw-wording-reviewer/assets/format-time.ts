/**
 * 时间点显示的规范实现。
 *
 * 本文件同时是 aw-wording-reviewer 的时间点契约事实源和可复用实现。它只处理
 * 「某件事发生在何时」；Duration、Elapsed、Countdown 与 Recurrence 文案由各自
 * 的规则和 formatter 处理，不要混入这里。
 *
 * 无依赖、无框架绑定，可直接放进任意 TypeScript 项目。所有日历判断都使用运行
 * 环境的本地时区；昨天、前天、明天、后天与天数按自然日计算，不按连续 24 小时。
 */

export type TTimeDisplayMode = 'relative' | 'absolute'
export type TTimeValue = number | string | Date | null | undefined

/** 默认简体中文；用于其他语言时可以覆盖文案，不改变分档逻辑。 */
export interface ITimeDisplayLabels {
  /** 键为本地日历自然日差：-2、-1、1、2。 */
  dayOffsets: Record<number, string>
  justNow: string
  soon: string
  minutesAgo: (n: number) => string
  minutesLater: (n: number) => string
  daysAgo: (n: number) => string
  daysLater: (n: number) => string
  /** 时间值或显式传入的基准时间无效时的占位符。 */
  empty: string
}

export type TTimeDisplayLabelOverrides = Partial<Omit<ITimeDisplayLabels, 'dayOffsets'>> & {
  dayOffsets?: Partial<Record<number, string>>
}

export interface ITimeDisplayOptions {
  mode: TTimeDisplayMode
  /**
   * 是否在称谓、天数或日期后追加 HH:mm。默认 false。
   * 相对时间的秒、分钟和同日三个优先档不受此开关影响。
   */
  showExactTime?: boolean
  /** 用于判断相对距离、同日和同年的基准；省略时使用 Date.now()。 */
  baseTime?: TTimeValue
  labels?: TTimeDisplayLabelOverrides
}

const MINUTE = 60_000
const HOUR = 3_600_000
const DAY = 86_400_000

/** 数字与中文单位之间保留一个半角空格。 */
export const DEFAULT_TIME_LABELS: ITimeDisplayLabels = {
  dayOffsets: { [-2]: '前天', [-1]: '昨天', 1: '明天', 2: '后天' },
  justNow: '刚刚',
  soon: '马上',
  minutesAgo: (n) => `${n} 分钟前`,
  minutesLater: (n) => `${n} 分钟后`,
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

function sameLocalDay(targetTime: number, baseTime: number): boolean {
  return dateKey(targetTime) === dateKey(baseTime)
}

function sameLocalYear(targetTime: number, baseTime: number): boolean {
  return new Date(targetTime).getFullYear() === new Date(baseTime).getFullYear()
}

function clock(time: number): string {
  const date = new Date(time)
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function calendarDate(time: number, includeYear: boolean): string {
  const date = new Date(time)
  const monthAndDay = `${pad(date.getMonth() + 1)}/${pad(date.getDate())}`
  return includeYear ? `${date.getFullYear()}/${monthAndDay}` : monthAndDay
}

function appendClock(text: string, time: number, showExactTime: boolean): string {
  return showExactTime ? `${text} ${clock(time)}` : text
}

function resolveTime(value: TTimeValue): number | null {
  if (value === null || value === undefined) return null
  if (typeof value === 'number') return Number.isFinite(value) ? value : null
  if (value instanceof Date) {
    const time = value.getTime()
    return Number.isFinite(time) ? time : null
  }

  const trimmed = value.trim()
  if (!trimmed) return null

  // 无时区的日历字符串按本地时间解析，避免 `YYYY-MM-DD` 被当作 UTC 后跨日。
  const local = trimmed.match(
    /^(\d{4})[/-](\d{2})[/-](\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?$/,
  )
  if (local) {
    const [, year, month, day, hour = '0', minute = '0', second = '0'] = local
    const parsedYear = Number(year)
    const parsedMonth = Number(month)
    const parsedDay = Number(day)
    const parsedHour = Number(hour)
    const parsedMinute = Number(minute)
    const parsedSecond = Number(second)
    const date = new Date(
      parsedYear,
      parsedMonth - 1,
      parsedDay,
      parsedHour,
      parsedMinute,
      parsedSecond,
    )
    const valid =
      date.getFullYear() === parsedYear &&
      date.getMonth() === parsedMonth - 1 &&
      date.getDate() === parsedDay &&
      date.getHours() === parsedHour &&
      date.getMinutes() === parsedMinute &&
      date.getSeconds() === parsedSecond
    return valid ? date.getTime() : null
  }

  const time = new Date(trimmed).getTime()
  return Number.isFinite(time) ? time : null
}

function resolveLabels(overrides?: TTimeDisplayLabelOverrides): ITimeDisplayLabels {
  return {
    ...DEFAULT_TIME_LABELS,
    ...overrides,
    dayOffsets: { ...DEFAULT_TIME_LABELS.dayOffsets, ...overrides?.dayOffsets },
  }
}

/**
 * 相对时间按优先级首次命中即停止：秒 → 分钟 → 同日钟点 → 邻近日称谓 →
 * 3～6 个自然日 → 同年日期 → 跨年日期。
 */
function formatRelativeTimePoint(
  time: number,
  baseTime: number,
  showExactTime: boolean,
  labels: ITimeDisplayLabels,
): string {
  const diff = time - baseTime
  const absoluteDiff = Math.abs(diff)

  if (absoluteDiff < MINUTE) return diff > 0 ? labels.soon : labels.justNow

  if (absoluteDiff < HOUR) {
    const minutes = Math.floor(absoluteDiff / MINUTE)
    return diff < 0 ? labels.minutesAgo(minutes) : labels.minutesLater(minutes)
  }

  if (sameLocalDay(time, baseTime)) return clock(time)

  const dayDiff = calendarDayDiff(time, baseTime)
  if (Math.abs(dayDiff) <= 2) {
    return appendClock(labels.dayOffsets[dayDiff], time, showExactTime)
  }

  if (Math.abs(dayDiff) <= 6) {
    const dayText = dayDiff < 0 ? labels.daysAgo(Math.abs(dayDiff)) : labels.daysLater(dayDiff)
    return appendClock(dayText, time, showExactTime)
  }

  return appendClock(calendarDate(time, !sameLocalYear(time, baseTime)), time, showExactTime)
}

/** 绝对时间只有一套规则，过去与未来不分支。 */
function formatAbsoluteTimePoint(
  time: number,
  baseTime: number,
  showExactTime: boolean,
): string {
  if (sameLocalDay(time, baseTime)) {
    return showExactTime ? clock(time) : calendarDate(time, false)
  }

  return appendClock(calendarDate(time, !sameLocalYear(time, baseTime)), time, showExactTime)
}

/** 产品中的时间点统一经本函数输出，不要在页面里手写分档。 */
export function formatTimeDisplay(value: TTimeValue, options: ITimeDisplayOptions): string {
  const labels = resolveLabels(options.labels)
  const time = resolveTime(value)
  if (time === null) return labels.empty

  const baseTime = options.baseTime === undefined ? Date.now() : resolveTime(options.baseTime)
  if (baseTime === null) return labels.empty

  const showExactTime = options.showExactTime ?? false
  return options.mode === 'relative'
    ? formatRelativeTimePoint(time, baseTime, showExactTime, labels)
    : formatAbsoluteTimePoint(time, baseTime, showExactTime)
}

/** 周期任务的「下一次运行」固定使用相对时间，并显示可用的精确钟点。 */
export function formatNextRunTime(
  value: TTimeValue,
  baseTime: TTimeValue = Date.now(),
): string {
  return formatTimeDisplay(value, { mode: 'relative', showExactTime: true, baseTime })
}
