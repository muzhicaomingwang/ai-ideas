/**
 * activity-editor 组件 - 活动编辑弹窗
 * 用于新增或编辑单个活动的详细信息
 */
Component({
  options: {
    addGlobalClass: true,
    styleIsolation: 'apply-shared'
  },

  properties: {
    // 是否显示弹窗
    visible: {
      type: Boolean,
      value: false
    },
    // 编辑模式: 'add' | 'edit'
    mode: {
      type: String,
      value: 'add'
    },
    // 活动数据（编辑模式时传入）
    activity: {
      type: Object,
      value: null
    },
    // 当前编辑的活动索引（编辑模式时传入）
    activityIndex: {
      type: Number,
      value: -1
    },
    // 当前天数索引
    dayIndex: {
      type: Number,
      value: 0
    }
  },

  data: {
    // 表单数据
    formData: {
      time_start: '09:00',
      time_end: '10:00',
      activity: '',
      location: '',
      note: ''
    },
    // 时间选择器状态
    showStartTimePicker: false,
    showEndTimePicker: false,
    // 表单验证错误
    errors: {}
  },

  observers: {
    // 监听visible变化，打开时初始化表单
    'visible, activity': function(visible, activity) {
      if (visible) {
        this.initForm(activity);
      }
    }
  },

  methods: {
    /**
     * 初始化表单数据
     */
    initForm(activity) {
      if (activity && this.properties.mode === 'edit') {
        // 编辑模式：填充现有数据
        this.setData({
          formData: {
            time_start: activity.time_start || '09:00',
            time_end: activity.time_end || '10:00',
            activity: activity.activity || '',
            location: activity.location || '',
            note: activity.note || ''
          },
          errors: {}
        });
      } else {
        // 新增模式：使用默认值
        this.setData({
          formData: {
            time_start: '09:00',
            time_end: '10:00',
            activity: '',
            location: '',
            note: ''
          },
          errors: {}
        });
      }
    },

    /**
     * 输入框变化处理
     */
    onInputChange(e) {
      const { field } = e.currentTarget.dataset;
      const { value } = e.detail;
      this.setData({
        [`formData.${field}`]: value,
        [`errors.${field}`]: '' // 清除该字段的错误
      });
    },

    /**
     * 显示开始时间选择器
     */
    onShowStartTimePicker() {
      this.setData({ showStartTimePicker: true });
    },

    /**
     * 显示结束时间选择器
     */
    onShowEndTimePicker() {
      this.setData({ showEndTimePicker: true });
    },

    /**
     * 开始时间选择完成
     */
    onStartTimeChange(e) {
      const time = e.detail.value;
      this.setData({
        'formData.time_start': time,
        showStartTimePicker: false,
        'errors.time': ''
      });
    },

    /**
     * 结束时间选择完成
     */
    onEndTimeChange(e) {
      const time = e.detail.value;
      this.setData({
        'formData.time_end': time,
        showEndTimePicker: false,
        'errors.time': ''
      });
    },

    /**
     * 验证表单
     */
    validateForm() {
      const { formData } = this.data;
      const errors = {};

      // 验证活动名称（必填）
      if (!formData.activity || !formData.activity.trim()) {
        errors.activity = '请输入活动名称';
      }

      // 验证时间（结束时间应晚于开始时间）
      if (formData.time_start && formData.time_end) {
        const start = formData.time_start.replace(':', '');
        const end = formData.time_end.replace(':', '');
        if (parseInt(end) <= parseInt(start)) {
          errors.time = '结束时间应晚于开始时间';
        }
      }

      this.setData({ errors });
      return Object.keys(errors).length === 0;
    },

    /**
     * 保存活动
     */
    onSave() {
      if (!this.validateForm()) {
        wx.showToast({
          title: '请检查输入',
          icon: 'none'
        });
        return;
      }

      const { formData } = this.data;
      const { mode, activityIndex, dayIndex } = this.properties;

      // 构建活动数据
      const activityData = {
        time_start: formData.time_start,
        time_end: formData.time_end,
        activity: formData.activity.trim(),
        location: formData.location.trim(),
        note: formData.note.trim()
      };

      // 触发保存事件
      this.triggerEvent('save', {
        mode,
        dayIndex,
        activityIndex,
        activity: activityData
      });

      // 关闭弹窗
      this.onClose();
    },

    /**
     * 取消/关闭弹窗
     */
    onClose() {
      this.triggerEvent('close');
    },

    /**
     * 阻止蒙层点击穿透
     */
    preventTap() {
      // 空函数，仅用于阻止事件穿透
    }
  }
});
