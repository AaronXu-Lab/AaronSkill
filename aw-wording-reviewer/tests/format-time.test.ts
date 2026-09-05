import assert from 'node:assert/strict'
import test from 'node:test'

import { formatNextRunTime, formatTimeDisplay } from '../assets/format-time.ts'

const MINUTE = 60_000
const HOUR = 3_600_000

function localTime(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
  second = 0,
  millisecond = 0,
): number {
  return new Date(year, month - 1, day, hour, minute, second, millisecond).getTime()
}

test('relative boundaries stop at the first matching tier', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)

  assert.equal(formatTimeDisplay(baseTime, { mode: 'relative', baseTime }), '刚刚')
  assert.equal(formatTimeDisplay(baseTime - 59_999, { mode: 'relative', baseTime }), '刚刚')
  assert.equal(formatTimeDisplay(baseTime + 59_999, { mode: 'relative', baseTime }), '马上')
  assert.equal(formatTimeDisplay(baseTime - MINUTE, { mode: 'relative', baseTime }), '1 分钟前')
  assert.equal(formatTimeDisplay(baseTime + MINUTE, { mode: 'relative', baseTime }), '1 分钟后')
  assert.equal(
    formatTimeDisplay(baseTime + HOUR - 1, { mode: 'relative', baseTime }),
    '59 分钟后',
  )
  assert.equal(formatTimeDisplay(baseTime + HOUR, { mode: 'relative', baseTime }), '13:00')
})

test('natural-day tiers use local calendar days instead of continuous 24-hour windows', () => {
  const baseTime = localTime(2026, 7, 15, 1, 30)
  const yesterday = localTime(2026, 7, 14, 23, 30)

  assert.equal(formatTimeDisplay(yesterday, { mode: 'relative', baseTime }), '昨天')
  assert.equal(
    formatTimeDisplay(yesterday, { mode: 'relative', showExactTime: true, baseTime }),
    '昨天 23:30',
  )
  assert.equal(
    formatTimeDisplay(localTime(2026, 7, 13, 23, 30), { mode: 'relative', baseTime }),
    '前天',
  )
  assert.equal(
    formatTimeDisplay(localTime(2026, 7, 16, 3, 30), { mode: 'relative', baseTime }),
    '明天',
  )
  assert.equal(
    formatTimeDisplay(localTime(2026, 7, 17, 3, 30), { mode: 'relative', baseTime }),
    '后天',
  )

  const threeDaysLater = localTime(2026, 7, 18, 8, 5)
  const sixDaysAgo = localTime(2026, 7, 9, 8, 5)
  assert.equal(formatTimeDisplay(threeDaysLater, { mode: 'relative', baseTime }), '3 天后')
  assert.equal(
    formatTimeDisplay(threeDaysLater, { mode: 'relative', showExactTime: true, baseTime }),
    '3 天后 08:05',
  )
  assert.equal(formatTimeDisplay(sixDaysAgo, { mode: 'relative', baseTime }), '6 天前')
})

test('relative dates switch at seven natural days and include the year only across years', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)

  assert.equal(
    formatTimeDisplay(localTime(2026, 7, 8, 9, 5), { mode: 'relative', baseTime }),
    '07/08',
  )
  assert.equal(
    formatTimeDisplay(localTime(2026, 7, 8, 9, 5), {
      mode: 'relative',
      showExactTime: true,
      baseTime,
    }),
    '07/08 09:05',
  )
  assert.equal(
    formatTimeDisplay(localTime(2025, 12, 20, 9, 5), { mode: 'relative', baseTime }),
    '2025/12/20',
  )
  assert.equal(
    formatTimeDisplay(localTime(2027, 1, 20, 9, 5), {
      mode: 'relative',
      showExactTime: true,
      baseTime,
    }),
    '2027/01/20 09:05',
  )
})

test('showExactTime does not affect the first three relative tiers', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)
  const values = [baseTime + 30_000, baseTime - 5 * MINUTE, baseTime + 2 * HOUR]

  for (const value of values) {
    assert.equal(
      formatTimeDisplay(value, { mode: 'relative', showExactTime: false, baseTime }),
      formatTimeDisplay(value, { mode: 'relative', showExactTime: true, baseTime }),
    )
  }
})

test('absolute mode uses one past-and-future rule set', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)
  const sameDay = localTime(2026, 7, 15, 9, 5)
  assert.equal(formatTimeDisplay(sameDay, { mode: 'absolute', baseTime }), '07/15')
  assert.equal(
    formatTimeDisplay(sameDay, { mode: 'absolute', showExactTime: true, baseTime }),
    '09:05',
  )

  for (const value of [localTime(2026, 7, 10, 9, 5), localTime(2026, 7, 20, 9, 5)]) {
    const expectedDate = value < baseTime ? '07/10' : '07/20'
    assert.equal(formatTimeDisplay(value, { mode: 'absolute', baseTime }), expectedDate)
    assert.equal(
      formatTimeDisplay(value, { mode: 'absolute', showExactTime: true, baseTime }),
      `${expectedDate} 09:05`,
    )
  }

  for (const value of [localTime(2025, 12, 20, 9, 5), localTime(2027, 1, 20, 9, 5)]) {
    const expectedDate = value < baseTime ? '2025/12/20' : '2027/01/20'
    assert.equal(formatTimeDisplay(value, { mode: 'absolute', baseTime }), expectedDate)
    assert.equal(
      formatTimeDisplay(value, { mode: 'absolute', showExactTime: true, baseTime }),
      `${expectedDate} 09:05`,
    )
  }
})

test('invalid or missing values use the em dash placeholder', () => {
  const options = { mode: 'relative' as const, baseTime: localTime(2026, 7, 15, 12, 0) }
  assert.equal(formatTimeDisplay(undefined, options), '—')
  assert.equal(formatTimeDisplay(null, options), '—')
  assert.equal(formatTimeDisplay('', options), '—')
  assert.equal(formatTimeDisplay('not-a-time', options), '—')
  assert.equal(formatTimeDisplay('2026/02/30', options), '—')
  assert.equal(formatTimeDisplay(Date.now(), { mode: 'absolute', baseTime: null }), '—')
})

test('calendar strings without a timezone are interpreted in local time', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)
  assert.equal(
    formatTimeDisplay('2026/07/15 09:05', {
      mode: 'absolute',
      showExactTime: true,
      baseTime,
    }),
    '09:05',
  )
})

test('next run always uses relative mode with exact time enabled', () => {
  const baseTime = localTime(2026, 7, 15, 12, 0)
  assert.equal(formatNextRunTime(localTime(2026, 7, 16, 9, 0), baseTime), '明天 09:00')
})
