Page({
  data: {
    destination: '',
    days: 3,
    budget: 'mid'
  },

  onDestInput(e) {
    this.setData({ destination: e.detail.value });
  },

  onDaysChange(e) {
    this.setData({ days: e.detail.value });
  },

  onBudgetChange(e) {
    this.setData({ budget: e.detail.value });
  },

  generatePlan() {
    if (!this.data.destination) {
      wx.showToast({
        title: '请输入目的地',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: 'AI正在规划中...',
    });

    // 模拟AI生成过程
    setTimeout(() => {
      wx.hideLoading();
      const params = `?dest=${this.data.destination}&days=${this.data.days}&budget=${this.data.budget}`;
      wx.navigateTo({
        url: '/pages/result/result' + params
      });
    }, 1500);
  }
});
