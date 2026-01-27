Page({
  data: {
    destination: '',
    days: '',
    budget: '',
    itinerary: []
  },

  onLoad(options) {
    const { destination, days, budget } = options;
    this.setData({
      destination: decodeURIComponent(destination || '未知目的地'),
      days: days || 3,
      budget: budget || 5000
    });
    this.generateItinerary(parseInt(days || 3));
  },

  generateItinerary(days) {
    const activities = [
      { morning: '探访当地历史博物馆，感受文化底蕴', afternoon: '漫步市中心特色街区，打卡网红咖啡店', evening: '欣赏城市夜景，体验地道美食' },
      { morning: '前往自然公园徒步，呼吸新鲜空气', afternoon: '参观艺术画廊，沉浸在艺术海洋', evening: '在爵士酒吧小酌，享受惬意时光' },
      { morning: '体验当地手工艺制作', afternoon: '去海边/湖边散步，放松身心', evening: '逛当地夜市，搜罗特色纪念品' },
      { morning: '打卡著名地标建筑', afternoon: '在特色书店度过午后时光', evening: '观看当地特色演出' },
      { morning: '寻找隐藏在巷弄里的美食', afternoon: '去观景台俯瞰整个城市', evening: '在河边餐厅享用浪漫晚餐' }
    ];

    const itinerary = [];
    for (let i = 0; i < days; i++) {
      // 循环使用活动模板，避免天数过多时越界
      const activity = activities[i % activities.length];
      itinerary.push({
        day: i + 1,
        ...activity
      });
    }

    this.setData({ itinerary });
  },

  goBack() {
    wx.navigateBack();
  }
});
