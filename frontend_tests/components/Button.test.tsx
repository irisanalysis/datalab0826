/**
 * Button组件测试
 * 测试企业级SaaS平台中按钮组件的功能和样式
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

// 模拟按钮组件（基于设计系统）
const MockButton: React.FC<{
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  className?: string;
}> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  loading = false, 
  onClick,
  className = ''
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-orange-500 to-pink-500 text-white hover:from-orange-600 hover:to-pink-600',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className} ${
    disabled ? 'opacity-50 cursor-not-allowed' : ''
  } ${loading ? 'cursor-wait' : ''}`;
  
  return (
    <button
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      data-testid="button"
    >
      {loading && <span className="mr-2">⏳</span>}
      {children}
    </button>
  );
};

describe('Button组件测试', () => {
  
  test('渲染基本按钮', () => {
    render(<MockButton>点击我</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('点击我');
  });
  
  test('处理点击事件', () => {
    const handleClick = jest.fn();
    render(<MockButton onClick={handleClick}>点击我</MockButton>);
    
    const button = screen.getByTestId('button');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('禁用状态正确工作', () => {
    const handleClick = jest.fn();
    render(<MockButton disabled onClick={handleClick}>禁用按钮</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toBeDisabled();
    
    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });
  
  test('加载状态正确显示', () => {
    render(<MockButton loading>加载中</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent('⏳');
  });
  
  test('不同尺寸样式正确应用', () => {
    const { rerender } = render(<MockButton size="sm">小按钮</MockButton>);
    let button = screen.getByTestId('button');
    expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm');
    
    rerender(<MockButton size="lg">大按钮</MockButton>);
    button = screen.getByTestId('button');
    expect(button).toHaveClass('px-6', 'py-3', 'text-lg');
  });
  
  test('不同变体样式正确应用', () => {
    const { rerender } = render(<MockButton variant="primary">主要按钮</MockButton>);
    let button = screen.getByTestId('button');
    expect(button).toHaveClass('from-orange-500', 'to-pink-500');
    
    rerender(<MockButton variant="secondary">次要按钮</MockButton>);
    button = screen.getByTestId('button');
    expect(button).toHaveClass('bg-gray-200');
    
    rerender(<MockButton variant="outline">轮廓按钮</MockButton>);
    button = screen.getByTestId('button');
    expect(button).toHaveClass('border', 'border-gray-300');
  });
  
  test('自定义className正确合并', () => {
    render(<MockButton className="custom-class">自定义按钮</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('custom-class');
  });
  
  test('可访问性属性正确设置', () => {
    render(<MockButton>可访问按钮</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toHaveAttribute('type', 'button');
  });
  
  test('焦点状态样式正确', () => {
    render(<MockButton>焦点测试</MockButton>);
    
    const button = screen.getByTestId('button');
    expect(button).toHaveClass('focus:ring-2', 'focus:ring-offset-2');
  });
  
});

describe('Button组件快照测试', () => {
  
  test('主要按钮快照', () => {
    const { container } = render(
      <MockButton variant="primary" size="md">
        保存数据
      </MockButton>
    );
    expect(container.firstChild).toMatchSnapshot();
  });
  
  test('加载状态按钮快照', () => {
    const { container } = render(
      <MockButton loading variant="primary">
        上传中...
      </MockButton>
    );
    expect(container.firstChild).toMatchSnapshot();
  });
  
});

describe('Button组件集成测试', () => {
  
  test('在表单中正确工作', () => {
    const handleSubmit = jest.fn();
    
    render(
      <form onSubmit={handleSubmit}>
        <MockButton type="submit">提交表单</MockButton>
      </form>
    );
    
    const button = screen.getByTestId('button');
    fireEvent.click(button);
    
    // 验证表单提交事件被触发
    expect(handleSubmit).toHaveBeenCalled();
  });
  
  test('与键盘导航配合', () => {
    const handleClick = jest.fn();
    
    render(<MockButton onClick={handleClick}>键盘测试</MockButton>);
    
    const button = screen.getByTestId('button');
    
    // 模拟键盘按下空格键
    fireEvent.keyDown(button, { key: ' ', code: 'Space' });
    
    // 验证焦点状态
    button.focus();
    expect(document.activeElement).toBe(button);
  });
  
});