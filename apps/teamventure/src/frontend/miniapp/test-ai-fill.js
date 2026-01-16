/**
 * AI填充功能测试脚本
 * 在微信开发者工具Console中运行此脚本查看不同天数的生成效果
 */

// 复制核心逻辑用于测试
function generateAITemplate(days, origin, destination) {
  const basicInfo = `# 团建行程方案

## 基本信息
- **天数**: ${days}天${days > 1 ? (days - 1) + '夜' : ''}
- **预算**: ¥500 - ¥800/人

## 行程路线
- **出发地**: ${origin}
- **到达地**: ${destination}`

  // 途经点逻辑
  let waypoints = ''
  if (days >= 5 && days <= 6) {
    waypoints = '\n- **途径地**: （建议第3天，请填写具体城市）'
  } else if (days === 7 || days === 8) {
    waypoints = '\n- **途径地1**: （建议第3天，请填写具体城市）\n- **途径地2**: （建议第5天，请填写具体城市）'
  } else if (days >= 9) {
    waypoints = '\n- **途径地1**: （建议第3天，请填写具体城市）\n- **途径地2**: （建议第5天，请填写具体城市）\n- **途径地3**: （建议第7天，请填写具体城市）'
  }

  const transportation = `

## 交通安排
### 去程
- **方式**: 高铁/航班（${origin} → ${destination}，请填写具体班次和时间）

### 返程
- **方式**: 高铁/航班（${destination} → ${origin}，请填写具体班次和时间）`

  const accommodation = generateAccommodation(days, origin, destination)

  const activities = `

## 活动偏好
- 团队协作（如：拓展训练、团队挑战）
- 文化体验（如：当地特色、历史古迹）
- 休闲娱乐（如：美食品鉴、自由活动）

## 特殊要求
- 如有老人/小孩、饮食限制等特殊需求，请在此填写
- 如无特殊要求可删除此段`

  return basicInfo + waypoints + transportation + accommodation + activities
}

function generateAccommodation(days, origin, destination) {
  let accommodation = '\n\n## 住宿安排'

  if (days === 1) {
    accommodation += '\n<!-- 1天行程无需住宿安排 -->'
    return accommodation
  }

  for (let day = 1; day <= days; day++) {
    accommodation += `\n### 第${numberToChinese(day)}日`

    if (day === 1) {
      accommodation += `\n- **入住**: ${destination}XX酒店（请填写具体酒店名称和星级）`
    } else if (day === days) {
      accommodation += `\n- **出发**: ${destination}XX酒店\n<!-- 当日返程，无需入住 -->`
    } else if (days >= 5 && isWaypointDay(day, days)) {
      const waypointIndex = getWaypointIndex(day, days)
      accommodation += `\n- **出发**: 前一站酒店`
      accommodation += `\n- **入住**: 途径地${waypointIndex}XX酒店（请填写具体酒店名称）`
    } else {
      accommodation += `\n- **出发**: ${destination}XX酒店`
      accommodation += `\n- **入住**: ${destination}XX度假村（或续住前一酒店）`
    }
  }

  return accommodation
}

function isWaypointDay(day, totalDays) {
  if (totalDays >= 5 && totalDays <= 6 && day === 3) return true
  if ((totalDays === 7 || totalDays === 8) && (day === 3 || day === 5)) return true
  if (totalDays >= 9 && (day === 3 || day === 5 || day === 7)) return true
  return false
}

function getWaypointIndex(day, totalDays) {
  if (totalDays >= 5 && totalDays <= 6 && day === 3) return 1
  if (totalDays === 7 || totalDays === 8) {
    if (day === 3) return 1
    if (day === 5) return 2
  }
  if (totalDays >= 9) {
    if (day === 3) return 1
    if (day === 5) return 2
    if (day === 7) return 3
  }
  return 1
}

function numberToChinese(num) {
  const chinese = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
  if (num <= 10) return chinese[num - 1]
  return num.toString()
}

// ==================== 测试用例 ====================

console.log('========== AI填充功能测试 ==========\n')

// 测试1天
console.log('【测试1】1天旅行（无住宿）')
console.log(generateAITemplate(1, '北京', '天津'))
console.log('\n' + '='.repeat(50) + '\n')

// 测试2天
console.log('【测试2】2天旅行（1晚住宿）')
console.log(generateAITemplate(2, '上海', '杭州'))
console.log('\n' + '='.repeat(50) + '\n')

// 测试3天
console.log('【测试3】3天旅行（2晚住宿）')
console.log(generateAITemplate(3, '北京', '青岛'))
console.log('\n' + '='.repeat(50) + '\n')

// 测试5天（1个途经点）
console.log('【测试4】5天旅行（1个途经点在第3天）')
console.log(generateAITemplate(5, '广州', '云南'))
console.log('\n' + '='.repeat(50) + '\n')

// 测试7天（2个途经点）
console.log('【测试5】7天旅行（2个途经点在第3、5天）')
console.log(generateAITemplate(7, '上海', '成都'))
console.log('\n' + '='.repeat(50) + '\n')

// 测试9天（3个途经点）
console.log('【测试6】9天旅行（3个途经点在第3、5、7天）')
console.log(generateAITemplate(9, '北京', '西藏'))
console.log('\n' + '='.repeat(50) + '\n')

console.log('测试完成！')
