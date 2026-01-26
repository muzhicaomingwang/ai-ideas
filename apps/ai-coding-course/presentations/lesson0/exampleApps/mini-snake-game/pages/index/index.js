const GRID_SIZE = 20;
const CELL_SIZE = 15;

Page({
  data: {
    score: 0,
    isPlaying: false,
    isGameOver: false
  },

  onLoad() {
    this.initGame();
  },

  initGame() {
    this.snake = [{x: 5, y: 5}, {x: 4, y: 5}, {x: 3, y: 5}];
    this.food = this.generateFood();
    this.direction = 'right';
    this.nextDirection = 'right';
    this.score = 0;
    
    this.setData({
      score: 0,
      isGameOver: false
    });

    const query = wx.createSelectorQuery();
    query.select('#gameCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        const dpr = wx.getSystemInfoSync().pixelRatio;
        
        canvas.width = res[0].width * dpr;
        canvas.height = res[0].height * dpr;
        ctx.scale(dpr, dpr);
        
        this.canvas = canvas;
        this.ctx = ctx;
        this.draw();
      });
  },

  startGame() {
    if (this.data.isPlaying) return;
    
    if (this.data.isGameOver) {
      this.initGame();
    }

    this.setData({ isPlaying: true });
    
    this.gameLoop = setInterval(() => {
      this.update();
      this.draw();
    }, 150);
  },

  update() {
    this.direction = this.nextDirection;
    const head = { ...this.snake[0] };

    switch(this.direction) {
      case 'up': head.y--; break;
      case 'down': head.y++; break;
      case 'left': head.x--; break;
      case 'right': head.x++; break;
    }

    // Check collision with walls
    if (head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE) {
      this.gameOver();
      return;
    }

    // Check collision with self
    for (let i = 0; i < this.snake.length; i++) {
      if (head.x === this.snake[i].x && head.y === this.snake[i].y) {
        this.gameOver();
        return;
      }
    }

    this.snake.unshift(head);

    // Check food
    if (head.x === this.food.x && head.y === this.food.y) {
      this.score += 10;
      this.setData({ score: this.score });
      this.food = this.generateFood();
    } else {
      this.snake.pop();
    }
  },

  draw() {
    if (!this.ctx) return;
    
    const ctx = this.ctx;
    ctx.clearRect(0, 0, 300, 300);

    // Draw snake
    ctx.fillStyle = '#4CAF50';
    this.snake.forEach(segment => {
      ctx.fillRect(segment.x * CELL_SIZE, segment.y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1);
    });

    // Draw food
    ctx.fillStyle = '#FF5722';
    ctx.beginPath();
    ctx.arc(
      this.food.x * CELL_SIZE + CELL_SIZE/2, 
      this.food.y * CELL_SIZE + CELL_SIZE/2, 
      CELL_SIZE/2 - 1, 
      0, 
      2 * Math.PI
    );
    ctx.fill();
  },

  generateFood() {
    let food;
    while (true) {
      food = {
        x: Math.floor(Math.random() * GRID_SIZE),
        y: Math.floor(Math.random() * GRID_SIZE)
      };
      // Check if food spawns on snake
      const onSnake = this.snake.some(segment => segment.x === food.x && segment.y === food.y);
      if (!onSnake) break;
    }
    return food;
  },

  gameOver() {
    clearInterval(this.gameLoop);
    this.setData({ 
      isPlaying: false,
      isGameOver: true 
    });
    wx.showToast({
      title: '游戏结束',
      icon: 'none'
    });
  },

  onDirectionTap(e) {
    const dir = e.currentTarget.dataset.dir;
    this.changeDirection(dir);
  },

  changeDirection(newDir) {
    const opposites = {
      'up': 'down',
      'down': 'up',
      'left': 'right',
      'right': 'left'
    };
    
    if (newDir !== opposites[this.direction]) {
      this.nextDirection = newDir;
    }
  }
});
