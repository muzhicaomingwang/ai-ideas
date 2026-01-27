Page({
  data: {
    destination: '',
    days: '',
    budget: '',
    daysRange: Array.from({length: 15}, (_, i) => i + 1)
  },

  onDestinationInput(e) {
    this.setData({ destination: e.detail.value });
  },

  onDaysChange(e) {
    this.setData({ days: this.data.daysRange[e.detail.value] });
  },

  onBudgetInput(e) {
    this.setData({ budget: e.detail.value });
  },

  generatePlan() {
    const { destination, days, budget } = this.data;
    if (!destination || !days || !budget) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    wx.navigateTo({
      url: `/pages/result/result?destination=${destination}&days=${days}&budget=${budget}`
    });
  }
});
