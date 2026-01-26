Page({
  data: {
    result: '0',
    prevValue: null,
    operator: null,
    waitingForNewValue: false
  },

  onNumber(e) {
    const num = e.currentTarget.dataset.num;
    const { result, waitingForNewValue } = this.data;

    if (waitingForNewValue) {
      this.setData({
        result: String(num),
        waitingForNewValue: false
      });
    } else {
      this.setData({
        result: result === '0' ? String(num) : result + num
      });
    }
  },

  onDot() {
    const { result, waitingForNewValue } = this.data;
    if (waitingForNewValue) {
      this.setData({
        result: '0.',
        waitingForNewValue: false
      });
    } else if (result.indexOf('.') === -1) {
      this.setData({
        result: result + '.'
      });
    }
  },

  onClear() {
    this.setData({
      result: '0',
      prevValue: null,
      operator: null,
      waitingForNewValue: false
    });
  },

  onToggleSign() {
    const { result } = this.data;
    this.setData({
      result: String(parseFloat(result) * -1)
    });
  },

  onPercent() {
    const { result } = this.data;
    this.setData({
      result: String(parseFloat(result) / 100)
    });
  },

  onOperator(e) {
    const nextOperator = e.currentTarget.dataset.op;
    const { result, prevValue, operator } = this.data;
    const inputValue = parseFloat(result);

    if (prevValue == null) {
      this.setData({
        prevValue: inputValue,
        waitingForNewValue: true,
        operator: nextOperator
      });
    } else if (operator) {
      const currentValue = prevValue || 0;
      const newValue = this.calculate(currentValue, inputValue, operator);

      this.setData({
        result: String(newValue),
        prevValue: newValue,
        waitingForNewValue: true,
        operator: nextOperator
      });
    }
  },

  onEqual() {
    const { result, prevValue, operator } = this.data;
    const inputValue = parseFloat(result);

    if (operator && prevValue != null) {
      const newValue = this.calculate(prevValue, inputValue, operator);
      this.setData({
        result: String(newValue),
        prevValue: null,
        operator: null,
        waitingForNewValue: true
      });
    }
  },

  calculate(prev, next, op) {
    switch (op) {
      case '+': return prev + next;
      case '-': return prev - next;
      case '*': return prev * next;
      case '/': return prev / next;
      default: return next;
    }
  }
});
