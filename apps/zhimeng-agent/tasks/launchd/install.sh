#!/bin/bash
# zhimeng-agent 定时任务安装脚本
# 将 launchd plist 文件安装到系统并启用

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 确保 LaunchAgents 目录存在
mkdir -p "$LAUNCH_AGENTS_DIR"

# 确保 logs 目录存在
mkdir -p "$PROJECT_ROOT/logs"
log_info "日志目录已就绪: $PROJECT_ROOT/logs"

# 定时任务列表
TASKS=(
    "com.zhimeng.daily-report"
    "com.zhimeng.email-organizer"
    "com.zhimeng.desktop-organizer"
    "com.zhimeng.tech-news"
)

install_task() {
    local task_name=$1
    local plist_file="$SCRIPT_DIR/${task_name}.plist"
    local target_file="$LAUNCH_AGENTS_DIR/${task_name}.plist"

    if [[ ! -f "$plist_file" ]]; then
        log_error "plist 文件不存在: $plist_file"
        return 1
    fi

    # 如果已加载，先卸载
    if launchctl list | grep -q "$task_name"; then
        log_warn "任务 $task_name 已存在，先卸载..."
        launchctl unload "$target_file" 2>/dev/null || true
    fi

    # 复制 plist 文件（使用复制而非软链接，更稳定）
    cp "$plist_file" "$target_file"
    log_info "已安装: $target_file"

    # 加载任务
    launchctl load "$target_file"
    log_info "已加载: $task_name"
}

uninstall_task() {
    local task_name=$1
    local target_file="$LAUNCH_AGENTS_DIR/${task_name}.plist"

    if [[ -f "$target_file" ]]; then
        launchctl unload "$target_file" 2>/dev/null || true
        rm -f "$target_file"
        log_info "已卸载: $task_name"
    else
        log_warn "任务未安装: $task_name"
    fi
}

show_status() {
    echo ""
    echo "========== 定时任务状态 =========="
    for task in "${TASKS[@]}"; do
        if launchctl list | grep -q "$task"; then
            echo -e "  ${GREEN}●${NC} $task (已加载)"
        else
            echo -e "  ${RED}○${NC} $task (未加载)"
        fi
    done
    echo ""
    echo "========== 调度时间 =========="
    echo "  com.zhimeng.daily-report     : 每天 00:00"
    echo "  com.zhimeng.email-organizer  : 每天 02:00"
    echo "  com.zhimeng.desktop-organizer: 每天 04:00"
    echo "  com.zhimeng.tech-news        : 每天 07:00"
    echo ""
}

run_task_now() {
    local task_name=$1
    log_info "立即执行任务: $task_name"
    launchctl start "$task_name"
}

case "${1:-install}" in
    install)
        log_info "开始安装定时任务..."
        for task in "${TASKS[@]}"; do
            install_task "$task"
        done
        show_status
        log_info "安装完成！"
        ;;
    uninstall)
        log_info "开始卸载定时任务..."
        for task in "${TASKS[@]}"; do
            uninstall_task "$task"
        done
        log_info "卸载完成！"
        ;;
    status)
        show_status
        ;;
    run)
        if [[ -z "$2" ]]; then
            log_error "请指定任务名，例如: ./install.sh run daily-report"
            echo "可用任务: daily-report, email-organizer, desktop-organizer, tech-news"
            exit 1
        fi
        run_task_now "com.zhimeng.$2"
        ;;
    *)
        echo "用法: $0 {install|uninstall|status|run <task-name>}"
        echo ""
        echo "命令:"
        echo "  install    - 安装并启用所有定时任务"
        echo "  uninstall  - 卸载所有定时任务"
        echo "  status     - 显示任务状态"
        echo "  run <name> - 立即执行指定任务"
        echo ""
        echo "示例:"
        echo "  $0 install"
        echo "  $0 run daily-report"
        echo "  $0 status"
        exit 1
        ;;
esac
