/**
 * itinerary-validator.js
 * 行程数据验证工具
 * 提供行程、天数、活动的完整验证功能
 */

/**
 * 验证活动数据
 * @param {Object} activity - 活动对象
 * @returns {Object} { valid: boolean, errors: Object }
 */
function validateActivity(activity) {
  const errors = {};

  if (!activity) {
    return { valid: false, errors: { activity: '活动数据不能为空' } };
  }

  // 验证活动名称（必填）
  if (!activity.activity || !activity.activity.trim()) {
    errors.activity = '请输入活动名称';
  } else if (activity.activity.trim().length > 50) {
    errors.activity = '活动名称不能超过50个字符';
  }

  // 验证时间范围
  if (activity.time_start && activity.time_end) {
    const start = activity.time_start.replace(':', '');
    const end = activity.time_end.replace(':', '');
    if (parseInt(end) <= parseInt(start)) {
      errors.time = '结束时间应晚于开始时间';
    }
  }

  // 验证地点（选填，但有长度限制）
  if (activity.location && activity.location.length > 100) {
    errors.location = '地点名称不能超过100个字符';
  }

  // 验证备注（选填，但有长度限制）
  if (activity.note && activity.note.length > 200) {
    errors.note = '备注不能超过200个字符';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

/**
 * 验证单天数据
 * @param {Object} day - 天数据对象
 * @param {number} dayIndex - 天索引
 * @returns {Object} { valid: boolean, errors: Object }
 */
function validateDay(day, dayIndex = 0) {
  const errors = {};

  if (!day) {
    return { valid: false, errors: { day: '天数据不能为空' } };
  }

  // 验证日期
  if (!day.date) {
    errors.date = `第${dayIndex + 1}天缺少日期`;
  }

  // 验证活动列表
  if (!day.activities || !Array.isArray(day.activities)) {
    errors.activities = `第${dayIndex + 1}天活动列表格式错误`;
  } else if (day.activities.length === 0) {
    // 允许空活动列表，但可以提示
    // errors.activities = `第${dayIndex + 1}天没有安排活动`;
  } else {
    // 验证每个活动
    const activityErrors = [];
    day.activities.forEach((activity, actIndex) => {
      const result = validateActivity(activity);
      if (!result.valid) {
        activityErrors.push({
          index: actIndex,
          errors: result.errors
        });
      }
    });
    if (activityErrors.length > 0) {
      errors.activityErrors = activityErrors;
    }

    // 检查活动时间是否有冲突
    const timeConflicts = checkTimeConflicts(day.activities);
    if (timeConflicts.length > 0) {
      errors.timeConflicts = timeConflicts;
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
}

/**
 * 检查活动时间冲突
 * @param {Array} activities - 活动数组
 * @returns {Array} 冲突信息数组
 */
function checkTimeConflicts(activities) {
  const conflicts = [];

  if (!activities || activities.length < 2) {
    return conflicts;
  }

  // 按开始时间排序
  const sorted = activities
    .map((act, index) => ({ ...act, originalIndex: index }))
    .filter(act => act.time_start && act.time_end)
    .sort((a, b) => {
      const timeA = parseInt(a.time_start.replace(':', ''));
      const timeB = parseInt(b.time_start.replace(':', ''));
      return timeA - timeB;
    });

  // 检查相邻活动是否有时间重叠
  for (let i = 0; i < sorted.length - 1; i++) {
    const current = sorted[i];
    const next = sorted[i + 1];

    const currentEnd = parseInt(current.time_end.replace(':', ''));
    const nextStart = parseInt(next.time_start.replace(':', ''));

    if (currentEnd > nextStart) {
      conflicts.push({
        activity1: current.originalIndex,
        activity2: next.originalIndex,
        message: `"${current.activity}"与"${next.activity}"时间重叠`
      });
    }
  }

  return conflicts;
}

/**
 * 验证完整行程数据
 * @param {Object} itinerary - 行程对象
 * @returns {Object} { valid: boolean, errors: Object, warnings: Array }
 */
function validateItinerary(itinerary) {
  const errors = {};
  const warnings = [];

  if (!itinerary) {
    return { valid: false, errors: { itinerary: '行程数据不能为空' }, warnings };
  }

  // 验证行程标题
  if (!itinerary.title || !itinerary.title.trim()) {
    errors.title = '请输入行程标题';
  } else if (itinerary.title.trim().length > 30) {
    errors.title = '行程标题不能超过30个字符';
  }

  // 验证日期范围
  if (!itinerary.startDate) {
    errors.startDate = '请选择开始日期';
  }
  if (!itinerary.endDate) {
    errors.endDate = '请选择结束日期';
  }
  if (itinerary.startDate && itinerary.endDate) {
    const start = new Date(itinerary.startDate);
    const end = new Date(itinerary.endDate);
    if (end < start) {
      errors.dateRange = '结束日期不能早于开始日期';
    }
  }

  // 验证天数数据
  if (!itinerary.days || !Array.isArray(itinerary.days)) {
    errors.days = '行程天数数据格式错误';
  } else if (itinerary.days.length === 0) {
    errors.days = '行程至少需要包含1天';
  } else {
    // 验证每一天
    const dayErrors = [];
    itinerary.days.forEach((day, dayIndex) => {
      const result = validateDay(day, dayIndex);
      if (!result.valid) {
        dayErrors.push({
          index: dayIndex,
          errors: result.errors
        });
      }
      // 收集警告信息（如空活动列表）
      if (day.activities && day.activities.length === 0) {
        warnings.push(`第${dayIndex + 1}天没有安排活动`);
      }
    });
    if (dayErrors.length > 0) {
      errors.dayErrors = dayErrors;
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
    warnings
  };
}

/**
 * 格式化验证错误为用户友好的提示
 * @param {Object} errors - 错误对象
 * @returns {string} 格式化后的错误信息
 */
function formatErrors(errors) {
  if (!errors || Object.keys(errors).length === 0) {
    return '';
  }

  const messages = [];

  // 处理顶级错误
  Object.keys(errors).forEach(key => {
    const error = errors[key];

    if (typeof error === 'string') {
      messages.push(error);
    } else if (key === 'dayErrors' && Array.isArray(error)) {
      // 处理天级别错误
      error.forEach(dayError => {
        const dayNum = dayError.index + 1;
        const dayErrors = dayError.errors;

        if (dayErrors.date) {
          messages.push(dayErrors.date);
        }
        if (dayErrors.activityErrors && Array.isArray(dayErrors.activityErrors)) {
          dayErrors.activityErrors.forEach(actError => {
            const actNum = actError.index + 1;
            Object.values(actError.errors).forEach(msg => {
              messages.push(`第${dayNum}天活动${actNum}: ${msg}`);
            });
          });
        }
        if (dayErrors.timeConflicts && Array.isArray(dayErrors.timeConflicts)) {
          dayErrors.timeConflicts.forEach(conflict => {
            messages.push(`第${dayNum}天: ${conflict.message}`);
          });
        }
      });
    }
  });

  return messages.join('\n');
}

/**
 * 快速验证并显示Toast提示
 * @param {Object} itinerary - 行程对象
 * @returns {boolean} 是否验证通过
 */
function validateAndToast(itinerary) {
  const result = validateItinerary(itinerary);

  if (!result.valid) {
    const message = formatErrors(result.errors);
    wx.showToast({
      title: message.split('\n')[0], // 只显示第一条错误
      icon: 'none',
      duration: 2000
    });
    return false;
  }

  if (result.warnings.length > 0) {
    // 有警告但验证通过，可选择性提示
    console.warn('行程验证警告:', result.warnings);
  }

  return true;
}

/**
 * 时间字符串转分钟数
 * @param {string} timeStr - 时间字符串 "HH:mm"
 * @returns {number} 分钟数
 */
function timeToMinutes(timeStr) {
  if (!timeStr) return 0;
  const [hours, minutes] = timeStr.split(':').map(Number);
  return hours * 60 + minutes;
}

/**
 * 分钟数转时间字符串
 * @param {number} minutes - 分钟数
 * @returns {string} 时间字符串 "HH:mm"
 */
function minutesToTime(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

/**
 * 计算活动时长
 * @param {Object} activity - 活动对象
 * @returns {number} 时长（分钟）
 */
function getActivityDuration(activity) {
  if (!activity || !activity.time_start || !activity.time_end) {
    return 0;
  }
  const start = timeToMinutes(activity.time_start);
  const end = timeToMinutes(activity.time_end);
  return end - start;
}

/**
 * 计算单天总活动时长
 * @param {Object} day - 天数据对象
 * @returns {number} 总时长（分钟）
 */
function getDayTotalDuration(day) {
  if (!day || !day.activities || !Array.isArray(day.activities)) {
    return 0;
  }
  return day.activities.reduce((total, activity) => {
    return total + getActivityDuration(activity);
  }, 0);
}

/**
 * 格式化时长显示
 * @param {number} minutes - 分钟数
 * @returns {string} 格式化字符串（如"2小时30分钟"）
 */
function formatDuration(minutes) {
  if (minutes <= 0) return '0分钟';

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours > 0 && mins > 0) {
    return `${hours}小时${mins}分钟`;
  } else if (hours > 0) {
    return `${hours}小时`;
  } else {
    return `${mins}分钟`;
  }
}

module.exports = {
  // 验证函数
  validateActivity,
  validateDay,
  validateItinerary,
  validateAndToast,

  // 错误处理
  formatErrors,
  checkTimeConflicts,

  // 时间工具
  timeToMinutes,
  minutesToTime,
  getActivityDuration,
  getDayTotalDuration,
  formatDuration
};
