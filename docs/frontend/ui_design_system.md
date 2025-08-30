# SaaS 数据分析平台 UI 设计系统规范

## 概览

本文档定义了企业级SaaS数据分析平台的完整UI设计系统，基于现代设计理念和快速开发需求，确保界面的一致性、可访问性和实现效率。

## 核心设计原则

### 1. 设计哲学
- **专业可信**: 企业级产品的权威感和可信度
- **数据驱动**: 突出数据可视化和分析能力
- **高效操作**: 优化用户工作流程，减少操作步骤
- **响应式设计**: 完美适配桌面、平板、移动设备
- **可访问性优先**: WCAG 2.1 AA级别合规

### 2. 快速开发原则
- **组件复用**: 一次设计，多处使用
- **Tailwind优先**: 使用标准类名快速实现
- **渐进增强**: 核心功能优先，装饰效果后加
- **平台原生**: 尊重各平台设计规范

---

## 色彩系统

### 主色调 - 橙色到粉色渐变主题

```css
/* 主品牌色彩 */
:root {
  /* Primary Gradient - 橙粉渐变 */
  --gradient-primary: linear-gradient(135deg, #ff6b35 0%, #f7931e 25%, #ff8a80 75%, #ff5722 100%);
  --gradient-primary-hover: linear-gradient(135deg, #e55722 0%, #de7d0a 25%, #e57570 75%, #e64a19 100%);
  
  /* Secondary Gradient - 深度变化 */
  --gradient-secondary: linear-gradient(135deg, #ff8a65 0%, #ffab91 100%);
  --gradient-accent: linear-gradient(135deg, #ff7043 0%, #ff5722 100%);
  
  /* 固体颜色值 */
  --color-primary: #ff6b35;
  --color-primary-light: #ff8a65;
  --color-primary-dark: #e64a19;
  --color-secondary: #ff5722;
  --color-accent: #f7931e;
}
```

### 语义化颜色

```css
/* 状态颜色 */
:root {
  --color-success: #10b981;
  --color-success-light: #34d399;
  --color-success-dark: #059669;
  --color-success-bg: #ecfdf5;
  
  --color-warning: #f59e0b;
  --color-warning-light: #fbbf24;
  --color-warning-dark: #d97706;
  --color-warning-bg: #fffbeb;
  
  --color-error: #ef4444;
  --color-error-light: #f87171;
  --color-error-dark: #dc2626;
  --color-error-bg: #fef2f2;
  
  --color-info: #3b82f6;
  --color-info-light: #60a5fa;
  --color-info-dark: #2563eb;
  --color-info-bg: #eff6ff;
}
```

### 中性色系

```css
/* 中性色板 */
:root {
  --color-white: #ffffff;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  --color-black: #000000;
}
```

### 数据可视化色板

```css
/* 图表专用色板 */
:root {
  --chart-color-1: #ff6b35;
  --chart-color-2: #3b82f6;
  --chart-color-3: #10b981;
  --chart-color-4: #f59e0b;
  --chart-color-5: #8b5cf6;
  --chart-color-6: #ef4444;
  --chart-color-7: #06b6d4;
  --chart-color-8: #84cc16;
}
```

---

## 字体系统

### 字体族

```css
:root {
  /* 主字体 - 无衬线体 */
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
  
  /* 等宽字体 - 代码和数字 */
  --font-family-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, 'Cascadia Code', monospace;
  
  /* 中文字体支持 */
  --font-family-chinese: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
```

### 字体尺寸和行高

```css
/* 字体层级系统 */
:root {
  /* Display - 英雄标题 */
  --text-display: 3rem;      /* 48px */
  --text-display-lh: 1.1;
  
  /* H1 - 页面标题 */
  --text-h1: 2.25rem;        /* 36px */
  --text-h1-lh: 1.2;
  
  /* H2 - 章节标题 */
  --text-h2: 1.875rem;       /* 30px */
  --text-h2-lh: 1.3;
  
  /* H3 - 子章节标题 */
  --text-h3: 1.5rem;         /* 24px */
  --text-h3-lh: 1.4;
  
  /* H4 - 卡片标题 */
  --text-h4: 1.25rem;        /* 20px */
  --text-h4-lh: 1.4;
  
  /* Body Large - 重要正文 */
  --text-lg: 1.125rem;       /* 18px */
  --text-lg-lh: 1.5;
  
  /* Body - 默认正文 */
  --text-base: 1rem;         /* 16px */
  --text-base-lh: 1.5;
  
  /* Small - 辅助文字 */
  --text-sm: 0.875rem;       /* 14px */
  --text-sm-lh: 1.4;
  
  /* Extra Small - 标签说明 */
  --text-xs: 0.75rem;        /* 12px */
  --text-xs-lh: 1.3;
}
```

### 字重系统

```css
:root {
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
}
```

---

## 间距系统

### 基础间距

```css
/* 8px基础间距系统 */
:root {
  --space-0: 0;
  --space-px: 1px;
  --space-0_5: 0.125rem;     /* 2px */
  --space-1: 0.25rem;        /* 4px */
  --space-1_5: 0.375rem;     /* 6px */
  --space-2: 0.5rem;         /* 8px */
  --space-2_5: 0.625rem;     /* 10px */
  --space-3: 0.75rem;        /* 12px */
  --space-3_5: 0.875rem;     /* 14px */
  --space-4: 1rem;           /* 16px */
  --space-5: 1.25rem;        /* 20px */
  --space-6: 1.5rem;         /* 24px */
  --space-7: 1.75rem;        /* 28px */
  --space-8: 2rem;           /* 32px */
  --space-10: 2.5rem;        /* 40px */
  --space-12: 3rem;          /* 48px */
  --space-16: 4rem;          /* 64px */
  --space-20: 5rem;          /* 80px */
  --space-24: 6rem;          /* 96px */
  --space-32: 8rem;          /* 128px */
}
```

### 组件间距

```css
/* 组件专用间距 */
:root {
  --spacing-component-xs: var(--space-2);   /* 组件内部小间距 */
  --spacing-component-sm: var(--space-4);   /* 组件内部标准间距 */
  --spacing-component-md: var(--space-6);   /* 组件间距 */
  --spacing-component-lg: var(--space-8);   /* 区块间距 */
  --spacing-component-xl: var(--space-12);  /* 页面区域间距 */
}
```

---

## 圆角系统

```css
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;      /* 2px */
  --radius-base: 0.25rem;     /* 4px */
  --radius-md: 0.375rem;      /* 6px */
  --radius-lg: 0.5rem;        /* 8px */
  --radius-xl: 0.75rem;       /* 12px */
  --radius-2xl: 1rem;         /* 16px */
  --radius-3xl: 1.5rem;       /* 24px */
  --radius-full: 9999px;      /* 完全圆角 */
}
```

---

## 阴影系统

```css
:root {
  /* 卡片阴影 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  /* 内阴影 */
  --shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
  
  /* 彩色阴影 - 品牌色 */
  --shadow-primary: 0 4px 14px 0 rgb(255 107 53 / 0.2);
  --shadow-primary-lg: 0 10px 25px -5px rgb(255 107 53 / 0.25);
}
```

---

## 组件系统

### 1. 按钮组件

#### 主要按钮 (Primary Button)

```css
.btn-primary {
  /* 基础样式 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--text-base-lh);
  border-radius: var(--radius-lg);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  
  /* 主要按钮样式 */
  background: var(--gradient-primary);
  color: var(--color-white);
  box-shadow: var(--shadow-primary);
  
  /* 鼠标悬停 */
  &:hover {
    background: var(--gradient-primary-hover);
    box-shadow: var(--shadow-primary-lg);
    transform: translateY(-1px);
  }
  
  /* 激活状态 */
  &:active {
    transform: translateY(0);
    box-shadow: var(--shadow-base);
  }
  
  /* 禁用状态 */
  &:disabled {
    background: var(--color-gray-300);
    color: var(--color-gray-500);
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
  }
  
  /* 加载状态 */
  &.loading {
    position: relative;
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 16px;
      height: 16px;
      border: 2px solid transparent;
      border-top: 2px solid currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  }
}
```

#### 次要按钮 (Secondary Button)

```css
.btn-secondary {
  /* 继承基础样式 */
  @extend .btn-primary;
  
  /* 次要按钮样式 */
  background: var(--color-white);
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  box-shadow: var(--shadow-base);
  
  &:hover {
    background: var(--color-primary);
    color: var(--color-white);
    border-color: var(--color-primary);
  }
}
```

#### 按钮尺寸变化

```css
/* 小尺寸按钮 */
.btn-sm {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  border-radius: var(--radius-base);
}

/* 大尺寸按钮 */
.btn-lg {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
  border-radius: var(--radius-xl);
}

/* 全宽按钮 */
.btn-full {
  width: 100%;
}
```

### 2. 输入框组件

#### 基础输入框

```css
.input-base {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  font-family: var(--font-family-sans);
  color: var(--color-gray-900);
  background: var(--color-white);
  border: 2px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease-in-out;
  
  /* 占位符样式 */
  &::placeholder {
    color: var(--color-gray-400);
  }
  
  /* 聚焦状态 */
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgb(255 107 53 / 0.1);
  }
  
  /* 错误状态 */
  &.error {
    border-color: var(--color-error);
    
    &:focus {
      border-color: var(--color-error);
      box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
    }
  }
  
  /* 成功状态 */
  &.success {
    border-color: var(--color-success);
    
    &:focus {
      border-color: var(--color-success);
      box-shadow: 0 0 0 3px rgb(16 185 129 / 0.1);
    }
  }
  
  /* 禁用状态 */
  &:disabled {
    background: var(--color-gray-50);
    color: var(--color-gray-400);
    cursor: not-allowed;
  }
}
```

#### 搜索输入框

```css
.input-search {
  @extend .input-base;
  padding-left: var(--space-10);
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z'/%3e%3c/svg%3e");
  background-position: left var(--space-3) center;
  background-repeat: no-repeat;
  background-size: 16px;
}
```

### 3. 卡片组件

#### 基础卡片

```css
.card {
  background: var(--color-white);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-base);
  border: 1px solid var(--color-gray-100);
  overflow: hidden;
  transition: all 0.2s ease-in-out;
  
  /* 悬停效果 */
  &:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
  }
}

.card-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-gray-100);
  
  .card-title {
    font-size: var(--text-h4);
    font-weight: var(--font-semibold);
    color: var(--color-gray-900);
    margin: 0;
  }
  
  .card-subtitle {
    font-size: var(--text-sm);
    color: var(--color-gray-500);
    margin-top: var(--space-1);
  }
}

.card-body {
  padding: var(--space-6);
}

.card-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-gray-100);
  background: var(--color-gray-50);
}
```

#### 数据卡片

```css
.card-metric {
  @extend .card;
  
  .metric-value {
    font-size: var(--text-display);
    font-weight: var(--font-bold);
    color: var(--color-gray-900);
    font-family: var(--font-family-mono);
  }
  
  .metric-label {
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--color-gray-600);
    margin-top: var(--space-2);
  }
  
  .metric-change {
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
    display: flex;
    align-items: center;
    gap: var(--space-1);
    margin-top: var(--space-1);
    
    &.positive {
      color: var(--color-success);
    }
    
    &.negative {
      color: var(--color-error);
    }
  }
}
```

### 4. 导航组件

#### 侧边栏导航

```css
.sidebar {
  width: 280px;
  height: 100vh;
  background: var(--color-white);
  border-right: 1px solid var(--color-gray-200);
  box-shadow: var(--shadow-lg);
  position: fixed;
  left: 0;
  top: 0;
  transition: transform 0.3s ease-in-out;
  z-index: 40;
  
  /* 折叠状态 */
  &.collapsed {
    transform: translateX(-240px);
    width: 80px;
  }
  
  /* 移动端隐藏 */
  @media (max-width: 768px) {
    transform: translateX(-100%);
    
    &.open {
      transform: translateX(0);
    }
  }
}

.sidebar-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-gray-200);
  
  .logo {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: var(--text-h4);
    font-weight: var(--font-bold);
    color: var(--color-gray-900);
    
    .logo-icon {
      width: 32px;
      height: 32px;
      background: var(--gradient-primary);
      border-radius: var(--radius-lg);
    }
  }
}

.sidebar-nav {
  padding: var(--space-4) 0;
  
  .nav-section {
    margin-bottom: var(--space-6);
    
    .section-title {
      padding: 0 var(--space-6);
      font-size: var(--text-xs);
      font-weight: var(--font-semibold);
      color: var(--color-gray-400);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: var(--space-3);
    }
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    padding: var(--space-3) var(--space-6);
    font-size: var(--text-base);
    font-weight: var(--font-medium);
    color: var(--color-gray-600);
    text-decoration: none;
    transition: all 0.2s ease-in-out;
    position: relative;
    
    /* 图标 */
    .nav-icon {
      width: 20px;
      height: 20px;
      margin-right: var(--space-3);
      opacity: 0.7;
    }
    
    /* 徽章 */
    .nav-badge {
      margin-left: auto;
      background: var(--color-gray-200);
      color: var(--color-gray-600);
      font-size: var(--text-xs);
      font-weight: var(--font-semibold);
      padding: var(--space-1) var(--space-2);
      border-radius: var(--radius-full);
      min-width: 20px;
      text-align: center;
    }
    
    /* 悬停状态 */
    &:hover {
      color: var(--color-primary);
      background: var(--color-gray-50);
      
      .nav-icon {
        opacity: 1;
      }
    }
    
    /* 激活状态 */
    &.active {
      color: var(--color-primary);
      background: var(--color-gray-50);
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--gradient-primary);
      }
      
      .nav-icon {
        opacity: 1;
      }
      
      .nav-badge {
        background: var(--color-primary);
        color: var(--color-white);
      }
    }
  }
}
```

#### 顶部导航栏

```css
.header {
  height: 72px;
  background: var(--gradient-primary);
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  position: sticky;
  top: 0;
  z-index: 30;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    
    .sidebar-toggle {
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      border-radius: var(--radius-lg);
      color: var(--color-white);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
    
    .search-container {
      position: relative;
      
      .search-input {
        width: 320px;
        padding: var(--space-3) var(--space-4);
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-lg);
        color: var(--color-white);
        font-size: var(--text-base);
        
        &::placeholder {
          color: rgba(255, 255, 255, 0.7);
        }
        
        &:focus {
          outline: none;
          background: var(--color-white);
          color: var(--color-gray-900);
          
          &::placeholder {
            color: var(--color-gray-400);
          }
        }
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    
    .notification-btn {
      position: relative;
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      border-radius: var(--radius-lg);
      color: var(--color-white);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .notification-dot {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 8px;
        height: 8px;
        background: var(--color-error);
        border-radius: 50%;
        border: 2px solid var(--color-white);
      }
    }
    
    .user-menu {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-2);
      background: rgba(255, 255, 255, 0.1);
      border-radius: var(--radius-lg);
      cursor: pointer;
      transition: background 0.2s;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
      
      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: var(--radius-full);
        background: var(--color-white);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: var(--font-semibold);
        color: var(--color-primary);
      }
      
      .user-info {
        color: var(--color-white);
        
        .user-name {
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
        }
        
        .user-role {
          font-size: var(--text-xs);
          opacity: 0.8;
        }
      }
    }
  }
}
```

### 5. 表单组件

#### 表单布局

```css
.form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--space-8);
  background: var(--color-white);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-lg);
}

.form-group {
  margin-bottom: var(--space-6);
  
  .form-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--color-gray-700);
    margin-bottom: var(--space-2);
    
    /* 必填标识 */
    .required {
      color: var(--color-error);
      margin-left: var(--space-1);
    }
  }
  
  .form-help {
    font-size: var(--text-xs);
    color: var(--color-gray-500);
    margin-top: var(--space-1);
  }
  
  .form-error {
    font-size: var(--text-xs);
    color: var(--color-error);
    margin-top: var(--space-1);
    display: flex;
    align-items: center;
    gap: var(--space-1);
  }
}
```

#### 文件上传组件

```css
.file-upload {
  border: 2px dashed var(--color-gray-300);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  text-align: center;
  background: var(--color-gray-50);
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  
  /* 拖拽悬停状态 */
  &.drag-over {
    border-color: var(--color-primary);
    background: rgba(255, 107, 53, 0.05);
  }
  
  .upload-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto var(--space-4);
    color: var(--color-gray-400);
  }
  
  .upload-text {
    font-size: var(--text-base);
    color: var(--color-gray-600);
    margin-bottom: var(--space-2);
    
    .upload-link {
      color: var(--color-primary);
      font-weight: var(--font-medium);
    }
  }
  
  .upload-hint {
    font-size: var(--text-xs);
    color: var(--color-gray-400);
  }
}

.file-preview {
  margin-top: var(--space-4);
  
  .file-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    background: var(--color-white);
    border: 1px solid var(--color-gray-200);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-2);
    
    .file-icon {
      width: 32px;
      height: 32px;
      color: var(--color-primary);
    }
    
    .file-info {
      flex: 1;
      
      .file-name {
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--color-gray-900);
      }
      
      .file-size {
        font-size: var(--text-xs);
        color: var(--color-gray-500);
      }
    }
    
    .file-actions {
      display: flex;
      gap: var(--space-2);
      
      .remove-btn {
        width: 24px;
        height: 24px;
        background: none;
        border: none;
        color: var(--color-gray-400);
        cursor: pointer;
        border-radius: var(--radius-base);
        
        &:hover {
          color: var(--color-error);
          background: var(--color-error-bg);
        }
      }
    }
  }
}
```

### 6. 数据表格组件

```css
.table-container {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-base);
  border: 1px solid var(--color-gray-200);
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
  
  .table-header {
    background: var(--color-gray-50);
    
    .table-header-cell {
      padding: var(--space-4) var(--space-6);
      text-align: left;
      font-size: var(--text-xs);
      font-weight: var(--font-semibold);
      color: var(--color-gray-500);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--color-gray-200);
      
      /* 可排序列 */
      &.sortable {
        cursor: pointer;
        user-select: none;
        
        &:hover {
          color: var(--color-gray-700);
        }
        
        /* 排序指示器 */
        &.sort-asc::after {
          content: '↑';
          margin-left: var(--space-2);
        }
        
        &.sort-desc::after {
          content: '↓';
          margin-left: var(--space-2);
        }
      }
    }
  }
  
  .table-body {
    .table-row {
      border-bottom: 1px solid var(--color-gray-200);
      transition: background 0.1s ease;
      
      &:hover {
        background: var(--color-gray-50);
      }
      
      &.selected {
        background: rgba(255, 107, 53, 0.05);
      }
      
      .table-cell {
        padding: var(--space-4) var(--space-6);
        font-size: var(--text-sm);
        color: var(--color-gray-900);
        
        /* 数字列 */
        &.numeric {
          font-family: var(--font-family-mono);
          text-align: right;
        }
        
        /* 状态列 */
        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: var(--space-1);
          padding: var(--space-1) var(--space-2);
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          border-radius: var(--radius-full);
          
          &.success {
            background: var(--color-success-bg);
            color: var(--color-success-dark);
          }
          
          &.warning {
            background: var(--color-warning-bg);
            color: var(--color-warning-dark);
          }
          
          &.error {
            background: var(--color-error-bg);
            color: var(--color-error-dark);
          }
          
          .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: currentColor;
          }
        }
      }
    }
  }
}
```

### 7. 模态框组件

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  backdrop-filter: blur(4px);
  
  /* 动画进入 */
  animation: fadeIn 0.2s ease-out;
}

.modal {
  background: var(--color-white);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  
  /* 动画进入 */
  animation: slideIn 0.3s ease-out;
  
  /* 尺寸变体 */
  &.modal-sm { width: 400px; }
  &.modal-md { width: 600px; }
  &.modal-lg { width: 800px; }
  &.modal-xl { width: 1000px; }
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .modal-title {
    font-size: var(--text-h3);
    font-weight: var(--font-semibold);
    color: var(--color-gray-900);
    margin: 0;
  }
  
  .modal-close {
    width: 40px;
    height: 40px;
    background: none;
    border: none;
    color: var(--color-gray-400);
    cursor: pointer;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      background: var(--color-gray-100);
      color: var(--color-gray-600);
    }
  }
}

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
  max-height: calc(90vh - 140px);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--color-gray-200);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* 动画关键帧 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

---

## 响应式断点系统

```css
/* 响应式断点定义 */
:root {
  --breakpoint-sm: 640px;   /* 小屏手机 */
  --breakpoint-md: 768px;   /* 大屏手机/小平板 */
  --breakpoint-lg: 1024px;  /* 平板/小笔记本 */
  --breakpoint-xl: 1280px;  /* 桌面 */
  --breakpoint-2xl: 1536px; /* 大桌面 */
}

/* 响应式工具类 */
@media (max-width: 639px) {
  .sidebar {
    width: 100vw;
    transform: translateX(-100%);
  }
  
  .header {
    padding: 0 var(--space-4);
    
    .search-container .search-input {
      width: 200px;
    }
  }
  
  .card {
    margin: 0 var(--space-4);
    border-radius: var(--radius-xl);
  }
  
  .modal {
    margin: var(--space-4);
    width: calc(100vw - 2rem);
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 240px;
  }
  
  .main-content {
    margin-left: 240px;
  }
}

@media (min-width: 1024px) {
  .main-content {
    margin-left: 280px;
  }
}
```

---

## 状态和交互

### 加载状态

```css
/* 骨架屏 */
.skeleton {
  background: linear-gradient(90deg, 
    var(--color-gray-200) 25%, 
    var(--color-gray-100) 50%, 
    var(--color-gray-200) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-text {
  height: 1rem;
  border-radius: var(--radius-base);
  margin-bottom: var(--space-2);
  
  &.skeleton-text-sm { height: 0.75rem; }
  &.skeleton-text-lg { height: 1.5rem; }
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
}

.skeleton-card {
  height: 200px;
  border-radius: var(--radius-lg);
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 加载旋转器 */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-gray-200);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 错误状态

```css
.error-container {
  padding: var(--space-8);
  text-align: center;
  
  .error-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto var(--space-4);
    color: var(--color-error);
  }
  
  .error-title {
    font-size: var(--text-h3);
    font-weight: var(--font-semibold);
    color: var(--color-gray-900);
    margin-bottom: var(--space-2);
  }
  
  .error-message {
    font-size: var(--text-base);
    color: var(--color-gray-600);
    margin-bottom: var(--space-6);
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
}
```

### 空状态

```css
.empty-state {
  padding: var(--space-12) var(--space-8);
  text-align: center;
  
  .empty-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto var(--space-6);
    color: var(--color-gray-300);
  }
  
  .empty-title {
    font-size: var(--text-h4);
    font-weight: var(--font-semibold);
    color: var(--color-gray-900);
    margin-bottom: var(--space-2);
  }
  
  .empty-description {
    font-size: var(--text-base);
    color: var(--color-gray-500);
    margin-bottom: var(--space-6);
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
}
```

---

## 通知系统

### Toast通知

```css
.toast-container {
  position: fixed;
  top: var(--space-6);
  right: var(--space-6);
  z-index: 100;
  max-width: 400px;
}

.toast {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-gray-200);
  padding: var(--space-4);
  margin-bottom: var(--space-3);
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  
  /* 动画进入 */
  animation: toastSlideIn 0.3s ease-out;
  
  /* 类型样式 */
  &.toast-success {
    border-left: 4px solid var(--color-success);
    
    .toast-icon {
      color: var(--color-success);
    }
  }
  
  &.toast-warning {
    border-left: 4px solid var(--color-warning);
    
    .toast-icon {
      color: var(--color-warning);
    }
  }
  
  &.toast-error {
    border-left: 4px solid var(--color-error);
    
    .toast-icon {
      color: var(--color-error);
    }
  }
  
  &.toast-info {
    border-left: 4px solid var(--color-info);
    
    .toast-icon {
      color: var(--color-info);
    }
  }
  
  .toast-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    margin-top: 2px;
  }
  
  .toast-content {
    flex: 1;
    
    .toast-title {
      font-size: var(--text-sm);
      font-weight: var(--font-medium);
      color: var(--color-gray-900);
      margin-bottom: var(--space-1);
    }
    
    .toast-message {
      font-size: var(--text-xs);
      color: var(--color-gray-600);
      line-height: 1.4;
    }
  }
  
  .toast-close {
    width: 20px;
    height: 20px;
    background: none;
    border: none;
    color: var(--color-gray-400);
    cursor: pointer;
    border-radius: var(--radius-base);
    flex-shrink: 0;
    
    &:hover {
      background: var(--color-gray-100);
      color: var(--color-gray-600);
    }
  }
}

@keyframes toastSlideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```

---

## 数据可视化

### 图表容器

```css
.chart-container {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-base);
  border: 1px solid var(--color-gray-200);
  padding: var(--space-6);
  
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    
    .chart-title {
      font-size: var(--text-h4);
      font-weight: var(--font-semibold);
      color: var(--color-gray-900);
    }
    
    .chart-actions {
      display: flex;
      gap: var(--space-2);
      
      .chart-action-btn {
        width: 32px;
        height: 32px;
        background: var(--color-gray-50);
        border: 1px solid var(--color-gray-200);
        border-radius: var(--radius-base);
        color: var(--color-gray-600);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &:hover {
          background: var(--color-gray-100);
          color: var(--color-gray-900);
        }
      }
    }
  }
  
  .chart-content {
    position: relative;
    height: 300px;
    
    /* 图表加载状态 */
    &.loading {
      display: flex;
      align-items: center;
      justify-content: center;
      
      .chart-spinner {
        width: 40px;
        height: 40px;
      }
    }
  }
  
  .chart-legend {
    margin-top: var(--space-4);
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-4);
    justify-content: center;
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      
      .legend-color {
        width: 12px;
        height: 12px;
        border-radius: var(--radius-base);
      }
      
      .legend-label {
        font-size: var(--text-sm);
        color: var(--color-gray-600);
      }
    }
  }
}
```

---

## 暗色模式支持

```css
/* 暗色模式变量 */
[data-theme="dark"] {
  /* 背景色 */
  --color-white: #1f2937;
  --color-gray-50: #1f2937;
  --color-gray-100: #374151;
  --color-gray-200: #4b5563;
  --color-gray-300: #6b7280;
  --color-gray-400: #9ca3af;
  --color-gray-500: #d1d5db;
  --color-gray-600: #e5e7eb;
  --color-gray-700: #f3f4f6;
  --color-gray-800: #f9fafb;
  --color-gray-900: #ffffff;
  
  /* 阴影调整 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
  --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.4);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4);
}

/* 主题切换按钮 */
.theme-toggle {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: var(--radius-lg);
  color: var(--color-white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  
  .theme-icon {
    width: 20px;
    height: 20px;
  }
}
```

---

## Tailwind CSS 配置

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{html,js,ts,jsx,tsx}",
    "./web/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#ff6b35', // 主品牌色
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        secondary: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ff5722', // 次要品牌色
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
        'mono': ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular'],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'skeleton': 'skeleton-loading 1.5s infinite',
        'toast-slide': 'toastSlideIn 0.3s ease-out',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'primary': '0 4px 14px 0 rgb(255 107 53 / 0.2)',
        'primary-lg': '0 10px 25px -5px rgb(255 107 53 / 0.25)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
  darkMode: ['class', '[data-theme="dark"]'],
}
```

---

## 实现指南

### 1. 开发优先级

**第一阶段 - 基础组件**
- [ ] 色彩系统和CSS变量
- [ ] 字体和间距系统
- [ ] 基础按钮组件
- [ ] 基础输入框组件
- [ ] 基础卡片组件

**第二阶段 - 布局系统**
- [ ] 侧边栏导航
- [ ] 顶部导航栏
- [ ] 主内容区域
- [ ] 响应式布局

**第三阶段 - 高级组件**
- [ ] 数据表格
- [ ] 表单系统
- [ ] 模态框
- [ ] 通知系统

**第四阶段 - 数据可视化**
- [ ] 图表容器
- [ ] 数据卡片
- [ ] 状态指示器

**第五阶段 - 交互优化**
- [ ] 加载状态
- [ ] 错误处理
- [ ] 空状态
- [ ] 暗色模式

### 2. 关键实现文件

```
web/src/
├── styles/
│   ├── globals.css          # 全局样式和CSS变量
│   ├── components.css       # 组件样式
│   └── utilities.css        # 工具类
├── components/
│   ├── ui/                  # 基础UI组件
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Modal.tsx
│   ├── layout/              # 布局组件
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   └── features/            # 功能组件
│       ├── Dashboard.tsx
│       ├── DataSources.tsx
│       └── Settings.tsx
└── lib/
    ├── theme.ts             # 主题配置
    └── utils.ts             # 工具函数
```

### 3. 快速开始模板

```html
<!-- 基础页面模板 -->
<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析平台</title>
    <link rel="stylesheet" href="/styles/globals.css">
</head>
<body>
    <!-- 主布局 -->
    <div class="app-layout">
        <!-- 侧边栏 -->
        <aside class="sidebar">
            <!-- 导航内容 -->
        </aside>
        
        <!-- 主内容区 -->
        <main class="main-content">
            <!-- 顶部导航 -->
            <header class="header">
                <!-- 头部内容 -->
            </header>
            
            <!-- 页面内容 -->
            <div class="page-content">
                <!-- 具体页面内容 -->
            </div>
        </main>
    </div>
</body>
</html>
```

### 4. 组件使用示例

```jsx
// React组件示例
import { Card, Button, Input } from '@/components/ui'

function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* 指标卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="card-metric">
          <div className="metric-value">1,234</div>
          <div className="metric-label">总用户数</div>
          <div className="metric-change positive">
            ↑ 12.5% 较上月
          </div>
        </Card>
      </div>
      
      {/* 数据表格 */}
      <Card>
        <div className="card-header">
          <h2 className="card-title">数据源</h2>
          <Button className="btn-primary btn-sm">
            添加数据源
          </Button>
        </div>
        <div className="card-body">
          {/* 表格内容 */}
        </div>
      </Card>
    </div>
  )
}
```

---

## 可访问性清单

### WCAG 2.1 AA 合规要求

- [ ] **色彩对比度**: 所有文本达到4.5:1对比度
- [ ] **键盘导航**: 所有交互元素可键盘操作
- [ ] **焦点指示**: 清晰的焦点样式
- [ ] **屏幕阅读器**: 适当的ARIA标签
- [ ] **语义化HTML**: 使用正确的HTML元素
- [ ] **表单标签**: 所有表单控件有关联标签
- [ ] **错误提示**: 清晰的错误信息和指导
- [ ] **动画控制**: 支持减少动画偏好设置

---

## 性能优化

### CSS优化

- [ ] **关键CSS内联**: 首屏样式内联加载
- [ ] **CSS压缩**: 生产环境启用CSS压缩
- [ ] **字体优化**: 使用font-display: swap
- [ ] **渐进增强**: 核心功能优先加载

### 图像优化

- [ ] **WebP支持**: 现代浏览器使用WebP格式
- [ ] **响应式图片**: 不同屏幕尺寸的图片优化
- [ ] **懒加载**: 图片和图标的懒加载实现

---

## 测试策略

### 视觉回归测试

- [ ] **Storybook**: 组件库文档和测试
- [ ] **Chromatic**: 视觉回归测试
- [ ] **截图对比**: 自动化UI测试

### 跨浏览器测试

- [ ] **Chrome**: 最新版本
- [ ] **Firefox**: 最新版本  
- [ ] **Safari**: 最新版本
- [ ] **Edge**: 最新版本
- [ ] **移动浏览器**: iOS Safari, Chrome Mobile

---

这个设计系统为您的SaaS数据分析平台提供了完整的UI规范，基于现代设计原则和快速开发需求。所有组件都经过精心设计，确保在6天开发周期内能够快速实现，同时保证专业的企业级外观和良好的用户体验。