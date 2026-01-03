// pages/profile/profile.js
import { get } from '../../utils/request.js'

Page({
  data: {
    isLoggedIn: false,
    userInfo: {
      userId: '',
      nickName: '',
      avatarUrl: ''
    },
    stats: {
      totalPlans: 0,
      favoritePlans: 0,
      completedPlans: 0
    }
  },

  onLoad() {
    this.checkLoginStatus();
  },

  onShow() {
    if (this.data.isLoggedIn) {
      this.loadUserStats();
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');

    if (token && userInfo) {
      this.setData({
        isLoggedIn: true,
        userInfo: userInfo
      });
      this.loadUserStats();
    }
  },

  // 加载用户统计数据
  async loadUserStats() {
    try {
      // 这里应该调用实际的 API
      // const res = await request('/api/user/stats');
      // this.setData({ stats: res.data });

      // 临时模拟数据
      this.setData({
        stats: {
          totalPlans: 12,
          favoritePlans: 5,
          completedPlans: 3
        }
      });
    } catch (error) {
      console.error('加载统计数据失败:', error);
    }
  },

  // 登录
  handleLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  // 退出登录
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          this.setData({
            isLoggedIn: false,
            userInfo: {
              userId: '',
              nickName: '',
              avatarUrl: ''
            },
            stats: {
              totalPlans: 0,
              favoritePlans: 0,
              completedPlans: 0
            }
          });
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  },

  // 我的方案
  handleGoMyPlans() {
    wx.switchTab({
      url: '/pages/myplans/myplans'
    });
  },

  // 我的收藏
  handleGoFavorites() {
    if (!this.data.isLoggedIn) {
      this.showLoginTip();
      return;
    }
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 浏览历史
  handleGoHistory() {
    if (!this.data.isLoggedIn) {
      this.showLoginTip();
      return;
    }
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 设置
  handleGoSettings() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 帮助与反馈
  handleGoHelp() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 关于我们
  handleGoAbout() {
    wx.showModal({
      title: '关于 TeamVenture',
      content: 'TeamVenture 是一个 AI 驱动的智能团建方案生成平台，致力于为企业提供高质量的团建活动方案。\n\n版本：1.0.0',
      showCancel: false
    });
  },

  // 显示登录提示
  showLoginTip() {
    wx.showModal({
      title: '提示',
      content: '请先登录',
      confirmText: '去登录',
      success: (res) => {
        if (res.confirm) {
          this.handleLogin();
        }
      }
    });
  }
});
