Page({
  // 页面的初始数据
  data: {
    result: '0', // 当前显示的计算结果，默认为 '0'
    prevValue: null, // 存储上一个输入的数值
    operator: null, // 存储当前选择的运算符 (+, -, *, /)
    waitingForNewValue: false // 标记是否正在等待输入新的数值（在点击运算符后）
  },

  // 数字按钮点击事件处理函数
  onNumber(e) {
    // 获取点击按钮上的 data-num 属性值
    const num = e.currentTarget.dataset.num;
    // 获取当前的数据状态
    const { result, waitingForNewValue } = this.data;

    if (waitingForNewValue) {
      // 如果正在等待新数值（即刚才点击了运算符），则直接显示新输入的数字
      this.setData({
        result: String(num),
        waitingForNewValue: false // 重置等待标记
      });
    } else {
      // 否则，将新数字追加到当前结果后面（如果当前是 '0' 则直接替换）
      this.setData({
        result: result === '0' ? String(num) : result + num
      });
    }
  },

  // 小数点按钮点击事件处理函数
  onDot() {
    const { result, waitingForNewValue } = this.data;
    
    if (waitingForNewValue) {
      // 如果正在等待新数值，点击小数点则显示 '0.'
      this.setData({
        result: '0.',
        waitingForNewValue: false
      });
    } else if (result.indexOf('.') === -1) {
      // 如果当前结果中还没有小数点，则追加小数点
      this.setData({
        result: result + '.'
      });
    }
  },

  // 清除按钮 (AC) 点击事件处理函数
  onClear() {
    // 重置所有数据到初始状态
    this.setData({
      result: '0',
      prevValue: null,
      operator: null,
      waitingForNewValue: false
    });
  },

  // 正负号切换按钮 (+/-) 点击事件处理函数
  onToggleSign() {
    const { result } = this.data;
    // 将当前结果转换为浮点数，乘以 -1，再转回字符串
    this.setData({
      result: String(parseFloat(result) * -1)
    });
  },

  // 百分比按钮 (%) 点击事件处理函数
  onPercent() {
    const { result } = this.data;
    // 将当前结果除以 100
    this.setData({
      result: String(parseFloat(result) / 100)
    });
  },

  // 运算符按钮 (+, -, *, /) 点击事件处理函数
  onOperator(e) {
    // 获取点击按钮上的 data-op 属性值（即运算符）
    const nextOperator = e.currentTarget.dataset.op;
    const { result, prevValue, operator } = this.data;
    // 将当前显示的字符串转换为浮点数
    const inputValue = parseFloat(result);

    if (prevValue == null) {
      // 如果没有上一个数值，说明是第一次点击运算符
      // 将当前数值存为 prevValue，并记录运算符
      this.setData({
        prevValue: inputValue,
        waitingForNewValue: true, // 标记接下来输入的是新数值
        operator: nextOperator
      });
    } else if (operator) {
      // 如果已经有上一个数值和运算符，说明是连续运算（例如 1 + 2 +）
      // 先计算前一步的结果
      const currentValue = prevValue || 0;
      const newValue = this.calculate(currentValue, inputValue, operator);

      // 更新显示结果为计算后的值，并准备进行下一步运算
      this.setData({
        result: String(newValue),
        prevValue: newValue,
        waitingForNewValue: true,
        operator: nextOperator
      });
    }
  },

  // 等于号 (=) 点击事件处理函数
  onEqual() {
    const { result, prevValue, operator } = this.data;
    const inputValue = parseFloat(result);

    // 只有在有运算符和上一个数值的情况下才进行计算
    if (operator && prevValue != null) {
      const newValue = this.calculate(prevValue, inputValue, operator);
      // 显示计算结果，并重置运算符状态
      this.setData({
        result: String(newValue),
        prevValue: null,
        operator: null,
        waitingForNewValue: true // 计算完成后，下一次输入将开始新的数字
      });
    }
  },

  // 辅助函数：执行具体的数学运算
  calculate(prev, next, op) {
    switch (op) {
      case '+': return prev + next; // 加法
      case '-': return prev - next; // 减法
      case '*': return prev * next; // 乘法
      case '/': return prev / next; // 除法
      default: return next;
    }
  }
});
