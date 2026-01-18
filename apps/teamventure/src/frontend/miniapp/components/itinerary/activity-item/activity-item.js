/**
 * activity-item 组件 - 单个活动项
 * 展示活动的时间、名称、地点、备注，支持编辑/删除/复制/移动操作
 */
Component({
  options: {
    addGlobalClass: true,
    styleIsolation: 'apply-shared'
  },

  properties: {
    // 活动数据
    activity: {
      type: Object,
      value: {
        id: '',
        time_start: '',
        time_end: '',
        activity: '',
        location: '',
        note: ''
      }
    },
    // 活动在列表中的索引
    itemIndex: {
      type: Number,
      value: 0
    },
    // 是否为第一个活动（控制上移按钮显示）
    isFirst: {
      type: Boolean,
      value: false
    },
    // 是否为最后一个活动（控制下移按钮显示）
    isLast: {
      type: Boolean,
      value: false
    },
    // 是否处于拖拽状态
    isDragging: {
      type: Boolean,
      value: false
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
     * 点击活动项（编辑）
     */
    onTapActivity() {
      this.triggerEvent('edit', {
        itemIndex: this.properties.itemIndex
      });
    },

    /**
     * 删除活动
     */
    onDelete(e) {
      // 阻止事件冒泡，避免触发编辑
      e.stopPropagation && e.stopPropagation();
      this.triggerEvent('delete', {
        itemIndex: this.properties.itemIndex
      });
    },

    /**
     * 复制活动
     */
    onCopy(e) {
      e.stopPropagation && e.stopPropagation();
      this.triggerEvent('copy', {
        itemIndex: this.properties.itemIndex
      });
    },

    /**
     * 上移活动
     */
    onMoveUp(e) {
      e.stopPropagation && e.stopPropagation();
      if (this.properties.isFirst) return;
      this.triggerEvent('move', {
        itemIndex: this.properties.itemIndex,
        direction: 'up'
      });
    },

    /**
     * 下移活动
     */
    onMoveDown(e) {
      e.stopPropagation && e.stopPropagation();
      if (this.properties.isLast) return;
      this.triggerEvent('move', {
        itemIndex: this.properties.itemIndex,
        direction: 'down'
      });
    },

    /**
     * 长按开始拖拽
     */
    onLongPress() {
      this.triggerEvent('dragstart', {
        itemIndex: this.properties.itemIndex
      });
    }
  }
});
