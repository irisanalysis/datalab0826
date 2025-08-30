# Frontend Architecture Specification
## SaaS Data Analysis Platform

**Version**: 1.0  
**Date**: 2025-08-29  
**Framework**: Next.js 14 + TypeScript + Tailwind CSS

---

## 1. Project Structure Design

### 1.1 Directory Architecture

```
web/
├── app/                          # Next.js 14 App Router
│   ├── (auth)/                   # Route Groups for Auth
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx            # Auth layout wrapper
│   ├── (dashboard)/              # Protected Dashboard Routes
│   │   ├── analytics/            # Data analysis pages
│   │   ├── data-sources/         # Data source management
│   │   ├── profile/              # User profile management
│   │   ├── settings/             # Multi-tab settings panel
│   │   ├── integrations/         # Third-party integrations
│   │   ├── security/             # Device & security management
│   │   └── layout.tsx            # Dashboard layout with sidebar
│   ├── api/                      # API route handlers
│   │   ├── auth/                 # Authentication endpoints
│   │   └── proxy/                # Backend API proxy
│   ├── globals.css               # Global styles and CSS variables
│   ├── layout.tsx                # Root layout
│   ├── loading.tsx               # Global loading UI
│   ├── error.tsx                 # Global error boundary
│   └── not-found.tsx             # 404 page
├── components/                   # Reusable UI components
│   ├── ui/                       # Atomic design system components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Tooltip.tsx
│   │   ├── Badge.tsx
│   │   └── index.ts              # Barrel exports
│   ├── forms/                    # Form-specific components
│   │   ├── LoginForm.tsx
│   │   ├── ProfileForm.tsx
│   │   ├── DataSourceForm.tsx
│   │   └── SettingsForm.tsx
│   ├── layout/                   # Layout components
│   │   ├── Sidebar.tsx           # Collapsible navigation
│   │   ├── Header.tsx            # Top gradient header
│   │   ├── Breadcrumbs.tsx
│   │   └── MobileMenu.tsx
│   ├── data/                     # Data-specific components
│   │   ├── DataSourceCard.tsx
│   │   ├── ConnectionStatus.tsx
│   │   ├── DataPreview.tsx
│   │   └── IntegrationGrid.tsx
│   └── security/                 # Security-related components
│       ├── SessionList.tsx
│       ├── DeviceCard.tsx
│       └── ActivityLog.tsx
├── lib/                          # Utility libraries
│   ├── auth.ts                   # Authentication utilities
│   ├── api.ts                    # API client configuration
│   ├── utils.ts                  # General utilities
│   ├── validations/              # Form validation schemas
│   │   ├── auth.ts
│   │   ├── profile.ts
│   │   └── datasource.ts
│   └── constants.ts              # App constants
├── hooks/                        # Custom React hooks
│   ├── useAuth.ts                # Authentication hook
│   ├── useLocalStorage.ts        # Local storage management
│   ├── useDebounce.ts            # Input debouncing
│   ├── useMediaQuery.ts          # Responsive design
│   └── useApi.ts                 # API data fetching
├── store/                        # State management
│   ├── providers/                # Context providers
│   │   ├── AuthProvider.tsx
│   │   ├── ThemeProvider.tsx
│   │   └── NotificationProvider.tsx
│   ├── slices/                   # Zustand store slices
│   │   ├── authSlice.ts
│   │   ├── uiSlice.ts
│   │   └── dataSourceSlice.ts
│   └── index.ts                  # Store configuration
├── types/                        # TypeScript type definitions
│   ├── auth.ts
│   ├── user.ts
│   ├── datasource.ts
│   ├── api.ts
│   └── global.ts
├── styles/                       # Additional styling
│   ├── components.css            # Component-specific styles
│   └── animations.css            # Custom animations
├── public/                       # Static assets
│   ├── icons/                    # SVG icons
│   ├── images/                   # Images and illustrations
│   └── favicon.ico
├── __tests__/                    # Test files
│   ├── components/
│   ├── pages/
│   └── utils/
├── .env.local                    # Environment variables
├── .env.example                  # Environment template
├── next.config.js                # Next.js configuration
├── tailwind.config.js            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── jest.config.js                # Jest testing configuration
├── playwright.config.ts          # E2E testing configuration
└── package.json                  # Dependencies and scripts
```

### 1.2 Component Architecture Strategy

#### 1.2.1 Atomic Design System
```typescript
// Atomic Level Hierarchy
atoms/         // Button, Input, Label, Icon
molecules/     // FormField, SearchBox, StatusIndicator
organisms/     // NavigationSidebar, DataSourceGrid, SettingsPanel
templates/     // DashboardLayout, AuthLayout
pages/         // Complete page implementations
```

#### 1.2.2 Component Composition Pattern
```typescript
// Example: Composable Card Component
<Card>
  <Card.Header>
    <Card.Title>Data Source</Card.Title>
    <Card.Actions>
      <Button variant="ghost">Edit</Button>
    </Card.Actions>
  </Card.Header>
  <Card.Content>
    <ConnectionStatus status="connected" />
  </Card.Content>
  <Card.Footer>
    <Badge variant="success">Active</Badge>
  </Card.Footer>
</Card>
```

---

## 2. State Management Strategy

### 2.1 Global State Architecture (Zustand + Context API)

```typescript
// store/index.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { authSlice } from './slices/authSlice'
import { uiSlice } from './slices/uiSlice'
import { dataSourceSlice } from './slices/dataSourceSlice'

export const useStore = create()(
  devtools(
    persist(
      (...args) => ({
        ...authSlice(...args),
        ...uiSlice(...args),
        ...dataSourceSlice(...args),
      }),
      {
        name: 'saas-platform-storage',
        partialize: (state) => ({
          auth: state.auth,
          ui: { theme: state.ui.theme, sidebarCollapsed: state.ui.sidebarCollapsed }
        })
      }
    )
  )
)
```

### 2.2 Authentication State Management

```typescript
// store/slices/authSlice.ts
interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshAuth: () => Promise<void>
  updateProfile: (profile: UserProfile) => Promise<void>
}

export const authSlice: StateCreator<AuthState> = (set, get) => ({
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  
  login: async (credentials) => {
    set({ isLoading: true })
    try {
      const response = await apiClient.post('/auth/login', credentials)
      const { user, accessToken, refreshToken } = response.data
      
      set({
        user,
        token: accessToken,
        refreshToken,
        isAuthenticated: true,
        isLoading: false
      })
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },
  
  logout: () => {
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false
    })
  }
})
```

### 2.3 UI State Management

```typescript
// store/slices/uiSlice.ts
interface UIState {
  theme: 'light' | 'dark' | 'system'
  sidebarCollapsed: boolean
  notifications: Notification[]
  modals: ModalState
  loading: Record<string, boolean>
  toggleSidebar: () => void
  setTheme: (theme: UIState['theme']) => void
  addNotification: (notification: Notification) => void
  removeNotification: (id: string) => void
  setLoading: (key: string, loading: boolean) => void
}
```

### 2.4 Server State Management (TanStack Query)

```typescript
// hooks/useApi.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export const useDataSources = () => {
  return useQuery({
    queryKey: ['dataSources'],
    queryFn: () => apiClient.get('/data-sources'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useCreateDataSource = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (dataSource: CreateDataSourceRequest) =>
      apiClient.post('/data-sources', dataSource),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataSources'] })
    }
  })
}
```

---

## 3. UI Component System

### 3.1 Design System Foundation

#### 3.1.1 Color System (Tailwind Configuration)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Primary Orange
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        secondary: {
          50: '#fdf2f8',
          100: '#fce7f3',
          200: '#fbcfe8',
          300: '#f9a8d4',
          400: '#f472b6',
          500: '#ec4899', // Primary Pink
          600: '#db2777',
          700: '#be185d',
          800: '#9d174d',
          900: '#831843',
        },
        gradient: {
          'orange-pink': 'linear-gradient(135deg, #f97316 0%, #ec4899 100%)',
          'orange-pink-light': 'linear-gradient(135deg, #fdba74 0%, #f9a8d4 100%)',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          700: '#15803d',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          700: '#b45309',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          700: '#c53030',
        },
        neutral: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      }
    }
  }
}
```

#### 3.1.2 Typography Scale
```css
/* globals.css */
:root {
  /* Typography Scale */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  
  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Spacing Scale */
  --space-unit: 0.25rem;      /* 4px base unit */
}
```

### 3.2 Core UI Components

#### 3.2.1 Button Component System
```typescript
// components/ui/Button.tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    loading = false,
    leftIcon,
    rightIcon,
    children, 
    disabled,
    ...props 
  }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2'
    
    const variants = {
      primary: 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white hover:from-primary-600 hover:to-secondary-600 focus:ring-primary-500',
      secondary: 'bg-neutral-100 text-neutral-900 hover:bg-neutral-200 focus:ring-neutral-500',
      outline: 'border border-primary-500 text-primary-500 hover:bg-primary-50 focus:ring-primary-500',
      ghost: 'text-neutral-600 hover:bg-neutral-100 focus:ring-neutral-500',
      danger: 'bg-error-500 text-white hover:bg-error-600 focus:ring-error-500'
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-base gap-2',
      lg: 'px-6 py-3 text-lg gap-2.5'
    }
    
    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          (disabled || loading) && 'opacity-50 cursor-not-allowed',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
        ) : leftIcon}
        {children}
        {!loading && rightIcon}
      </button>
    )
  }
)

Button.displayName = 'Button'
export default Button
```

#### 3.2.2 Card Component System
```typescript
// components/ui/Card.tsx
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined'
}

const Card = ({ className, variant = 'default', ...props }: CardProps) => {
  const variants = {
    default: 'bg-white border border-neutral-200 shadow-sm',
    elevated: 'bg-white shadow-lg border border-neutral-100',
    outlined: 'bg-white border-2 border-primary-200'
  }
  
  return (
    <div
      className={cn(
        'rounded-lg overflow-hidden',
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('px-6 py-4 border-b border-neutral-100', className)} {...props} />
)

const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('px-6 py-4', className)} {...props} />
)

const CardFooter = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('px-6 py-4 border-t border-neutral-100 bg-neutral-50', className)} {...props} />
)

const CardTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
  <h3 className={cn('text-lg font-semibold text-neutral-900', className)} {...props} />
)

const CardActions = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('flex items-center space-x-2', className)} {...props} />
)

Card.Header = CardHeader
Card.Content = CardContent
Card.Footer = CardFooter
Card.Title = CardTitle
Card.Actions = CardActions

export default Card
```

### 3.3 Layout Components

#### 3.3.1 Sidebar Navigation
```typescript
// components/layout/Sidebar.tsx
'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useStore } from '@/store'
import { cn } from '@/lib/utils'
import {
  HomeIcon,
  DatabaseIcon,
  UserIcon,
  CogIcon,
  ShieldCheckIcon,
  PuzzlePieceIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline'

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  badge?: number
  status?: 'connected' | 'disconnected' | 'syncing'
  children?: NavigationItem[]
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  {
    name: 'Data Sources',
    href: '/dashboard/data-sources',
    icon: DatabaseIcon,
    badge: 3,
    status: 'connected'
  },
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Profile', href: '/dashboard/profile', icon: UserIcon },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: CogIcon,
    children: [
      { name: 'Personal', href: '/dashboard/settings/personal', icon: UserIcon },
      { name: 'Security', href: '/dashboard/settings/security', icon: ShieldCheckIcon },
      { name: 'Team', href: '/dashboard/settings/team', icon: UsersIcon },
      { name: 'Billing', href: '/dashboard/settings/billing', icon: CreditCardIcon },
      { name: 'Notifications', href: '/dashboard/settings/notifications', icon: BellIcon },
    ]
  },
  { name: 'Integrations', href: '/dashboard/integrations', icon: PuzzlePieceIcon, badge: 2 },
  { name: 'Security', href: '/dashboard/security', icon: ShieldCheckIcon }
]

export default function Sidebar() {
  const pathname = usePathname()
  const { sidebarCollapsed, toggleSidebar } = useStore()
  
  const StatusIndicator = ({ status }: { status?: string }) => {
    if (!status) return null
    
    const colors = {
      connected: 'bg-success-500',
      disconnected: 'bg-error-500',
      syncing: 'bg-warning-500 animate-pulse'
    }
    
    return (
      <div className={cn('w-2 h-2 rounded-full', colors[status as keyof typeof colors])} />
    )
  }
  
  const Badge = ({ count }: { count?: number }) => {
    if (!count) return null
    
    return (
      <span className="bg-primary-500 text-white text-xs rounded-full px-2 py-0.5 min-w-[1.25rem] text-center">
        {count > 99 ? '99+' : count}
      </span>
    )
  }
  
  return (
    <div 
      className={cn(
        'fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-neutral-200 transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        <div className={cn('flex items-center space-x-3', sidebarCollapsed && 'justify-center')}>
          <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">SA</span>
          </div>
          {!sidebarCollapsed && (
            <h1 className="text-lg font-semibold text-neutral-900">SaaS Analytics</h1>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-md hover:bg-neutral-100 transition-colors"
          aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? (
            <ChevronRightIcon className="w-5 h-5" />
          ) : (
            <ChevronLeftIcon className="w-5 h-5" />
          )}
        </button>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          
          return (
            <div key={item.name}>
              <Link
                href={item.href}
                className={cn(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                    : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900',
                  sidebarCollapsed && 'justify-center'
                )}
              >
                <item.icon 
                  className={cn('w-5 h-5 flex-shrink-0', !sidebarCollapsed && 'mr-3')} 
                />
                {!sidebarCollapsed && (
                  <>
                    <span className="flex-1">{item.name}</span>
                    <div className="flex items-center space-x-2">
                      <StatusIndicator status={item.status} />
                      <Badge count={item.badge} />
                    </div>
                  </>
                )}
              </Link>
              
              {/* Sub-navigation */}
              {!sidebarCollapsed && item.children && isActive && (
                <div className="ml-6 mt-1 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.name}
                      href={child.href}
                      className={cn(
                        'group flex items-center px-3 py-1.5 text-sm rounded-md transition-colors',
                        pathname === child.href
                          ? 'text-primary-700 bg-primary-50'
                          : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-50'
                      )}
                    >
                      <child.icon className="w-4 h-4 mr-2" />
                      {child.name}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>
      
      {/* User Section */}
      <div className="p-3 border-t border-neutral-200">
        <div className={cn('flex items-center space-x-3', sidebarCollapsed && 'justify-center')}>
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <UserIcon className="w-5 h-5 text-primary-600" />
          </div>
          {!sidebarCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 truncate">John Doe</p>
              <p className="text-xs text-neutral-500 truncate">john@example.com</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

#### 3.3.2 Header Component
```typescript
// components/layout/Header.tsx
'use client'

import { useState } from 'react'
import { useStore } from '@/store'
import { 
  MagnifyingGlassIcon, 
  BellIcon,
  UserCircleIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'
import Button from '@/components/ui/Button'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const { user, notifications } = useStore()
  const unreadCount = notifications.filter(n => !n.read).length
  
  return (
    <header className="bg-gradient-to-r from-primary-500 to-secondary-500 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Search */}
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-white/70" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-white/30 rounded-md leading-5 bg-white/20 text-white placeholder-white/70 focus:outline-none focus:bg-white/30 focus:border-white/50 focus:ring-white/50 sm:text-sm"
                placeholder="Search data sources, analytics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <button className="relative p-2 text-white/80 hover:text-white transition-colors">
              <BellIcon className="h-6 w-6" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-error-500 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
            
            {/* Settings */}
            <button className="p-2 text-white/80 hover:text-white transition-colors">
              <Cog6ToothIcon className="h-6 w-6" />
            </button>
            
            {/* Profile Dropdown */}
            <div className="relative">
              <button className="flex items-center space-x-3 text-white/90 hover:text-white transition-colors">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <UserCircleIcon className="w-6 h-6" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium">{user?.name || 'User'}</p>
                  <p className="text-xs text-white/70">{user?.email}</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
```

---

## 4. Performance Optimization Strategy

### 4.1 Code Splitting & Lazy Loading

```typescript
// app/dashboard/layout.tsx
import dynamic from 'next/dynamic'
import { Suspense } from 'react'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

// Lazy load heavy components
const Sidebar = dynamic(() => import('@/components/layout/Sidebar'), {
  loading: () => <div className="w-64 h-full bg-neutral-100 animate-pulse" />
})

const DataVisualization = dynamic(() => import('@/components/charts/DataVisualization'), {
  loading: () => <LoadingSpinner />
})

// Route-based code splitting
const AnalyticsPage = dynamic(() => import('./analytics/page'), {
  loading: () => <LoadingSpinner />,
  ssr: false // Client-side only for heavy data components
})

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-neutral-50">
      <Suspense fallback={<div className="w-64 bg-white border-r" />}>
        <Sidebar />
      </Suspense>
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          <Suspense fallback={<LoadingSpinner />}>
            {children}
          </Suspense>
        </main>
      </div>
    </div>
  )
}
```

### 4.2 Image & Asset Optimization

```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    domains: ['example.com', 'cdn.example.com'],
  },
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@heroicons/react', 'lucide-react'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
}

module.exports = nextConfig
```

### 4.3 Caching Strategy

```typescript
// lib/api.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
})

// Request interceptor for auth tokens
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Add cache headers for GET requests
  if (config.method === 'get') {
    config.headers['Cache-Control'] = 'max-age=300' // 5 minutes
  }
  
  return config
})

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const response = await axios.post('/auth/refresh', { refreshToken })
          const { accessToken } = response.data
          localStorage.setItem('accessToken', accessToken)
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${accessToken}`
          return apiClient(error.config)
        } catch (refreshError) {
          // Refresh failed, redirect to login
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)
```

### 4.4 Bundle Analysis & Optimization

```json
// package.json scripts
{
  "scripts": {
    "analyze": "cross-env ANALYZE=true next build",
    "build:analyze": "npm run build && npx @next/bundle-analyzer",
    "lighthouse": "lhci autorun",
    "perf:audit": "next build && next start & sleep 5 && lighthouse http://localhost:3000 --chrome-flags='--headless' --output html --output-path ./lighthouse-report.html"
  }
}
```

---

## 5. Development Tools Configuration

### 5.1 Enhanced TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "ES6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"],
      "@/hooks/*": ["./hooks/*"],
      "@/store/*": ["./store/*"],
      "@/types/*": ["./types/*"],
      "@/utils/*": ["./lib/utils/*"]
    },
    // Enhanced type checking
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

### 5.2 ESLint & Prettier Configuration

```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": [
    "@typescript-eslint",
    "react-hooks",
    "jsx-a11y",
    "import"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-role": "error",
    "import/order": [
      "error",
      {
        "groups": ["builtin", "external", "internal", "parent", "sibling", "index"],
        "newlines-between": "always",
        "alphabetize": {
          "order": "asc",
          "caseInsensitive": true
        }
      }
    ],
    "prefer-const": "error",
    "no-console": "warn"
  },
  "settings": {
    "react": {
      "version": "detect"
    },
    "import/resolver": {
      "typescript": {}
    }
  }
}
```

```json
// .prettierrc
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "jsxBracketSameLine": false,
  "arrowParens": "avoid",
  "endOfLine": "lf"
}
```

### 5.3 Testing Framework Setup

```javascript
// jest.config.js
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  collectCoverageFrom: [
    'components/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    'hooks/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

```javascript
// jest.setup.js
import '@testing-library/jest-dom'
import { TextEncoder, TextDecoder } from 'util'

global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})
```

### 5.4 Playwright E2E Testing

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

---

## 6. Accessibility & Responsive Design

### 6.1 WCAG 2.1 AA Compliance

```typescript
// components/ui/AccessibleButton.tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  'aria-label'?: string
  'aria-describedby'?: string
}

const AccessibleButton = forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  ({ 
    className,
    children,
    disabled,
    loading,
    'aria-label': ariaLabel,
    'aria-describedby': ariaDescribedBy,
    ...props 
  }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          // Base styles with focus indicators
          'relative inline-flex items-center justify-center font-medium rounded-md transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
          // High contrast mode support
          'contrast-more:border-2 contrast-more:border-current',
          // Loading state
          loading && 'cursor-not-allowed',
          className
        )}
        disabled={disabled || loading}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <span className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
            <span className="sr-only">Loading...</span>
          </span>
        )}
        <span className={cn('flex items-center gap-2', loading && 'opacity-0')}>
          {children}
        </span>
      </button>
    )
  }
)

AccessibleButton.displayName = 'AccessibleButton'
export default AccessibleButton
```

### 6.2 Responsive Breakpoint System

```css
/* globals.css - Custom breakpoint system */
:root {
  /* Breakpoints */
  --bp-xs: 375px;   /* Mobile small */
  --bp-sm: 640px;   /* Mobile large */
  --bp-md: 768px;   /* Tablet */
  --bp-lg: 1024px;  /* Desktop small */
  --bp-xl: 1280px;  /* Desktop */
  --bp-2xl: 1536px; /* Desktop large */
  
  /* Container sizes */
  --container-xs: 100%;
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1536px;
}

/* Responsive utilities */
.container-responsive {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .container-responsive {
    max-width: 640px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

@media (min-width: 768px) {
  .container-responsive {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  .container-responsive {
    max-width: 1024px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

@media (min-width: 1280px) {
  .container-responsive {
    max-width: 1280px;
  }
}

@media (min-width: 1536px) {
  .container-responsive {
    max-width: 1536px;
  }
}
```

### 6.3 Mobile-First Responsive Hook

```typescript
// hooks/useMediaQuery.ts
import { useState, useEffect } from 'react'

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    if (media.matches !== matches) {
      setMatches(media.matches)
    }
    
    const listener = () => setMatches(media.matches)
    media.addEventListener('change', listener)
    
    return () => media.removeEventListener('change', listener)
  }, [matches, query])

  return matches
}

// Predefined breakpoint hooks
export const useBreakpoint = () => {
  const isMobile = useMediaQuery('(max-width: 767px)')
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)')
  const isDesktop = useMediaQuery('(min-width: 1024px)')
  const isLarge = useMediaQuery('(min-width: 1280px)')
  
  return {
    isMobile,
    isTablet,
    isDesktop,
    isLarge,
    device: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop'
  }
}
```

---

## 7. Security Implementation

### 7.1 JWT Token Management

```typescript
// lib/auth.ts
import { jwtDecode } from 'jwt-decode'

interface TokenPayload {
  sub: string
  exp: number
  iat: number
  role: string
}

export class AuthTokenManager {
  private static instance: AuthTokenManager
  private refreshTimer: NodeJS.Timeout | null = null

  static getInstance(): AuthTokenManager {
    if (!AuthTokenManager.instance) {
      AuthTokenManager.instance = new AuthTokenManager()
    }
    return AuthTokenManager.instance
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem('accessToken', accessToken)
    localStorage.setItem('refreshToken', refreshToken)
    this.scheduleRefresh(accessToken)
  }

  getAccessToken(): string | null {
    return localStorage.getItem('accessToken')
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refreshToken')
  }

  clearTokens(): void {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer)
      this.refreshTimer = null
    }
  }

  isTokenExpired(token: string): boolean {
    try {
      const decoded = jwtDecode<TokenPayload>(token)
      return decoded.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  private scheduleRefresh(token: string): void {
    try {
      const decoded = jwtDecode<TokenPayload>(token)
      const now = Date.now()
      const expiry = decoded.exp * 1000
      
      // Refresh 5 minutes before expiry
      const refreshTime = expiry - now - 5 * 60 * 1000
      
      if (refreshTime > 0) {
        this.refreshTimer = setTimeout(async () => {
          await this.refreshTokens()
        }, refreshTime)
      }
    } catch (error) {
      console.error('Error scheduling token refresh:', error)
    }
  }

  private async refreshTokens(): Promise<void> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) return

    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken })
      })

      if (response.ok) {
        const { accessToken, refreshToken: newRefreshToken } = await response.json()
        this.setTokens(accessToken, newRefreshToken)
      } else {
        this.clearTokens()
        window.location.href = '/login'
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.clearTokens()
      window.location.href = '/login'
    }
  }
}
```

### 7.2 XSS & CSRF Protection

```typescript
// lib/security.ts
import DOMPurify from 'dompurify'

// XSS Protection
export const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li'],
    ALLOWED_ATTR: []
  })
}

export const sanitizeInput = (input: string): string => {
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+="[^"]*"/gi, '')
}

// CSRF Token Management
export const getCsrfToken = (): string => {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  return token || ''
}

// Content Security Policy Headers (Next.js middleware)
export const securityHeaders = {
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' https://api.example.com",
    "frame-ancestors 'none'",
  ].join('; '),
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
}
```

---

## 8. Performance Metrics & Monitoring

### 8.1 Web Vitals Monitoring

```typescript
// lib/analytics.ts
import { getCLS, getFCP, getFID, getLCP, getTTFB } from 'web-vitals'

interface MetricData {
  name: string
  value: number
  id: string
  delta: number
}

export function initializeWebVitals() {
  function sendToAnalytics(metric: MetricData) {
    // Send to your analytics service
    if (process.env.NODE_ENV === 'production') {
      fetch('/api/analytics/web-vitals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metric),
        keepalive: true
      }).catch(console.error)
    }
    
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`${metric.name}: ${metric.value}`)
    }
  }

  getCLS(sendToAnalytics)
  getFCP(sendToAnalytics)
  getFID(sendToAnalytics)
  getLCP(sendToAnalytics)
  getTTFB(sendToAnalytics)
}

// Performance thresholds
export const performanceThresholds = {
  LCP: 2500, // Good: ≤ 2.5s
  FID: 100,  // Good: ≤ 100ms
  CLS: 0.1,  // Good: ≤ 0.1
  FCP: 1800, // Good: ≤ 1.8s
  TTFB: 800, // Good: ≤ 0.8s
}
```

### 8.2 Error Boundary & Logging

```typescript
// components/ErrorBoundary.tsx
'use client'

import { Component, ErrorInfo, ReactNode } from 'react'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to monitoring service
    this.logError(error, errorInfo)
    
    // Call custom error handler
    this.props.onError?.(error, errorInfo)
  }

  private logError = (error: Error, errorInfo: ErrorInfo) => {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    }

    if (process.env.NODE_ENV === 'production') {
      fetch('/api/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorData),
      }).catch(console.error)
    } else {
      console.error('Error Boundary caught an error:', error, errorInfo)
    }
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 px-4">
          <Card className="max-w-md w-full">
            <Card.Content className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-error-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-error-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-neutral-900 mb-2">
                Something went wrong
              </h2>
              <p className="text-neutral-600 mb-6">
                We're sorry, but something unexpected happened. Please try again.
              </p>
              {process.env.NODE_ENV === 'development' && (
                <details className="text-left mb-4 p-3 bg-neutral-100 rounded text-sm">
                  <summary className="cursor-pointer font-medium">Error details</summary>
                  <pre className="mt-2 text-xs overflow-auto">
                    {this.state.error?.stack}
                  </pre>
                </details>
              )}
              <div className="flex gap-3 justify-center">
                <Button onClick={this.handleRetry}>
                  Try Again
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => window.location.href = '/dashboard'}
                >
                  Go to Dashboard
                </Button>
              </div>
            </Card.Content>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
```

---

## 9. Implementation Roadmap

### 9.1 Phase 1: Foundation (Weeks 1-2)
- **Week 1**: Project setup, authentication system, basic layout
- **Week 2**: Core UI components, navigation system, responsive framework

### 9.2 Phase 2: Core Features (Weeks 3-8)
- **Week 3-4**: User profile management, settings panel
- **Week 5-6**: Data source connection module
- **Week 7-8**: Security features, device management

### 9.3 Phase 3: Enhancement (Weeks 9-12)
- **Week 9-10**: Third-party integrations, advanced features
- **Week 11-12**: Performance optimization, testing, deployment

### 9.4 Quality Gates
- **Code Quality**: 90% TypeScript coverage, ESLint/Prettier compliance
- **Performance**: Lighthouse score ≥ 90, Core Web Vitals green
- **Accessibility**: WCAG 2.1 AA compliance, screen reader testing
- **Testing**: 80% test coverage, E2E test suite completion

---

## 10. Deployment & DevOps

### 10.1 Build & Deployment Configuration

```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths: ['web/**']
  pull_request:
    branches: [main]
    paths: ['web/**']

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: web/package-lock.json
    
    - name: Install dependencies
      run: npm ci
      working-directory: web
    
    - name: Type check
      run: npm run type-check
      working-directory: web
    
    - name: Lint
      run: npm run lint
      working-directory: web
    
    - name: Run tests
      run: npm run test:ci
      working-directory: web
    
    - name: Build application
      run: npm run build
      working-directory: web
      env:
        NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
    
    - name: Run Lighthouse CI
      run: npm run lighthouse:ci
      working-directory: web

  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: echo "Deploy to production server"
      # Add your deployment steps here
```

---

This comprehensive frontend architecture specification provides a solid foundation for building a modern, scalable, and maintainable SaaS data analysis platform. The architecture emphasizes performance, accessibility, security, and developer experience while meeting all the requirements outlined in the PRD.

The implementation follows industry best practices and provides clear guidelines for the development team to build a high-quality frontend application that will scale with the business needs.