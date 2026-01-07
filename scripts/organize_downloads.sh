#!/bin/bash
# ============================================================
# Downloads 文件夹整理脚本 v2 (修复版)
# ============================================================

DOWNLOADS_DIR="$HOME/Downloads"
cd "$DOWNLOADS_DIR" || exit 1

echo "🚀 开始整理 Downloads 文件夹..."
echo ""

# 创建目录结构
mkdir -p work/{documents,presentations,data,design,hr}
mkdir -p development/{packages,archives,configs,fonts}
mkdir -p learning/{ebooks,papers,courses}
mkdir -p media/{images,screenshots,videos,audio}
mkdir -p personal/{finance,identity,misc}
mkdir -p _inbox

echo "📁 目录结构已创建"
echo ""

# 计数器
moved=0

# 遍历所有文件（不进入子目录）
for file in *; do
    # 跳过目录
    [ -d "$file" ] && continue

    # 获取小写扩展名
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    filename_lower=$(echo "$file" | tr '[:upper:]' '[:lower:]')

    dest=""

    # 根据扩展名分类
    case "$ext_lower" in
        # ----- Development: 安装包 -----
        dmg|pkg|app|exe|msi|deb|rpm)
            dest="development/packages"
            ;;

        # ----- Development: 压缩包 -----
        zip|tar|gz|tgz|rar|7z|bz2|xz)
            dest="development/archives"
            ;;

        # ----- Development: 配置 -----
        yml|yaml|conf|config|env|ini|properties|toml)
            dest="development/configs"
            ;;

        # ----- Development: 字体 -----
        ttf|otf|woff|woff2|eot)
            dest="development/fonts"
            ;;

        # ----- Work: 文档 -----
        docx|doc|pages|rtf|odt|md|txt)
            dest="work/documents"
            ;;

        # ----- Work: 演示 -----
        pptx|ppt|key|odp)
            dest="work/presentations"
            ;;

        # ----- Work: 数据 -----
        xlsx|xls|csv|numbers|json|xml|sql)
            dest="work/data"
            ;;

        # ----- Work: 设计 -----
        sketch|fig|xd|psd|ai|indd|afdesign|afphoto)
            dest="work/design"
            ;;

        # ----- Learning: 电子书 -----
        epub|mobi|azw3|djvu)
            dest="learning/ebooks"
            ;;

        # ----- Learning: PDF (默认归入学习) -----
        pdf)
            dest="learning/ebooks"
            ;;

        # ----- Media: 图片 -----
        jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|heic|heif|raw|cr2|nef)
            # 检查是否是HR/招聘相关
            if [[ "$file" == *候选人* ]] || [[ "$file" == *简历* ]] || [[ "$file" == *resume* ]] || [[ "$file" == *实习* ]]; then
                dest="work/hr"
            # 检查是否是截图
            elif [[ "$file" == 截屏* ]] || [[ "$file" == Screenshot* ]] || [[ "$file" == "Screen Shot"* ]] || [[ "$filename_lower" == *screenshot* ]]; then
                dest="media/screenshots"
            else
                dest="media/images"
            fi
            ;;

        # ----- Media: 视频 -----
        mp4|mov|avi|mkv|wmv|flv|webm|m4v|3gp)
            dest="media/videos"
            ;;

        # ----- Media: 音频 -----
        mp3|wav|flac|aac|m4a|ogg|wma|aiff)
            dest="media/audio"
            ;;

        # ----- 其他：根据文件名关键词判断 -----
        *)
            # 发票/财务
            if [[ "$file" == *发票* ]] || [[ "$filename_lower" == *invoice* ]] || [[ "$filename_lower" == *receipt* ]]; then
                dest="personal/finance"
            # 身份证件
            elif [[ "$file" == *身份证* ]] || [[ "$file" == *护照* ]] || [[ "$file" == *驾照* ]]; then
                dest="personal/identity"
            # HR/招聘
            elif [[ "$file" == *候选人* ]] || [[ "$file" == *简历* ]] || [[ "$filename_lower" == *resume* ]]; then
                dest="work/hr"
            # 无法识别 -> inbox
            else
                dest="_inbox"
            fi
            ;;
    esac

    # 移动文件
    if [ -n "$dest" ] && [ -f "$file" ]; then
        mv "$file" "$dest/" 2>/dev/null && {
            echo "  ✓ $file → $dest/"
            ((moved++))
        }
    fi
done

echo ""
echo "=========================================="
echo "📊 整理完成！移动了 $moved 个文件"
echo "=========================================="
echo ""

# 统计各目录
echo "📁 各目录文件数量："
for dir in work development learning media personal _inbox; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        [ "$count" -gt 0 ] && echo "  $dir/: $count 个文件"
    fi
done

echo ""

# 检查剩余文件
remaining=$(find . -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  仍有 $remaining 个文件未分类："
    find . -maxdepth 1 -type f -exec basename {} \; 2>/dev/null
fi

echo ""
open ~/Downloads
echo "✨ Done!"
