// components/stepper/stepper.js
Component({
  properties: {
    value: {
      type: Number,
      value: 0
    },
    min: {
      type: Number,
      value: 0
    },
    max: {
      type: Number,
      value: 999999
    },
    step: {
      type: Number,
      value: 1
    }
  },

  data: {},

  methods: {
    handleMinus() {
      const { value, min, step } = this.properties
      if (value <= min) return

      const newValue = Math.max(value - step, min)
      this.triggerChange(newValue)
    },

    handlePlus() {
      const { value, max, step } = this.properties
      if (value >= max) return

      const newValue = Math.min(value + step, max)
      this.triggerChange(newValue)
    },

    handleInput(e) {
      const inputValue = e.detail.value
      const numValue = parseInt(inputValue, 10)

      if (isNaN(numValue)) return

      this.setData({ value: numValue })
    },

    handleBlur(e) {
      const inputValue = e.detail.value
      let numValue = parseInt(inputValue, 10)

      if (isNaN(numValue)) {
        numValue = this.properties.min
      }

      const { min, max } = this.properties
      numValue = Math.max(min, Math.min(max, numValue))

      this.triggerChange(numValue)
    },

    triggerChange(value) {
      this.setData({ value })
      this.triggerEvent('change', { value })
    }
  }
})
