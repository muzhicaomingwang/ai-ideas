#!/bin/bash
# ============================================================
# Downloads 终极整理脚本 v4
# 目标：5个文件夹，0散落文件
# ============================================================

cd ~/Downloads || exit 1

# 启用dotglob以匹配隐藏文件
shopt -s dotglob

echo "🚀 开始整理（5文件夹版）..."

# 创建5个目录
mkdir -p Work      # 工作相关（简历、文档、专利、数据）
mkdir -p Tech      # 技术相关（安装包、压缩包、开发）
mkdir -p Media     # 媒体文件（图片、视频、音频）
mkdir -p Personal  # 个人文件（身份证、发票等）
mkdir -p _trash    # 垃圾/临时文件

# 删除旧目录（如果存在）
rmdir 01-installers 02-resumes 03-work-docs 04-data 05-media 06-archives 07-dev 08-patents 09-personal work development learning media personal _inbox 2>/dev/null

echo "📁 目录结构已创建"

moved=0

for file in *; do
    [ -d "$file" ] && continue
    [ ! -f "$file" ] && continue

    dest=""
    filename="$file"
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    # ========== 1. 垃圾文件（隐藏文件、临时文件）==========
    if [[ "$file" == .~* ]] || [[ "$file" == .DS_Store ]] || [[ "$file" == .localized ]] || \
       [[ "$file" == .* ]] || [[ "$file" == result ]]; then
        dest="_trash"

    # ========== 2. 个人文件（身份证、发票、护照等）==========
    elif [[ "$file" == *身份证* ]] || [[ "$file" == *护照* ]] || [[ "$file" == *发票* ]] || \
         [[ "$file" == *电子发票* ]] || [[ "$file" == *保险* ]] || [[ "$file" == *社保* ]] || \
         [[ "$file" == *无犯罪* ]] || [[ "$file" == *马拉松* ]] || [[ "$file" == *花名册* ]] || \
         [[ "$file" == 王植萌* ]]; then
        dest="Personal"

    # ========== 3. 工作相关（简历、专利、文档、数据）==========
    # 简历/HR
    elif [[ "$file" == *简历* ]] || [[ "$file" == *候选人* ]] || [[ "$file" == *招聘* ]] || \
         [[ "$file" == 【JAVA开发* ]] || [[ "$file" == 【产品运营* ]] || \
         [[ "$file" == *Resume* ]] || [[ "$file" == *resume* ]]; then
        dest="Work"
    # 专利
    elif [[ "$file" == PN143235* ]] || [[ "$file" == *专利* ]] || [[ "$file" == *复审* ]]; then
        dest="Work"

    # ========== 4. 按扩展名分类 ==========
    else
        case "$ext_lower" in
            # Tech: 安装包
            dmg|pkg|exe|msi|deb|rpm|apk|ipa|app)
                dest="Tech"
                ;;

            # Tech: 压缩包
            zip|tar|gz|tgz|rar|7z|bz2|xz|larkcache|cpgz)
                dest="Tech"
                ;;

            # Tech: 开发相关
            java|py|js|ts|sh|yml|yaml|conf|config|env|ini|properties|ipynb|vsix|crx|excalidraw|xmind|h2d|difypkg|m3u8|ofd)
                dest="Tech"
                ;;

            # Work: 数据文件
            csv|xls|xlsx|numbers|json|xml|sql)
                dest="Work"
                ;;

            # Media: 图片
            jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|heic|heif)
                dest="Media"
                ;;

            # Media: 视频
            mp4|mov|avi|mkv|wmv|flv|webm|m4v)
                dest="Media"
                ;;

            # Media: 音频
            mp3|wav|flac|aac|m4a|ogg|wma)
                dest="Media"
                ;;

            # Work: 文档类（PDF、Word、PPT等）
            pdf|doc|docx|ppt|pptx|key|pages|rtf|txt|html|md)
                dest="Work"
                ;;

            # 其他未知扩展名
            *)
                if [[ -x "$file" ]]; then
                    dest="Tech"
                else
                    dest="_trash"
                fi
                ;;
        esac
    fi

    # 移动文件
    if [ -n "$dest" ] && [ -f "$file" ]; then
        mv "$file" "$dest/" 2>/dev/null && ((moved++))
    fi
done

echo ""
echo "=========================================="
echo "📊 整理完成！移动了 $moved 个文件"
echo "=========================================="
echo ""

# 统计
echo "📁 各目录文件数量："
for dir in Work Tech Media Personal _trash; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
        [ "$count" -gt 0 ] && echo "  $dir/: $count 个文件"
    fi
done

echo ""

# 检查散落文件
remaining=$(find . -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  仍有 $remaining 个文件未分类："
    find . -maxdepth 1 -type f -exec basename {} \; 2>/dev/null | head -20
else
    echo "🎉 所有文件已分类完成！零散落！"
fi

echo ""
echo "✨ Done!"
open ~/Downloads
