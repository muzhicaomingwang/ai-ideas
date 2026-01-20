import { filterItineraryMarkdownLines } from '../../utils/itinerary-markdown.js'

describe('utils/itinerary-markdown - filterItineraryMarkdownLines', () => {
  test('keeps only Day headings and time rows', () => {
    const input = [
      '# 行程安排',
      '> 版本: v1',
      '',
      '## Day 1（2024-01-01）',
      '- 09:00 - 10:00 | 早餐 | | ',
      '随便写一句',
      '10:00 - 11:00 | 游玩 | 景点 |',
      '* 11:00 - 12:00 | 午餐 | |',
      '',
      '##Day 2',
      '- 早餐 | 缺少时间会被删 | |'
    ].join('\n')

    const out = filterItineraryMarkdownLines(input)

    expect(out).toBe([
      '## Day 1（2024-01-01）',
      '- 09:00 - 10:00 | 早餐 | |',
      '- 10:00 - 11:00 | 游玩 | 景点 |',
      '- 11:00 - 12:00 | 午餐 | |',
      '##Day 2'
    ].join('\n'))
  })

  test('prefixes "- " for time rows without list marker', () => {
    const input = [
      '## Day 1',
      '09:00 - 10:00 | 集合 | 大堂 |'
    ].join('\n')

    const out = filterItineraryMarkdownLines(input)
    expect(out).toBe([
      '## Day 1',
      '- 09:00 - 10:00 | 集合 | 大堂 |'
    ].join('\n'))
  })
})

