Page({
  data: {
    destination: '',
    days: 3,
    budgetLabel: '',
    plan: []
  },

  onLoad(options) {
    const { dest, days, budget } = options;
    const budgetMap = {
      low: '穷游',
      mid: '舒适',
      high: '豪华'
    };

    this.setData({
      destination: dest,
      days: parseInt(days),
      budgetLabel: budgetMap[budget]
    });

    this.generateMockPlan(parseInt(days));
  },

  generateMockPlan(days) {
    const activities = [
      { time: '09:00', name: '城市地标打卡', desc: '参观市中心最著名的地标建筑，拍照留念' },
      { time: '12:00', name: '特色午餐', desc: '品尝当地最地道的特色美食' },
      { time: '14:00', name: '博物馆巡礼', desc: '深入了解当地的历史文化底蕴' },
      { time: '18:00', name: '日落观景台', desc: '在最佳观景点欣赏城市日落全景' },
      { time: '20:00', name: '夜市探索', desc: '感受当地热闹的夜生活氛围' }
    ];

    const plan = [];
    for (let i = 1; i <= days; i++) {
      // 随机打乱活动顺序以模拟不同行程
      const dailyActs = [...activities].sort(() => Math.random() - 0.5);
      
      plan.push({
        day: i,
        theme: `第${i}天 - 深度探索之旅`,
        activities: dailyActs
      });
    }

    this.setData({ plan });
  }
});
