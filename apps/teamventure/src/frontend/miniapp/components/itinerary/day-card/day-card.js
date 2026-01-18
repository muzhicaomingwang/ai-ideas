/**
 * day-card 组件 - 单日行程卡片
 * 展示某一天的日期和所有活动，支持添加/删除/编辑活动
 */
Component({
  options: {
    addGlobalClass: true,
    styleIsolation: 'apply-shared'
  },

  properties: {
    // 天数数据
    dayData: {
      type: Object,
      value: {
        day: 1,
        date: '',
        items: []
      }
    },
    // 天数索引
    dayIndex: {
      type: Number,
      value: 0
    },
    // 是否可删除（只有一天时不可删除）
    canDelete: {
      type: Boolean,
      value: true
    },
    // 是否处于拖拽状态
    isDragging: {
      type: Boolean,
      value: false
    },
    // 当前拖拽的活动索引
    draggingItemIndex: {
      type: Number,
      value: -1
    }
  },

  data: {
    // 内部状态
  },

  lifetimes: {
    attached() {
      // 组件挂载
    },
    detached() {
      // 组件卸载
    }
  },

  methods: {
    /**
     * 日期变更
     */
    onDateChange(e) {
      const newDate = e.detail.value;
      this.triggerEvent('datechange', {
        dayIndex: this.properties.dayIndex,
        date: newDate
      });
    },

    /**
     * 删除当天
     */
    onDeleteDay() {
      if (!this.properties.canDelete) return;

      wx.showModal({
        title: '确认删除',
        content: `确定要删除第${this.properties.dayData.day}天的行程吗？`,
        confirmColor: '#ff4d4f',
        success: (res) => {
          if (res.confirm) {
            this.triggerEvent('deleteday', {
              dayIndex: this.properties.dayIndex
            });
          }
        }
      });
    },

    /**
     * 添加活动
     */
    onAddActivity() {
      this.triggerEvent('addactivity', {
        dayIndex: this.properties.dayIndex
      });
    },

    /**
     * 编辑活动
     */
    onEditActivity(e) {
      const { itemIndex } = e.currentTarget.dataset;
      this.triggerEvent('editactivity', {
        dayIndex: this.properties.dayIndex,
        itemIndex: itemIndex
      });
    },

    /**
     * 删除活动
     */
    onDeleteActivity(e) {
      const { itemIndex } = e.currentTarget.dataset;
      this.triggerEvent('deleteactivity', {
        dayIndex: this.properties.dayIndex,
        itemIndex: itemIndex
      });
    },

    /**
     * 复制活动
     */
    onCopyActivity(e) {
      const { itemIndex } = e.currentTarget.dataset;
      this.triggerEvent('copyactivity', {
        dayIndex: this.properties.dayIndex,
        itemIndex: itemIndex
      });
    },

    /**
     * 移动活动（上/下）
     */
    onMoveActivity(e) {
      const { itemIndex, direction } = e.currentTarget.dataset;
      this.triggerEvent('moveactivity', {
        dayIndex: this.properties.dayIndex,
        itemIndex: itemIndex,
        direction: direction
      });
    },

    /**
     * 活动项事件代理（来自 activity-item 组件）
     */
    onActivityEvent(e) {
      const { type, itemIndex, ...rest } = e.detail;
      this.triggerEvent(type, {
        dayIndex: this.properties.dayIndex,
        itemIndex: itemIndex,
        ...rest
      });
    }
  }
});
