/**
 * 时间点显示的规范实现。
 *
 * 本文件同时是 aw-wording-reviewer 的时间点契约事实源和可复用实现。它只处理
 * 「某件事发生在何时」；Duration、Elapsed、Countdown 与 Recurrence 文案由各自
 * 的规则和 formatter 处理，不要混入这里。
 *
 * 无依赖、无框架绑定，可直接放进任意 TypeScript 项目。所有日历判断都使用运行
 * 环境的本地时区；昨天、前天、明天、后天与天数按自然日计算，不按连续 24 小时。
 *
 * 相对时间措辞内置 zh-Hans、en、ja、ko 四套，通过 `locale` 选择，默认 zh-Hans；
 * 日期 `MM/DD`、`YYYY/MM/DD` 与 24 小时 `HH:mm` 不随语言变化。项目已有 i18n
 * 时用 `labels` 注入项目词条，覆盖同名内置措辞。
 */

export type TTimeDisplayMode = 'relative' | 'absolute'
export type TTimeValue = number | string | Date | null | undefined
export type TTimeLocale = 'zh-Hans' | 'en' | 'ja' | 'ko'

/** 相对时间各档的措辞；换语言只换措辞，不改变分档逻辑。 */
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
  /** 内置措辞的语言，默认 'zh-Hans'。 */
  locale?: TTimeLocale
  /** 覆盖所选 locale 的内置措辞，例如接入项目自身的 i18n 词条。 */
  labels?: TTimeDisplayLabelOverrides
}

const MINUTE = 60_000
const HOUR = 3_600_000
const DAY = 86_400_000

/**
 * 数字空格：zh-Hans、ja、en 在数字与单位之间保留一个半角空格；
 * ko 数字紧贴单位（`5분`），单位与「전 / 후」之间保留一个空格。
 */
export const TIME_LABELS: Record<TTimeLocale, ITimeDisplayLabels> = {
  'zh-Hans': {
    dayOffsets: { [-2]: '前天', [-1]: '昨天', 1: '明天', 2: '后天' },
    justNow: '刚刚',
    soon: '马上',
    minutesAgo: (n) => `${n} 分钟前`,
    minutesLater: (n) => `${n} 分钟后`,
    daysAgo: (n) => `${n} 天前`,
    daysLater: (n) => `${n} 天后`,
    empty: '—',
  },
  en: {
    dayOffsets: { [-2]: '2 days ago', [-1]: 'Yesterday', 1: 'Tomorrow', 2: 'In 2 days' },
    justNow: 'Just now',
    soon: 'In a moment',
    minutesAgo: (n) => `${n} min ago`,
    minutesLater: (n) => `In ${n} min`,
    daysAgo: (n) => `${n} ${n === 1 ? 'day' : 'days'} ago`,
    daysLater: (n) => `In ${n} ${n === 1 ? 'day' : 'days'}`,
    empty: '—',
  },
  ja: {
    dayOffsets: { [-2]: '一昨日', [-1]: '昨日', 1: '明日', 2: '明後日' },
    justNow: 'たった今',
    soon: 'まもなく',
    minutesAgo: (n) => `${n} 分前`,
    minutesLater: (n) => `${n} 分後`,
    daysAgo: (n) => `${n} 日前`,
    daysLater: (n) => `${n} 日後`,
    empty: '—',
  },
  ko: {
    dayOffsets: { [-2]: '그저께', [-1]: '어제', 1: '내일', 2: '모레' },
    justNow: '방금',
    soon: '곧',
    minutesAgo: (n) => `${n}분 전`,
    minutesLater: (n) => `${n}분 후`,
    daysAgo: (n) => `${n}일 전`,
    daysLater: (n) => `${n}일 후`,
    empty: '—',
  },
}

/** 默认 zh-Hans 措辞，保留旧导出名。 */
export const DEFAULT_TIME_LABELS: ITimeDisplayLabels = TIME_LABELS['zh-Hans']

function pad(value: number): string {
  return String(value).padStart(2, '0')
}

function dateKey(time: number): number {
  const date = new Date(time)
  const calendar = new Date(0)
  calendar.setUTCFullYear(date.getFullYear(), date.getMonth(), date.getDate())
  calendar.setUTCHours(0, 0, 0, 0)
  return calendar.getTime()
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
  return includeYear ? `${String(date.getFullYear()).padStart(4, '0')}/${monthAndDay}` : monthAndDay
}

function appendClock(text: string, time: number, showExactTime: boolean): string {
  return showExactTime ? `${text} ${clock(time)}` : text
}

function resolveTime(value: TTimeValue): number | null {
  if (value === null || value === undefined) return null
  if (typeof value === 'number') {
    const time = new Date(value).getTime()
    return Number.isFinite(time) ? time : null
  }
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
    // Date constructors map 0–99 to 1900–1999; restore the literal calendar year.
    if (parsedYear < 100) date.setFullYear(parsedYear)
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

function resolveLabels(
  locale: TTimeLocale = 'zh-Hans',
  overrides?: TTimeDisplayLabelOverrides,
): ITimeDisplayLabels {
  const base = TIME_LABELS[locale] ?? DEFAULT_TIME_LABELS
  return {
    ...base,
    ...overrides,
    // Partial 覆盖只写入提供的键，合并结果仍覆盖 -2、-1、1、2。
    dayOffsets: { ...base.dayOffsets, ...overrides?.dayOffsets } as ITimeDisplayLabels['dayOffsets'],
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
  const labels = resolveLabels(options.locale, options.labels)
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
  locale?: TTimeLocale,
): string {
  return formatTimeDisplay(value, { mode: 'relative', showExactTime: true, baseTime, locale })
}
