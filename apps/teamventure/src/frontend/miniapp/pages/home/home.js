// pages/home/home.js
Page({
  data: {
    hotDestinations: [
      { id: 1, name: '北京怀柔', emoji: '🏔️', tag: '山水田园' },
      { id: 2, name: '杭州千岛湖', emoji: '🏞️', tag: '湖光山色' },
      { id: 3, name: '上海崇明', emoji: '🌳', tag: '生态休闲' },
      { id: 4, name: '苏州周庄', emoji: '🏘️', tag: '古镇风情' },
      { id: 5, name: '南京紫金山', emoji: '⛰️', tag: '历史文化' },
      { id: 6, name: '青岛崂山', emoji: '🌊', tag: '海滨风光' }
    ],
    recommendedPlans: [
      {
        id: 1,
        name: '怀柔山水两日游',
        pricePerPerson: 800,
        duration: '2天1夜',
        destination: '北京怀柔',
        tags: ['户外拓展', '团队协作']
      },
      {
        id: 2,
        name: '千岛湖休闲三日游',
        pricePerPerson: 1200,
        duration: '3天2夜',
        destination: '杭州千岛湖',
        tags: ['休闲度假', '美食体验']
      },
      {
        id: 3,
        name: '崇明生态一日游',
        pricePerPerson: 300,
        duration: '1天',
        destination: '上海崇明',
        tags: ['亲近自然', '农家乐']
      }
    ],
    activityTypes: [
      { value: 'outdoor', label: '户外拓展', emoji: '🏃' },
      { value: 'leisure', label: '休闲度假', emoji: '🏖️' },
      { value: 'culture', label: '文化体验', emoji: '🎭' },
      { value: 'food', label: '美食之旅', emoji: '🍜' },
      { value: 'sports', label: '运动竞技', emoji: '⚽' },
      { value: 'adventure', label: '探险挑战', emoji: '🧗' }
    ]
  },

  onLoad() {
    // 页面加载时的逻辑
  },

  onShow() {
    // 页面显示时的逻辑
  },

  // 快捷操作
  handleGoGenerate() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  },

  handleGoMyPlans() {
    wx.switchTab({
      url: '/pages/myplans/myplans'
    });
  },

  // 查看更多目的地
  handleViewMoreDestinations() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 选择目的地
  handleSelectDestination(e) {
    const destination = e.currentTarget.dataset.destination;
    // 跳转到生成方案页面，并预填目的地
    wx.switchTab({
      url: '/pages/index/index'
    });
    // 注意：TabBar 页面无法通过 URL 传参，需要使用全局变量或缓存
    wx.setStorageSync('prefilledDestination', destination);
  },

  // 查看更多推荐方案
  handleViewMorePlans() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 查看方案模板
  handleViewPlanTemplate(e) {
    const planId = e.currentTarget.dataset.planId;
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 选择活动类型
  handleSelectActivityType(e) {
    const type = e.currentTarget.dataset.type;
    // 跳转到生成方案页面，并预填活动类型
    wx.switchTab({
      url: '/pages/index/index'
    });
    wx.setStorageSync('prefilledActivityType', type);
  }
});
