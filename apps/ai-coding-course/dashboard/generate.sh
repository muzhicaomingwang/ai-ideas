#!/bin/bash

# Claude Code Dashboard - Data Generator
# Reads ~/.claude/ data and generates index.html with inlined data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
OUTPUT_FILE="$SCRIPT_DIR/index.html"

echo "=== Claude Code Dashboard Generator ==="
echo "Data source: $CLAUDE_DIR"
echo "Output: $OUTPUT_FILE"
echo ""

# Check if data exists
if [ ! -f "$CLAUDE_DIR/stats-cache.json" ]; then
    echo "Error: $CLAUDE_DIR/stats-cache.json not found"
    exit 1
fi

# Read stats-cache.json
STATS_DATA=$(cat "$CLAUDE_DIR/stats-cache.json")

# Count skills from settings.json
SKILLS_COUNT=0
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    SKILLS_COUNT=$(python3 -c "
import json
with open('$CLAUDE_DIR/settings.json') as f:
    data = json.load(f)
    permissions = data.get('permissions', {})
    allow = permissions.get('allow', [])
    print(len(allow))
" 2>/dev/null || echo "0")
fi

# Count projects
PROJECTS_COUNT=0
if [ -d "$CLAUDE_DIR/projects" ]; then
    PROJECTS_COUNT=$(ls -d "$CLAUDE_DIR/projects"/*/ 2>/dev/null | wc -l | tr -d ' ')
fi

echo "Stats loaded:"
echo "  - Skills: $SKILLS_COUNT"
echo "  - Projects: $PROJECTS_COUNT"
echo ""

# Generate HTML
cat > "$OUTPUT_FILE" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0f0f23;
            color: #ffffff;
            min-height: 100vh;
            padding: 24px;
        }

        .header {
            text-align: center;
            margin-bottom: 32px;
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        .header .subtitle {
            color: #a0a0c0;
            font-size: 0.95rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: rgba(30, 30, 60, 0.6);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: rgba(102, 126, 234, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
        }

        .stat-card .label {
            font-size: 0.85rem;
            color: #a0a0c0;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-card .value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-card .unit {
            font-size: 0.9rem;
            color: #a0a0c0;
            margin-top: 4px;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .chart-card {
            background: rgba(30, 30, 60, 0.6);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 20px;
        }

        .chart-card .title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: #ffffff;
        }

        .chart-container {
            width: 100%;
            height: 300px;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        .full-width .chart-container {
            height: 250px;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #606080;
            font-size: 0.85rem;
        }

        .footer a {
            color: #667eea;
            text-decoration: none;
        }

        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }

            .stat-card .value {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Claude Code Dashboard</h1>
        <p class="subtitle">本地使用数据可视化 · 数据来源: ~/.claude/</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">总会话数</div>
            <div class="value" id="totalSessions">-</div>
        </div>
        <div class="stat-card">
            <div class="label">总消息数</div>
            <div class="value" id="totalMessages">-</div>
        </div>
        <div class="stat-card">
            <div class="label">最长会话</div>
            <div class="value" id="longestSession">-</div>
            <div class="unit">消息</div>
        </div>
        <div class="stat-card">
            <div class="label">Token 消耗</div>
            <div class="value" id="totalTokens">-</div>
            <div class="unit" id="tokenUnit">tokens</div>
        </div>
        <div class="stat-card">
            <div class="label">Skills</div>
            <div class="value" id="skillsCount">-</div>
        </div>
        <div class="stat-card">
            <div class="label">项目</div>
            <div class="value" id="projectsCount">-</div>
        </div>
    </div>

    <div class="charts-grid">
        <div class="chart-card">
            <div class="title">每日活动趋势</div>
            <div class="chart-container" id="dailyActivityChart"></div>
        </div>
        <div class="chart-card">
            <div class="title">Token 消耗趋势</div>
            <div class="chart-container" id="tokenTrendChart"></div>
        </div>
        <div class="chart-card">
            <div class="title">模型使用分布</div>
            <div class="chart-container" id="modelDistributionChart"></div>
        </div>
        <div class="chart-card full-width">
            <div class="title">活跃时段分布</div>
            <div class="chart-container" id="hourlyActivityChart"></div>
        </div>
    </div>

    <div class="footer">
        Generated by <a href="https://claude.ai/code" target="_blank">Claude Code</a> ·
        Last updated: <span id="lastUpdated">-</span>
    </div>

    <script>
        // Inline data (generated by generate.sh)
        const STATS_DATA = __STATS_DATA_PLACEHOLDER__;
        const SKILLS_COUNT = __SKILLS_COUNT_PLACEHOLDER__;
        const PROJECTS_COUNT = __PROJECTS_COUNT_PLACEHOLDER__;

        // Helper functions
        function formatNumber(num) {
            if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B';
            if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toLocaleString();
        }

        function formatTokens(num) {
            if (num >= 1000000000) return { value: (num / 1000000000).toFixed(2), unit: 'B tokens' };
            if (num >= 1000000) return { value: (num / 1000000).toFixed(2), unit: 'M tokens' };
            if (num >= 1000) return { value: (num / 1000).toFixed(1), unit: 'K tokens' };
            return { value: num.toLocaleString(), unit: 'tokens' };
        }

        function getModelShortName(fullName) {
            const mapping = {
                'claude-opus-4-1-20250805': 'Opus 4.1',
                'claude-opus-4-5-20251101': 'Opus 4.5',
                'claude-sonnet-4-20250514': 'Sonnet 4',
                'claude-sonnet-4-5-20250929': 'Sonnet 4.5'
            };
            return mapping[fullName] || fullName.split('-').slice(1, 3).join(' ');
        }

        // Calculate stats
        const totalSessions = STATS_DATA.totalSessions || 0;
        const totalMessages = STATS_DATA.totalMessages || 0;
        const longestSession = STATS_DATA.longestSession?.messageCount || 0;

        // Calculate total tokens
        let totalTokens = 0;
        if (STATS_DATA.modelUsage) {
            Object.values(STATS_DATA.modelUsage).forEach(model => {
                totalTokens += (model.inputTokens || 0) + (model.outputTokens || 0);
            });
        }

        // Update stat cards
        document.getElementById('totalSessions').textContent = formatNumber(totalSessions);
        document.getElementById('totalMessages').textContent = formatNumber(totalMessages);
        document.getElementById('longestSession').textContent = formatNumber(longestSession);

        const tokenFormatted = formatTokens(totalTokens);
        document.getElementById('totalTokens').textContent = tokenFormatted.value;
        document.getElementById('tokenUnit').textContent = tokenFormatted.unit;

        document.getElementById('skillsCount').textContent = formatNumber(SKILLS_COUNT);
        document.getElementById('projectsCount').textContent = formatNumber(PROJECTS_COUNT);
        document.getElementById('lastUpdated').textContent = new Date().toLocaleDateString('zh-CN');

        // ECharts theme colors
        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

        // Chart 1: Daily Activity Trend
        const dailyActivityChart = echarts.init(document.getElementById('dailyActivityChart'));
        const dailyActivity = STATS_DATA.dailyActivity || [];
        const sortedDailyActivity = [...dailyActivity].sort((a, b) => new Date(a.date) - new Date(b.date));

        dailyActivityChart.setOption({
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(30, 30, 60, 0.95)',
                borderColor: 'rgba(102, 126, 234, 0.3)',
                textStyle: { color: '#fff' }
            },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'category',
                data: sortedDailyActivity.map(d => d.date.slice(5)),
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: { color: '#a0a0c0', fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: { color: '#a0a0c0' },
                splitLine: { lineStyle: { color: '#252540' } }
            },
            series: [{
                name: '消息数',
                type: 'line',
                smooth: true,
                data: sortedDailyActivity.map(d => d.messageCount),
                itemStyle: { color: colors[0] },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
                        { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
                    ])
                }
            }]
        });

        // Chart 2: Token Consumption Trend
        const tokenTrendChart = echarts.init(document.getElementById('tokenTrendChart'));
        const dailyModelTokens = STATS_DATA.dailyModelTokens || [];
        const sortedTokenData = [...dailyModelTokens].sort((a, b) => new Date(a.date) - new Date(b.date));

        // Aggregate daily tokens
        const dailyTotals = sortedTokenData.map(d => {
            let total = 0;
            if (d.tokensByModel) {
                Object.values(d.tokensByModel).forEach(v => total += v);
            }
            return { date: d.date, tokens: total };
        });

        tokenTrendChart.setOption({
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(30, 30, 60, 0.95)',
                borderColor: 'rgba(102, 126, 234, 0.3)',
                textStyle: { color: '#fff' },
                formatter: function(params) {
                    const value = params[0].value;
                    return `${params[0].axisValue}<br/>Tokens: ${formatNumber(value)}`;
                }
            },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'category',
                data: dailyTotals.map(d => d.date.slice(5)),
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: { color: '#a0a0c0', fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: {
                    color: '#a0a0c0',
                    formatter: function(value) {
                        if (value >= 1000000) return (value / 1000000).toFixed(0) + 'M';
                        if (value >= 1000) return (value / 1000).toFixed(0) + 'K';
                        return value;
                    }
                },
                splitLine: { lineStyle: { color: '#252540' } }
            },
            series: [{
                name: 'Tokens',
                type: 'bar',
                data: dailyTotals.map(d => d.tokens),
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#764ba2' },
                        { offset: 1, color: '#667eea' }
                    ])
                }
            }]
        });

        // Chart 3: Model Usage Distribution
        const modelDistributionChart = echarts.init(document.getElementById('modelDistributionChart'));
        const modelUsage = STATS_DATA.modelUsage || {};
        const modelData = Object.entries(modelUsage).map(([name, data]) => ({
            name: getModelShortName(name),
            value: (data.inputTokens || 0) + (data.outputTokens || 0)
        })).filter(d => d.value > 0);

        modelDistributionChart.setOption({
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(30, 30, 60, 0.95)',
                borderColor: 'rgba(102, 126, 234, 0.3)',
                textStyle: { color: '#fff' },
                formatter: function(params) {
                    return `${params.name}<br/>Tokens: ${formatNumber(params.value)} (${params.percent}%)`;
                }
            },
            legend: {
                orient: 'vertical',
                right: '5%',
                top: 'center',
                textStyle: { color: '#a0a0c0' }
            },
            series: [{
                name: '模型使用',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['35%', '50%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 8,
                    borderColor: '#0f0f23',
                    borderWidth: 2
                },
                label: { show: false },
                emphasis: {
                    label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' }
                },
                labelLine: { show: false },
                data: modelData,
                color: colors
            }]
        });

        // Chart 4: Hourly Activity Distribution
        const hourlyActivityChart = echarts.init(document.getElementById('hourlyActivityChart'));
        const hourCounts = STATS_DATA.hourCounts || {};
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const hourlyData = hours.map(h => hourCounts[h.toString()] || 0);

        hourlyActivityChart.setOption({
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(30, 30, 60, 0.95)',
                borderColor: 'rgba(102, 126, 234, 0.3)',
                textStyle: { color: '#fff' },
                formatter: function(params) {
                    return `${params[0].axisValue}:00<br/>会话数: ${params[0].value}`;
                }
            },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: {
                type: 'category',
                data: hours.map(h => h.toString().padStart(2, '0')),
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: { color: '#a0a0c0' }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#404060' } },
                axisLabel: { color: '#a0a0c0' },
                splitLine: { lineStyle: { color: '#252540' } }
            },
            series: [{
                name: '会话数',
                type: 'bar',
                data: hourlyData,
                itemStyle: {
                    color: function(params) {
                        // Highlight peak hours
                        const value = params.value;
                        const max = Math.max(...hourlyData);
                        const ratio = value / max;
                        if (ratio > 0.7) return '#764ba2';
                        if (ratio > 0.4) return '#667eea';
                        return '#4a5568';
                    },
                    borderRadius: [4, 4, 0, 0]
                }
            }]
        });

        // Responsive resize
        window.addEventListener('resize', function() {
            dailyActivityChart.resize();
            tokenTrendChart.resize();
            modelDistributionChart.resize();
            hourlyActivityChart.resize();
        });
    </script>
</body>
</html>
HTMLEOF

# Replace placeholders with actual data
# Use Python for reliable JSON handling
python3 << PYEOF
import json
import re

with open('$OUTPUT_FILE', 'r') as f:
    html = f.read()

# Stats data
stats_data = '''$STATS_DATA'''

# Replace placeholders
html = html.replace('__STATS_DATA_PLACEHOLDER__', stats_data)
html = html.replace('__SKILLS_COUNT_PLACEHOLDER__', '$SKILLS_COUNT')
html = html.replace('__PROJECTS_COUNT_PLACEHOLDER__', '$PROJECTS_COUNT')

with open('$OUTPUT_FILE', 'w') as f:
    f.write(html)

print("HTML generated successfully!")
PYEOF

echo ""
echo "=== Done! ==="
echo "Open in browser: open $OUTPUT_FILE"
