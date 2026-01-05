#!/usr/bin/env node
/**
 * Design Tokens Transform Script
 * 将 tokens.json 转换为小程序可用的 WXSS 变量
 *
 * 使用方法: node transform.js
 */

const fs = require('fs');
const path = require('path');

// 读取 tokens
const tokensPath = path.join(__dirname, 'tokens.json');
const tokens = JSON.parse(fs.readFileSync(tokensPath, 'utf8'));

// 解析 Token 引用 (如 {global.colors.primary})
function resolveReference(value, allTokens) {
  if (typeof value !== 'string') return value;

  const refMatch = value.match(/^\{(.+)\}$/);
  if (!refMatch) return value;

  const refPath = refMatch[1].split('.');
  let resolved = allTokens;

  for (const key of refPath) {
    if (resolved && resolved[key]) {
      resolved = resolved[key];
    } else {
      return value; // 无法解析，返回原值
    }
  }

  return resolved.value || resolved;
}

// 将 Token 路径转换为 CSS 变量名
function tokenToCssVar(path) {
  return '--' + path.join('-').toLowerCase();
}

// 递归遍历 tokens 生成变量
function flattenTokens(obj, parentPath = [], result = {}, allTokens = tokens) {
  for (const [key, value] of Object.entries(obj)) {
    // 跳过元数据字段
    if (key.startsWith('$')) continue;

    const currentPath = [...parentPath, key];

    if (value && typeof value === 'object' && 'value' in value) {
      // 这是一个 token
      const cssVarName = tokenToCssVar(currentPath);
      const resolvedValue = resolveReference(value.value, allTokens);
      result[cssVarName] = {
        value: resolvedValue,
        description: value.description || ''
      };
    } else if (value && typeof value === 'object') {
      // 继续递归
      flattenTokens(value, currentPath, result, allTokens);
    }
  }

  return result;
}

// 生成 WXSS 内容
function generateWXSS(flatTokens) {
  let wxss = `/**
 * TeamVenture Design Tokens
 * 自动生成，请勿手动修改
 * 生成时间: ${new Date().toISOString()}
 *
 * 使用方法:
 * @import './design-tokens/variables.wxss';
 */

page {
`;

  // 按类别分组
  const categories = {
    'global-colors': [],
    'global-neutrals': [],
    'global-typography': [],
    'global-spacing': [],
    'global-borderradius': [],
    'global-shadows': [],
    'components': [],
    'pages': []
  };

  for (const [varName, data] of Object.entries(flatTokens)) {
    if (varName.startsWith('--global-colors')) {
      categories['global-colors'].push({ varName, ...data });
    } else if (varName.startsWith('--global-neutrals')) {
      categories['global-neutrals'].push({ varName, ...data });
    } else if (varName.startsWith('--global-typography')) {
      categories['global-typography'].push({ varName, ...data });
    } else if (varName.startsWith('--global-spacing')) {
      categories['global-spacing'].push({ varName, ...data });
    } else if (varName.startsWith('--global-borderradius')) {
      categories['global-borderradius'].push({ varName, ...data });
    } else if (varName.startsWith('--global-shadows')) {
      categories['global-shadows'].push({ varName, ...data });
    } else if (varName.startsWith('--components')) {
      categories['components'].push({ varName, ...data });
    } else if (varName.startsWith('--pages')) {
      categories['pages'].push({ varName, ...data });
    }
  }

  // 生成分类注释和变量
  const categoryLabels = {
    'global-colors': '颜色系统',
    'global-neutrals': '中性色',
    'global-typography': '字体排版',
    'global-spacing': '间距',
    'global-borderradius': '圆角',
    'global-shadows': '阴影',
    'components': '组件',
    'pages': '页面'
  };

  for (const [category, items] of Object.entries(categories)) {
    if (items.length === 0) continue;

    wxss += `\n  /* ========== ${categoryLabels[category]} ========== */\n`;

    for (const { varName, value, description } of items) {
      if (description) {
        wxss += `  /* ${description} */\n`;
      }
      wxss += `  ${varName}: ${value};\n`;
    }
  }

  wxss += `}

/* ========== 便捷类 ========== */

/* 主色按钮 */
.btn-primary {
  background-color: var(--global-colors-primary);
  color: #ffffff;
  border-radius: var(--global-borderradius-lg);
}

/* 次要按钮 */
.btn-secondary {
  background-color: var(--global-neutrals-card);
  color: var(--global-colors-primary);
  border: 2rpx solid var(--global-colors-primary);
  border-radius: var(--global-borderradius-lg);
}

/* 危险按钮 */
.btn-danger {
  background-color: var(--global-colors-danger);
  color: #ffffff;
  border-radius: var(--global-borderradius-lg);
}

/* 卡片样式 */
.card {
  background-color: var(--global-neutrals-card);
  border-radius: var(--global-borderradius-lg);
  box-shadow: var(--global-shadows-base);
  padding: var(--global-spacing-base);
}

/* 状态标签 */
.status-generating {
  background-color: var(--global-colors-primary-light);
  color: var(--global-colors-primary);
}

.status-completed {
  background-color: var(--global-colors-success-light);
  color: var(--global-colors-success);
}

.status-failed {
  background-color: var(--global-colors-danger-light);
  color: var(--global-colors-danger);
}
`;

  return wxss;
}

// 生成 JS 常量文件（用于 JS 中引用）
function generateJS(flatTokens) {
  let js = `/**
 * TeamVenture Design Tokens
 * 自动生成，请勿手动修改
 * 生成时间: ${new Date().toISOString()}
 */

const DESIGN_TOKENS = {
`;

  for (const [varName, data] of Object.entries(flatTokens)) {
    const jsKey = varName
      .replace(/^--/, '')
      .replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());

    js += `  ${jsKey}: '${data.value}',\n`;
  }

  js += `};

module.exports = DESIGN_TOKENS;
`;

  return js;
}

// 主函数
function main() {
  console.log('🎨 Design Tokens Transform');
  console.log('==========================\n');

  // 展平 tokens
  const flatTokens = flattenTokens(tokens);
  console.log(`✓ 解析了 ${Object.keys(flatTokens).length} 个 Token\n`);

  // 生成 WXSS
  const wxss = generateWXSS(flatTokens);
  const wxssPath = path.join(__dirname, 'variables.wxss');
  fs.writeFileSync(wxssPath, wxss);
  console.log(`✓ 生成 WXSS: ${wxssPath}`);

  // 生成 JS
  const js = generateJS(flatTokens);
  const jsPath = path.join(__dirname, 'tokens.js');
  fs.writeFileSync(jsPath, js);
  console.log(`✓ 生成 JS:   ${jsPath}`);

  console.log('\n🎉 完成！');
  console.log('\n使用方法:');
  console.log('  WXSS: @import \'./design-tokens/variables.wxss\';');
  console.log('  JS:   const tokens = require(\'./design-tokens/tokens.js\');');
}

main();
