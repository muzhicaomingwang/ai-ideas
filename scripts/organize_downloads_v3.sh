#!/bin/bash
# ============================================================
# Downloads 终极整理脚本 v3
# 目标：10个文件夹，0散落文件
# ============================================================

cd ~/Downloads || exit 1

echo "🚀 开始终极整理..."

# 创建目录结构（精简为10个）
mkdir -p 01-installers      # 所有安装包
mkdir -p 02-resumes         # 简历/HR
mkdir -p 03-work-docs       # 工作文档
mkdir -p 04-data            # 数据文件
mkdir -p 05-media           # 图片/视频/音频
mkdir -p 06-archives        # 压缩包
mkdir -p 07-dev             # 开发相关
mkdir -p 08-patents         # 专利
mkdir -p 09-personal        # 个人文件
mkdir -p _trash             # 垃圾/临时文件

# 删除旧的空目录（如果存在）
rmdir work development learning media personal _inbox 2>/dev/null

echo "📁 目录结构已创建"

# 计数
moved=0

for file in *; do
    [ -d "$file" ] && continue  # 跳过目录
    [ ! -f "$file" ] && continue

    dest=""
    filename="$file"
    ext="${file##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    # ========== 1. 垃圾文件优先处理 ==========
    # 临时锁定文件
    if [[ "$file" == .~* ]] || [[ "$file" == .DS_Store ]] || [[ "$file" == .localized ]]; then
        dest="_trash"

    # ========== 2. 简历/HR（高优先级，按文件名识别）==========
    elif [[ "$file" == *简历* ]] || [[ "$file" == *候选人* ]] || [[ "$file" == *招聘* ]] || \
         [[ "$file" == 【JAVA开发* ]] || [[ "$file" == 【产品运营* ]] || \
         [[ "$file" == *Resume* ]] || [[ "$file" == *resume* ]]; then
        dest="02-resumes"

    # ========== 3. 专利文件 ==========
    elif [[ "$file" == PN143235* ]] || [[ "$file" == *专利* ]] || [[ "$file" == *复审* ]]; then
        dest="08-patents"

    # ========== 4. 个人文件（身份证、发票、护照等）==========
    elif [[ "$file" == *身份证* ]] || [[ "$file" == *护照* ]] || [[ "$file" == *发票* ]] || \
         [[ "$file" == *电子发票* ]] || [[ "$file" == *保险* ]] || [[ "$file" == *社保* ]] || \
         [[ "$file" == *无犯罪* ]] || [[ "$file" == *马拉松* ]] || [[ "$file" == *花名册* ]] || \
         [[ "$file" == 王植萌* ]]; then
        dest="09-personal"

    # ========== 5. 按扩展名分类 ==========
    else
        case "$ext_lower" in
            # 安装包
            dmg|pkg|exe|msi|deb|rpm|apk|ipa|app)
                dest="01-installers"
                ;;

            # 压缩包
            zip|tar|gz|tgz|rar|7z|bz2|xz|larkcache|cpgz)
                dest="06-archives"
                ;;

            # 数据文件
            csv|xls|xlsx|numbers|json|xml|sql)
                dest="04-data"
                ;;

            # 开发相关
            java|py|js|ts|sh|yml|yaml|conf|config|env|ini|properties|ipynb|md|vsix|crx|excalidraw|xmind|h2d|difypkg|m3u8|ofd)
                dest="07-dev"
                ;;

            # 图片
            jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|heic|heif)
                dest="05-media"
                ;;

            # 视频
            mp4|mov|avi|mkv|wmv|flv|webm|m4v)
                dest="05-media"
                ;;

            # 音频
            mp3|wav|flac|aac|m4a|ogg|wma)
                dest="05-media"
                ;;

            # 文档类
            pdf|doc|docx|ppt|pptx|key|pages|rtf|txt|html)
                # PDF/文档需要进一步按内容分类
                if [[ "$file" == *Onepage* ]] || [[ "$file" == *汇报* ]] || [[ "$file" == *总结* ]] || \
                   [[ "$file" == *季度* ]] || [[ "$file" == *周报* ]] || [[ "$file" == *Review* ]] || \
                   [[ "$file" == *晋升* ]] || [[ "$file" == *绩效* ]] || [[ "$file" == *立项* ]] || \
                   [[ "$file" == *预算* ]] || [[ "$file" == *战略* ]] || [[ "$file" == *规范* ]] || \
                   [[ "$file" == *故障* ]] || [[ "$file" == *稳定性* ]] || [[ "$file" == *架构* ]] || \
                   [[ "$file" == *分享* ]] || [[ "$file" == *实践* ]] || [[ "$file" == *PPT* ]] || \
                   [[ "$file" == *pptx ]] || [[ "$file" == *key ]] || [[ "$file" == qunar* ]] || \
                   [[ "$file" == Qunar* ]] || [[ "$file" == *AI* ]] || [[ "$file" == *Agent* ]] || \
                   [[ "$file" == *智能* ]] || [[ "$file" == *大模型* ]] || [[ "$file" == *技术* ]] || \
                   [[ "$file" == *项目* ]] || [[ "$file" == *报告* ]] || [[ "$file" == *研报* ]] || \
                   [[ "$file" == *方案* ]] || [[ "$file" == *设计* ]] || [[ "$file" == *手册* ]] || \
                   [[ "$file" == *指南* ]] || [[ "$file" == *调研* ]] || [[ "$file" == *模版* ]] || \
                   [[ "$file" == *模板* ]] || [[ "$file" == *行程* ]] || [[ "$file" == *旅行* ]] || \
                   [[ "$file" == *旅游* ]] || [[ "$file" == *酒店* ]] || [[ "$file" == *机票* ]] || \
                   [[ "$file" == *会议* ]] || [[ "$file" == *日程* ]] || [[ "$file" == cs336* ]] || \
                   [[ "$file" == *cs336* ]] || [[ "$file" == *Cursor* ]] || [[ "$file" == *附加题* ]] || \
                   [[ "$file" == *San* ]] || [[ "$file" == report* ]] || [[ "$file" == *report* ]] || \
                   [[ "$file" == *Index* ]] || [[ "$file" == *Quality* ]] || [[ "$file" == *操作* ]] || \
                   [[ "$file" == *流程* ]] || [[ "$file" == README* ]]; then
                    dest="03-work-docs"
                # 带数字ID的票据/报销类PDF
                elif [[ "$file" =~ ^[0-9]{10,} ]] || [[ "$file" == *Grant_Record* ]]; then
                    dest="09-personal"
                else
                    dest="03-work-docs"  # 默认归入工作文档
                fi
                ;;

            # 其他未知扩展名
            *)
                # 无扩展名的可执行文件
                if [[ -x "$file" ]]; then
                    dest="01-installers"
                else
                    dest="_trash"
                fi
                ;;
        esac
    fi

    # 移动文件
    if [ -n "$dest" ] && [ -f "$file" ]; then
        mv "$file" "$dest/" 2>/dev/null && {
            ((moved++))
        }
    fi
done

echo ""
echo "=========================================="
echo "📊 整理完成！移动了 $moved 个文件"
echo "=========================================="
echo ""

# 统计
echo "📁 各目录文件数量："
for dir in 01-installers 02-resumes 03-work-docs 04-data 05-media 06-archives 07-dev 08-patents 09-personal _trash; do
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

# 清理空的旧目录
rmdir work development learning media personal _inbox 2>/dev/null

echo ""
echo "✨ Done! 打开 Finder 查看..."
open ~/Downloads
