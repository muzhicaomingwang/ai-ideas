// utils/itinerary-markdown.js

function normalizeLine(line) {
  return stripInvisible((line || '').replace(/\r/g, '')).trim()
}

function stripInvisible(s) {
  // Remove common invisible characters that can break regex matching.
  return String(s || '').replace(/[\u200B-\u200F\u202A-\u202E\u2060\uFEFF]/g, '')
}

function normalizePipes(line) {
  // Some IMEs/models output fullwidth pipes.
  return stripInvisible(String(line || '')).replace(/｜/g, '|')
}

function normalizeTimeRange(timeRange) {
  return stripInvisible(String(timeRange || ''))
    .replace(/：/g, ':')
    .replace(/[—–－‐‑‒―−~〜～﹣]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
}

export function itineraryToMarkdown(itinerary, itineraryVersion = 1) {
  const days = Array.isArray(itinerary?.days) ? itinerary.days : []

  const lines = []
  lines.push('# 行程安排')
  lines.push(`> 版本: v${itineraryVersion}`)
  lines.push('')

  for (const day of days) {
    const dayNum = day?.day ?? ''
    const date = day?.date ? `（${day.date}）` : ''
    lines.push(`## Day ${dayNum}${date}`)

    const items = Array.isArray(day?.items) ? day.items : []
    for (const item of items) {
      const timeStart = item?.time_start || ''
      const timeEnd = item?.time_end || ''
      const activity = item?.activity || ''
      const location = item?.location || ''
      const note = item?.note || ''

      const timeRange = `${timeStart} - ${timeEnd}`.trim()
      const parts = [timeRange, activity, location, note].map(p => String(p || '').trim())

      // 始终输出 4 段，保证可逆解析；空字段保留为空字符串
      lines.push(`- ${parts[0]} | ${parts[1]} | ${parts[2]} | ${parts[3]}`)
    }

    lines.push('')
  }

  // 去掉末尾多余空行
  while (lines.length > 0 && normalizeLine(lines[lines.length - 1]) === '') {
    lines.pop()
  }
  lines.push('')
  return lines.join('\n')
}

function parseDayHeading(line) {
  const m = /^##\s*Day\s*(\d+)\s*(?:（(.*)）)?\s*$/.exec(line)
  if (!m) return null
  return {
    day: Number(m[1]),
    date: m[2] ? m[2].trim() : ''
  }
}

function parseItemLine(line) {
  const trimmed = normalizePipes(line).replace(/^\-\s*/, '')
  const parts = trimmed.split('|').map(s => s.trim())
  if (parts.length < 2) return { error: '行项目格式错误：需要至少包含「时间 | 活动」' }

  const timeRange = normalizeTimeRange(parts[0])
  const activity = parts[1] || ''
  const location = parts[2] || ''
  const note = parts[3] || ''

  const timeMatch = /^(\d{1,2}:\d{2})\s*-\s*(\d{0,2}:?\d{0,2})\s*$/.exec(timeRange)
  if (!timeMatch) return { error: '时间格式错误：应为「HH:MM - HH:MM」（结束时间可留空）' }

  const timeStart = timeMatch[1]
  const timeEnd = (timeMatch[2] || '').trim()
  if (!activity.trim()) return { error: '活动不能为空' }

  return {
    item: {
      time_start: timeStart,
      time_end: timeEnd,
      activity: activity.trim(),
      location: location.trim(),
      note: note.trim()
    }
  }
}

export function parseItineraryMarkdown(markdown) {
  const errors = []
  const lines = normalizePipes(String(markdown || '')).replace(/\r/g, '').split('\n')

  const days = []
  let currentDay = null

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i]
    const line = normalizeLine(raw)
    if (!line) continue

    if (line.startsWith('# ')) continue
    if (line.startsWith('>')) continue

    const dayHeading = parseDayHeading(line)
    if (dayHeading) {
      currentDay = { day: dayHeading.day, date: dayHeading.date, items: [] }
      days.push(currentDay)
      continue
    }

    if (line.startsWith('- ')) {
      if (!currentDay) {
        errors.push(`第 ${i + 1} 行：行项目必须放在某个 Day 标题下方`)
        continue
      }
      const parsed = parseItemLine(line)
      if (parsed.error) {
        errors.push(`第 ${i + 1} 行：${parsed.error}`)
        continue
      }
      currentDay.items.push(parsed.item)
      continue
    }

    errors.push(`第 ${i + 1} 行：无法识别的内容（请使用 Day 标题或 "-" 行项目）`)
  }

  if (days.length === 0) errors.push('未找到任何 Day 标题（例如：## Day 1（日期））')
  for (const d of days) {
    if (!Array.isArray(d.items) || d.items.length === 0) {
      errors.push(`Day ${d.day} 下未找到任何行项目（以 "-" 开头）`)
    }
  }

  return {
    itinerary: { days },
    errors
  }
}

export function validateItineraryMarkdown(markdown) {
  const parsed = parseItineraryMarkdown(markdown)
  const totalItems = (parsed.itinerary?.days || []).reduce((sum, d) => sum + (d.items?.length || 0), 0)
  return {
    valid: parsed.errors.length === 0,
    errors: parsed.errors,
    itinerary: parsed.itinerary,
    stats: {
      days: parsed.itinerary?.days?.length || 0,
      items: totalItems
    }
  }
}

/**
 * Line-based cleanup:
 * - Treat every '\n' as a line (折行算一行)
 * - Keep only:
 *   1) Day headings: lines starting with "##Day" / "## Day"
 *   2) Time rows: lines starting with a time (optionally prefixed by "- " / "* ")
 * - Delete everything else.
 *
 * Notes:
 * - For time rows without a list marker, we prefix "- " so it can be parsed by the shared validator/parser.
 */
export function filterItineraryMarkdownLines(markdown) {
  const text = normalizePipes(String(markdown || '')).replace(/\r/g, '')
  const lines = text.split('\n')
  const out = []

  const dayRe = /^##\s*Day\b/i
  const timeStartRe = /^(\d{1,2}[:：]\d{2})\b/

  for (const raw of lines) {
    const line = stripInvisible(String(raw || '')).trim()
    if (!line) continue

    if (dayRe.test(line)) {
      out.push(line)
      continue
    }

    const withoutBullet = line.replace(/^[-*]\s*/, '')
    if (timeStartRe.test(withoutBullet)) {
      if (/^[-*]\s+/.test(line)) {
        out.push(line.replace(/^[-*]\s+/, '- '))
      } else {
        out.push(`- ${withoutBullet}`)
      }
    }
  }

  return out.join('\n').trim()
}
