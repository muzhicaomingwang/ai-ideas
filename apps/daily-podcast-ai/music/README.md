# 背景音乐文件夹

## 需要的音乐文件

为《完美的日子》播客准备以下背景音乐：

### 1. 恩尼奥·莫里康内 - 天堂电影院
- **原名**: Cinema Paradiso (Main Theme)
- **作曲**: Ennio Morricone
- **建议文件名**: `cinema-paradiso-main-theme.mp3`
- **时长**: 约2-3分钟
- **特点**: 温暖、怀旧、充满诗意

**获取方式**:
- iTunes/Apple Music
- Spotify（可用录屏工具录制）
- YouTube Music
- 网易云音乐

### 2. 雅尼 - 一个男人的梦想
- **原名**: One Man's Dream
- **作曲**: Yanni
- **建议文件名**: `yanni-one-mans-dream.mp3`
- **时长**: 约3-4分钟
- **特点**: 宁静、深沉、富有哲思

**获取方式**:
- iTunes/Apple Music
- Spotify
- YouTube Music
- 网易云音乐

---

## 使用说明

将下载的音乐文件放入此目录，然后运行：

```bash
cd /Users/qitmac001395/workspace/QAL/ideas/apps/daily-podcast-ai

./venv/bin/python scripts/add_background_music.py \
  output/2026-01-08/podcast-perfect-days-review-final.mp3 \
  --music music/cinema-paradiso-main-theme.mp3 music/yanni-one-mans-dream.mp3 \
  --output output/2026-01-08/podcast-perfect-days-with-bgm.mp3 \
  --volume 0.2
```

### 参数说明

- `--music`: 背景音乐文件（可多个，会自动交叉播放）
- `--volume`: 背景音量比例（0.2 = 20%）
- `--crossfade`: 音乐切换时淡入淡出时长（默认5秒）

---

## 版权说明

⚠️ 这些音乐文件受版权保护，仅供个人学习使用，请勿用于商业用途。
