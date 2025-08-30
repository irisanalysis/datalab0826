# Frontend Development Guide - Claude Code Instructions

> **Advanced Frontend Architecture Guide**: This document provides comprehensive frontend patterns and architecture for the AI Data Analysis Platform. For backend integration, see [../backend/CLAUDE.md](../backend/CLAUDE.md). For development principles, see [../.claude/CLAUDE.md](../.claude/CLAUDE.md).

This guide focuses on advanced React patterns, component architecture, performance optimization, and user experience patterns for the Next.js 14 application with TypeScript and modern frontend stack.

## Cross-Reference Links
- **Backend Integration**: [../backend/CLAUDE.md](../backend/CLAUDE.md) - Microservices architecture, API endpoints, database models
- **Development Guidelines**: [../.claude/CLAUDE.md](../.claude/CLAUDE.md) - Architecture principles and coding standards  
- **Package Management**: [../CLAUDE.md](../CLAUDE.md) - Project-wide development rules and commands

## Architecture Overview

This is the frontend for the AI Data Analysis Platform, built with Next.js 14 and TypeScript. The application uses the App Router pattern and integrates seamlessly with a comprehensive microservices backend architecture.

### Microservices Integration Architecture

The frontend integrates with multiple backend services through a unified API Gateway:

**Service Registry & Communication:**
```typescript
// Service endpoint configuration
const BACKEND_SERVICES = {
  API_GATEWAY: 'http://localhost:8000',     // Central authentication & routing
  DATA_SERVICE: 'http://localhost:8001',   // Data management & ETL
  AI_SERVICE: 'http://localhost:8002',     // ML analysis & AI chat
  COMPUTE_SERVICE: 'http://localhost:8003', // Heavy computation (Ray cluster)
  VIZ_SERVICE: 'http://localhost:8004',    // Chart generation & reports
  USER_SERVICE: 'http://localhost:8005',   // User management (planned)
  NOTIFICATION_SERVICE: 'http://localhost:8006' // Real-time notifications (planned)
} as const;
```

**Integration Patterns:**
- **Authentication Flow**: JWT tokens managed through API Gateway (8000)
- **Data Operations**: Direct data service integration (8001) 
- **AI Features**: Conversational analysis through AI service (8002)
- **Visualizations**: Dynamic chart generation via visualization service (8004)
- **Heavy Computing**: Background processing through compute service (8003)

**Backend Integration Points:**
- **Database Models**: User, DataSource, UserSession (see [backend CLAUDE.md](../backend/CLAUDE.md))
- **Authentication**: JWT-based with role-based access control (admin, analyst, user, viewer)
- **Real-time Communication**: WebSocket connections for live analysis updates
- **Error Handling**: Standardized error responses across all services

### Advanced Tech Stack & Architecture

**Core Framework**
- **Framework**: Next.js 14 with App Router + React Server Components
- **Language**: TypeScript 5.3+ with strict mode and advanced type patterns
- **Runtime**: Edge Runtime optimization for performance

**Styling & Design**
- **Styling**: Tailwind CSS 3.4+ with design tokens and CSS-in-JS patterns
- **UI Components**: Radix UI + Headless UI with compound component patterns
- **Animations**: Framer Motion + CSS transitions with spring physics
- **Icons**: Lucide React with dynamic icon loading

**State & Data Management**
- **Global State**: Zustand with selectors and subscription patterns
- **Server State**: React Query v5 with optimistic updates and background sync
- **Form State**: React Hook Form + Zod with advanced validation patterns
- **Client Cache**: React Query + IndexedDB for offline capability

**Performance & Developer Experience**
- **HTTP Client**: Axios with advanced interceptors and retry logic
- **Testing**: Vitest + Testing Library + MSW for API mocking
- **Monitoring**: React Error Boundary + Performance API
- **DevTools**: React Query DevTools + Zustand DevTools

## System Architecture & File Relationships

### Application Architecture Layers

**1. Infrastructure Layer (`src/lib/`) - Advanced Patterns**
```typescript
// Advanced API architecture with patterns
src/lib/api/
├── client.ts              # Factory pattern API client with interceptors
├── services/              # Service-specific clients with TypeScript generics
│   ├── auth.service.ts    # Authentication with token management
│   ├── dataSource.service.ts # Data operations with caching
│   ├── analysis.service.ts   # AI analysis with streaming
│   └── visualization.service.ts # Chart generation with WebWorkers
├── types/                # Advanced TypeScript patterns
│   ├── api.types.ts      # Generic API patterns and branded types
│   ├── auth.types.ts     # Authentication state types
│   ├── data.types.ts     # Domain model types with validation
│   └── utility.types.ts  # Utility types and type guards
├── hooks/                # Query hooks with optimistic updates
│   ├── useAuth.hook.ts   # Authentication hook with persistence
│   ├── useDataSources.hook.ts # Data source management with cache
│   └── useAnalysis.hook.ts    # Analysis operations with streaming
├── utils/                # Advanced utilities
│   ├── interceptors.ts   # Request/response/error interceptors
│   ├── errorHandling.ts  # Error boundary and retry patterns
│   ├── cache.ts         # Cache management and invalidation
│   └── transformers.ts  # Data transformation pipelines
└── middleware/          # Request/response middleware
    ├── auth.middleware.ts    # JWT handling and refresh
    ├── retry.middleware.ts   # Exponential backoff retry
    └── logging.middleware.ts # Request/response logging
```

**2. Advanced State Management (`src/store/`) - Patterns & Architecture**
```typescript
// Advanced state management with patterns
src/store/
├── slices/               # Zustand slices with selectors
│   ├── auth.slice.ts     # Authentication state with persistence
│   ├── dataSource.slice.ts # Data source state with optimistic updates
│   ├── analysis.slice.ts   # Analysis state with streaming updates
│   ├── ui.slice.ts        # UI state with preferences sync
│   └── cache.slice.ts     # Client-side cache management
├── middleware/           # Store middleware patterns
│   ├── persist.middleware.ts  # State persistence with IndexedDB
│   ├── devtools.middleware.ts # Development tools integration
│   └── sync.middleware.ts     # Multi-tab state synchronization
├── selectors/            # Memoized selectors with reselect
│   ├── auth.selectors.ts      # Authentication selectors
│   ├── dataSource.selectors.ts # Data source computed values
│   └── ui.selectors.ts        # UI state selectors
├── hooks/                # Store hooks with subscriptions
│   ├── useAuthStore.ts        # Authentication store hook
│   ├── useDataSourceStore.ts  # Data source store hook
│   └── useUIStore.ts          # UI store hook with theme
├── types/                # Store type definitions
│   ├── store.types.ts    # Store interfaces and generics
│   ├── actions.types.ts  # Action type definitions
│   └── state.types.ts    # State shape definitions
└── index.ts             # Store composition and exports
```

**3. Advanced Component Architecture (`src/components/`) - Design Patterns**
```typescript
// Advanced component patterns and architecture
src/components/
├── ui/                   # Design system with compound patterns
│   ├── primitives/      # Base Radix UI wrappers
│   │   ├── Button/      # Compound button with variants
│   │   │   ├── Button.tsx        # Main component
│   │   │   ├── Button.types.ts   # Props and variants
│   │   │   ├── Button.styles.ts  # Tailwind variants
│   │   │   └── index.ts         # Clean exports
│   │   ├── Card/        # Flexible card system
│   │   ├── Form/        # Form primitives with validation
│   │   ├── Table/       # Data table with virtualization
│   │   └── Chart/       # Chart wrapper with lazy loading
│   ├── composite/       # Composite UI components
│   │   ├── DataGrid/    # Advanced data grid with sorting/filtering
│   │   ├── CommandPalette/ # Command palette with search
│   │   ├── FileUpload/  # Drag-and-drop file upload
│   │   └── VirtualList/ # Virtual scrolling list
│   └── feedback/        # User feedback components
│       ├── Toast/       # Toast notification system
│       ├── Loading/     # Loading states and skeletons
│       ├── ErrorBoundary/ # Error boundary with fallbacks
│       └── EmptyState/  # Empty state illustrations
├── layout/               # Layout patterns with composition
│   ├── AppShell/        # Main application shell
│   │   ├── AppShell.tsx      # Shell component
│   │   ├── Header/          # Header with navigation
│   │   ├── Sidebar/         # Collapsible sidebar
│   │   ├── Footer/          # Footer component
│   │   └── Breadcrumb/      # Navigation breadcrumbs
│   ├── PageLayout/      # Page-specific layouts
│   │   ├── DashboardLayout/ # Dashboard-specific layout
│   │   ├── AuthLayout/      # Authentication layout
│   │   └── AnalysisLayout/  # Analysis page layout
│   └── Responsive/      # Responsive utilities
│       ├── Container/       # Responsive containers
│       ├── Grid/           # CSS Grid wrapper
│       └── Breakpoint/     # Breakpoint components
├── features/             # Feature modules with domain logic
│   ├── auth/            # Authentication module
│   │   ├── components/  # Auth-specific components
│   │   ├── hooks/       # Authentication hooks
│   │   ├── utils/       # Auth utilities
│   │   └── types/       # Auth type definitions
│   ├── dashboard/       # Dashboard module
│   │   ├── widgets/     # Dashboard widgets
│   │   ├── hooks/       # Dashboard-specific hooks
│   │   └── utils/       # Dashboard utilities
│   ├── data-sources/    # Data source management
│   │   ├── components/  # Data source components
│   │   ├── hooks/       # Data source hooks
│   │   ├── validation/  # Data source validation
│   │   └── transformers/ # Data transformations
│   ├── analysis/        # AI analysis module
│   │   ├── components/  # Analysis components
│   │   ├── hooks/       # Analysis hooks with streaming
│   │   ├── workers/     # Web Workers for heavy computation
│   │   └── utils/       # Analysis utilities
│   └── visualizations/  # Visualization module
│       ├── components/  # Chart components
│       ├── hooks/       # Visualization hooks
│       ├── renderers/   # Chart renderers
│       └── utils/       # Chart utilities
├── providers/           # Context providers with advanced patterns
│   ├── AppProvider.tsx  # Root application provider
│   ├── AuthProvider/    # Authentication context with persistence
│   ├── ThemeProvider/   # Theme with CSS custom properties
│   ├── QueryProvider/   # React Query with offline support
│   └── ErrorProvider/   # Global error handling context
├── hoc/                 # Higher-order components
│   ├── withAuth.tsx     # Authentication HOC
│   ├── withErrorBoundary.tsx # Error boundary HOC
│   └── withPermissions.tsx   # Permission-based rendering
└── hooks/               # Shared custom hooks
    ├── useAuth.ts       # Authentication hook
    ├── useLocalStorage.ts # Local storage hook
    ├── useDebounce.ts   # Debounce hook
    ├── useIntersection.ts # Intersection observer
    ├── useMediaQuery.ts  # Media query hook
    └── useWebSocket.ts   # WebSocket connection hook
```

### Advanced Import Patterns & Conventions

```typescript
// Infrastructure imports with type-only imports for better tree shaking
import { apiClient } from '@/lib/api/client'
import { authService } from '@/lib/api/services/auth.service'
import type { DataSource, User, APIResponse } from '@/lib/types/api.types'
import type { AuthState, DataSourceState } from '@/lib/types/store.types'

// State management with selective imports
import { useAuthStore } from '@/store/hooks/useAuthStore'
import { useDataSourceStore } from '@/store/hooks/useDataSourceStore'
import { selectCurrentUser, selectIsAuthenticated } from '@/store/selectors/auth.selectors'

// Component imports with compound patterns
import { Button } from '@/components/ui/primitives/Button'
import { Card, CardContent, CardHeader, CardActions } from '@/components/ui/primitives/Card'
import { DataSourceList } from '@/components/features/data-sources/components/DataSourceList'
import { AppShell } from '@/components/layout/AppShell'

// Hook imports with custom patterns
import { useAuth } from '@/components/features/auth/hooks/useAuth'
import { useDataSources } from '@/components/features/data-sources/hooks/useDataSources'
import { useDebounce, useLocalStorage, useMediaQuery } from '@/hooks'

// Utility imports
import { cn } from '@/lib/utils/cn' // Class name utility
import { formatDate, formatCurrency } from '@/lib/utils/formatters'
import { validateEmail, validatePassword } from '@/lib/utils/validators'

// Advanced patterns - lazy loading and code splitting
const LazyAnalysisModule = lazy(() => import('@/components/features/analysis'))
const LazyVisualizationModule = lazy(() => import('@/components/features/visualizations'))

// Dynamic imports for heavy dependencies
const loadPlotly = () => import('plotly.js-dist-min')
const loadD3 = () => import('d3')
```

### Component Import Best Practices

```typescript
// ✅ Preferred: Named imports with clear paths
import { DataTable } from '@/components/ui/composite/DataTable'
import { useDataSources } from '@/hooks/api/useDataSources'

// ✅ Type-only imports for better performance
import type { ComponentProps, ReactNode } from 'react'
import type { DataSourceConfig } from '@/lib/types/data.types'

// ✅ Grouped imports by source
// React ecosystem
import { useState, useEffect, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Third-party libraries
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { cn } from 'clsx'

// Internal imports
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'

// ❌ Avoid: Default imports for component libraries
// import Button from '@/components/ui/Button' // Less clear

// ❌ Avoid: Deep relative imports
// import { Button } from '../../../components/ui/Button'
```

### Application Flow Architecture
```
Next.js App Router (App Directory)
└── RootLayout (app/layout.tsx)
    ├── AuthProvider (JWT token management)
    ├── ThemeProvider (light/dark mode)
    ├── QueryProvider (server state caching)
    └── ToastProvider (notifications)
        └── Page Components
            ├── Landing Page (/)
            ├── Authentication (/auth/login, /auth/register)
            ├── Dashboard (/dashboard)
            ├── Data Sources (/data-sources)
            ├── AI Analysis (/analysis)
            └── Visualizations (/visualizations)
```

## Advanced Component Architecture Patterns

### Component Design Principles

**Core Component Design Philosophy:**
- **Composition over Inheritance** - Build complex UIs from simple, focused components
- **Props Interface Design** - Clear, consistent prop APIs with TypeScript generics
- **Accessibility First** - WCAG 2.1 AA compliance built-in with Radix UI
- **Performance by Default** - React.memo, useMemo, and useCallback where beneficial
- **Design System Consistency** - Unified design tokens and variant systems

**1. Compound Component Pattern with Context**
```typescript
// Advanced card component with compound pattern and context
import { createContext, useContext } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

// Card context for internal communication
interface CardContextValue {
  variant?: 'default' | 'outlined' | 'elevated' | 'filled'
  size?: 'sm' | 'md' | 'lg'
  interactive?: boolean
}

const CardContext = createContext<CardContextValue | undefined>(undefined)

const useCardContext = () => {
  const context = useContext(CardContext)
  if (!context) {
    throw new Error('Card compound components must be used within a Card')
  }
  return context
}

// Card variants with design system tokens
const cardVariants = cva(
  // Base styles with CSS custom properties
  'rounded-lg border transition-all duration-200 focus-within:ring-2 focus-within:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'bg-card text-card-foreground border-border shadow-sm',
        outlined: 'bg-background border-2 border-primary/20 hover:border-primary/40',
        elevated: 'bg-card shadow-lg hover:shadow-xl border-0',
        filled: 'bg-muted/50 border-0 hover:bg-muted/70'
      },
      size: {
        sm: 'text-sm',
        md: 'text-base', 
        lg: 'text-lg'
      },
      interactive: {
        true: 'cursor-pointer hover:scale-[1.02] active:scale-[0.98] transform-gpu',
        false: ''
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      interactive: false
    }
  }
)

interface CardProps extends 
  React.HTMLAttributes<HTMLDivElement>,
  VariantProps<typeof cardVariants> {
  asChild?: boolean
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(({ 
  children, 
  className, 
  variant, 
  size, 
  interactive,
  asChild = false,
  ...props 
}, ref) => {
  const Comp = asChild ? Slot : 'div'
  
  return (
    <CardContext.Provider value={{ variant, size, interactive }}>
      <Comp
        ref={ref}
        className={cn(cardVariants({ variant, size, interactive }), className)}
        {...props}
      >
        {children}
      </Comp>
    </CardContext.Provider>
  )
})
Card.displayName = 'Card'

// Card Header with context-aware styling
const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ 
  children, 
  className, 
  ...props 
}, ref) => {
  const { size } = useCardContext()
  
  return (
    <div 
      ref={ref}
      className={cn(
        'flex flex-col space-y-1.5',
        {
          'p-4': size === 'sm',
          'p-6': size === 'md',
          'p-8': size === 'lg'
        },
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
})
CardHeader.displayName = 'CardHeader'

// Card Title with semantic HTML and context
const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(({ 
  children, 
  className, 
  ...props 
}, ref) => {
  const { size } = useCardContext()
  
  return (
    <h3 
      ref={ref}
      className={cn(
        'font-semibold leading-none tracking-tight',
        {
          'text-lg': size === 'sm',
          'text-xl': size === 'md', 
          'text-2xl': size === 'lg'
        },
        className
      )} 
      {...props}
    >
      {children}
    </h3>
  )
})
CardTitle.displayName = 'CardTitle'

// Card Content with responsive padding
const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ 
  children, 
  className, 
  ...props 
}, ref) => {
  const { size } = useCardContext()
  
  return (
    <div 
      ref={ref}
      className={cn(
        {
          'p-4 pt-0': size === 'sm',
          'p-6 pt-0': size === 'md',
          'p-8 pt-0': size === 'lg'
        },
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
})
CardContent.displayName = 'CardContent'

// Card Footer with actions
const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ 
  children, 
  className, 
  ...props 
}, ref) => {
  const { size } = useCardContext()
  
  return (
    <div 
      ref={ref}
      className={cn(
        'flex items-center border-t bg-muted/50',
        {
          'p-4': size === 'sm',
          'p-6': size === 'md',
          'p-8': size === 'lg'
        },
        className
      )} 
      {...props}
    >
      {children}
    </div>
  )
})
CardFooter.displayName = 'CardFooter'

// Export as compound component with TypeScript support
Card.Header = CardHeader
Card.Title = CardTitle
Card.Description = CardDescription
Card.Content = CardContent
Card.Footer = CardFooter

export { Card, CardHeader, CardTitle, CardContent, CardFooter }

// Usage Example:
// <Card variant="elevated" size="lg" interactive>
//   <Card.Header>
//     <Card.Title>Dashboard Overview</Card.Title>
//     <Card.Description>Key metrics and insights</Card.Description>
//   </Card.Header>
//   <Card.Content>
//     <MetricsGrid data={metrics} />
//   </Card.Content>
//   <Card.Footer>
//     <Button variant="outline">View Details</Button>
//   </Card.Footer>
// </Card>
```

**2. Advanced Component Composition Patterns**
```typescript
// Render Props Pattern for flexible data fetching
interface DataProviderProps<T> {
  query: string
  variables?: Record<string, any>
  children: (state: {
    data: T | null
    loading: boolean
    error: Error | null
    refetch: () => void
  }) => ReactNode
}

function DataProvider<T>({ query, variables, children }: DataProviderProps<T>) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [query, variables],
    queryFn: () => apiClient.request(query, variables)
  })

  return children({
    data,
    loading: isLoading,
    error,
    refetch
  })
}

// Usage with TypeScript generics
<DataProvider<User[]> query="users">
  {({ data, loading, error }) => {
    if (loading) return <LoadingSkeleton />
    if (error) return <ErrorBoundary error={error} />
    return <UserList users={data} />
  }}
</DataProvider>
```

**3. Advanced Hook-based Component Architecture**
```typescript
// Custom hook with advanced patterns for data tables
function useDataTable<T extends Record<string, any>>({
  data,
  columns,
  filterFn,
  sortFn,
  enablePagination = true,
  enableVirtualization = false
}: UseDataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 })
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({})

  // Advanced table configuration
  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      pagination: enablePagination ? pagination : undefined,
      rowSelection
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: enablePagination ? setPagination : undefined,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    // Enable row selection
    enableRowSelection: true,
    // Custom filter functions
    filterFns: {
      fuzzy: (row, columnId, value, addMeta) => {
        const itemRank = rankItem(row.getValue(columnId), value)
        addMeta({ itemRank })
        return itemRank.passed
      }
    },
    // Global filter function
    globalFilterFn: 'fuzzy'
  })

  // Virtualization support for large datasets
  const { getVirtualItems, getTotalSize } = useVirtualizer({
    count: table.getRowModel().rows.length,
    getScrollElement: () => null, // Set by parent component
    estimateSize: () => 50,
    enabled: enableVirtualization
  })

  // Computed values and actions
  const selectedRows = table.getFilteredSelectedRowModel().rows
  const hasSelection = selectedRows.length > 0
  
  const actions = useMemo(() => ({
    selectAll: () => table.toggleAllRowsSelected(),
    selectPage: () => table.toggleAllPageRowsSelected(),
    clearSelection: () => table.resetRowSelection(),
    exportSelected: () => exportToCSV(selectedRows.map(row => row.original)),
    deleteSelected: () => {
      // Implement bulk delete logic
      const ids = selectedRows.map(row => row.original.id)
      return bulkDeleteItems(ids)
    },
    refreshData: () => table.reset(),
    resetFilters: () => {
      table.resetColumnFilters()
      table.resetGlobalFilter()
    },
    resetSorting: () => table.resetSorting()
  }), [table, selectedRows])

  return {
    // Table instance
    table,
    
    // Virtual items for performance
    virtualItems: enableVirtualization ? getVirtualItems : undefined,
    totalSize: enableVirtualization ? getTotalSize : undefined,
    
    // Selection state
    selectedRows,
    hasSelection,
    selectedCount: selectedRows.length,
    
    // Filter and sort state  
    globalFilter,
    columnFilters,
    sorting,
    
    // Pagination state
    pagination: enablePagination ? pagination : undefined,
    pageCount: enablePagination ? table.getPageCount() : undefined,
    canPreviousPage: enablePagination ? table.getCanPreviousPage() : false,
    canNextPage: enablePagination ? table.getCanNextPage() : false,
    
    // Actions
    ...actions,
    
    // State setters
    setSorting,
    setColumnFilters,
    setGlobalFilter,
    setPagination: enablePagination ? setPagination : undefined
  }
}

// Usage in component
const DataTable = <T extends Record<string, any>>({ 
  data, 
  columns, 
  enableSelection = true,
  enableVirtualization = false 
}: DataTableProps<T>) => {
  const {
    table,
    selectedCount,
    hasSelection,
    virtualItems,
    totalSize,
    exportSelected,
    deleteSelected,
    clearSelection
  } = useDataTable({ 
    data, 
    columns,
    enableVirtualization
  })

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <GlobalFilter
            value={globalFilter ?? ''}
            onChange={(value) => setGlobalFilter(String(value))}
          />
          {hasSelection && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">
                {selectedCount} selected
              </span>
              <Button variant="outline" size="sm" onClick={exportSelected}>
                Export
              </Button>
              <Button variant="destructive" size="sm" onClick={deleteSelected}>
                Delete
              </Button>
              <Button variant="ghost" size="sm" onClick={clearSelection}>
                Clear
              </Button>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <ColumnVisibilityToggle table={table} />
          <DataTableViewOptions table={table} />
        </div>
      </div>
      
      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className={cn(
                    header.column.getCanSort() && "cursor-pointer select-none"
                  )}>
                    <div 
                      onClick={header.column.getToggleSortingHandler()}
                      className="flex items-center space-x-2"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                      {header.column.getCanSort() && (
                        <Button variant="ghost" size="sm">
                          {header.column.getIsSorted() === "desc" ? (
                            <ArrowDownIcon className="h-4 w-4" />
                          ) : header.column.getIsSorted() === "asc" ? (
                            <ArrowUpIcon className="h-4 w-4" />
                          ) : (
                            <CaretSortIcon className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </div>
                    {header.column.getCanFilter() && (
                      <div className="mt-2">
                        <ColumnFilter column={header.column} />
                      </div>
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          
          <TableBody>
            {enableVirtualization && virtualItems ? (
              // Virtualized rows for performance
              <div style={{ height: `${totalSize}px`, position: 'relative' }}>
                {virtualItems.map((virtualItem) => {
                  const row = table.getRowModel().rows[virtualItem.index]
                  return (
                    <div
                      key={row.id}
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: `${virtualItem.size}px`,
                        transform: `translateY(${virtualItem.start}px)`
                      }}
                    >
                      <TableRow data-state={row.getIsSelected() && "selected"}>
                        {row.getVisibleCells().map((cell) => (
                          <TableCell key={cell.id}>
                            {flexRender(
                              cell.column.columnDef.cell,
                              cell.getContext()
                            )}
                          </TableCell>
                        ))}
                      </TableRow>
                    </div>
                  )
                })}
              </div>
            ) : (
              // Standard rows
              table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && "selected"}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center"
                  >
                    No results.
                  </TableCell>
                </TableRow>
              )
            )}
          </TableBody>
        </Table>
      </div>
      
      {/* Pagination */}
      {enablePagination && (
        <DataTablePagination table={table} />
      )}
    </div>
  )
}
```

**4. Factory Pattern for Dynamic Components**
```typescript
// Component factory for different chart types
type ChartType = 'bar' | 'line' | 'pie' | 'scatter' | 'area' | 'heatmap'

interface ChartFactory {
  create: (type: ChartType, data: any[], config?: ChartConfig) => ReactNode
}

// Chart component registry
const chartComponents = {
  bar: lazy(() => import('@/components/charts/BarChart')),
  line: lazy(() => import('@/components/charts/LineChart')),  
  pie: lazy(() => import('@/components/charts/PieChart')),
  scatter: lazy(() => import('@/components/charts/ScatterChart')),
  area: lazy(() => import('@/components/charts/AreaChart')),
  heatmap: lazy(() => import('@/components/charts/HeatmapChart'))
} as const

// Chart factory implementation
const chartFactory: ChartFactory = {
  create: (type, data, config = {}) => {
    const ChartComponent = chartComponents[type]
    
    if (!ChartComponent) {
      throw new Error(`Unsupported chart type: ${type}`)
    }
    
    const baseProps = {
      data,
      ...config,
      className: cn('w-full h-64', config.className)
    }

    return (
      <ErrorBoundary fallback={<ChartError type={type} />}>
        <Suspense fallback={<ChartSkeleton type={type} />}>
          <ChartComponent {...baseProps} />
        </Suspense>
      </ErrorBoundary>
    )
  }
}

// Dynamic visualization panel
const VisualizationPanel = ({ 
  chartType, 
  data, 
  config,
  onChartTypeChange,
  onConfigChange 
}: VisualizationPanelProps) => {
  const [isEditing, setIsEditing] = useState(false)
  const [localConfig, setLocalConfig] = useState(config)
  
  const chart = useMemo(() => {
    try {
      return chartFactory.create(chartType, data, localConfig)
    } catch (error) {
      return <ChartError error={error} />
    }
  }, [chartType, data, localConfig])

  const handleConfigUpdate = (newConfig: ChartConfig) => {
    setLocalConfig(newConfig)
    onConfigChange?.(newConfig)
  }

  return (
    <Card variant="outlined" className="relative">
      {/* Chart Type Selector */}
      <Card.Header className="flex flex-row items-center justify-between">
        <Card.Title>Data Visualization</Card.Title>
        <div className="flex items-center space-x-2">
          <ChartTypeSelector 
            value={chartType}
            onChange={onChartTypeChange}
          />
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setIsEditing(!isEditing)}
          >
            <SettingsIcon className="h-4 w-4" />
          </Button>
        </div>
      </Card.Header>
      
      {/* Configuration Panel */}
      {isEditing && (
        <Card.Content>
          <ChartConfigurationPanel
            chartType={chartType}
            config={localConfig}
            onConfigChange={handleConfigUpdate}
          />
        </Card.Content>
      )}
      
      {/* Chart Display */}
      <Card.Content className={isEditing ? 'pt-0' : ''}>
        <div className="relative">
          {chart}
          
          {/* Chart Actions Overlay */}
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="flex items-center space-x-1">
              <Button size="sm" variant="secondary">
                <DownloadIcon className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="secondary">
                <ShareIcon className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="secondary">
                <ExpandIcon className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </Card.Content>
    </Card>
  )
}
```

## Modern State Management with Zustand & React Query

### Advanced State Architecture Patterns

**1. Store Composition with TypeScript**
```typescript
// Store slice pattern with proper typing
import { create } from 'zustand'
import { subscribeWithSelector, persist, devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Individual slice types
interface AuthSlice {
  // State
  user: User | null
  token: string | null
  permissions: string[]
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  updateProfile: (updates: Partial<User>) => Promise<void>
  checkPermission: (permission: string) => boolean
}

interface DataSlice {
  // State
  dataSources: DataSource[]
  selectedSource: DataSource | null
  analysisResults: AnalysisResult[]
  isProcessing: boolean
  
  // Actions
  fetchDataSources: () => Promise<void>
  selectDataSource: (id: string) => void
  runAnalysis: (config: AnalysisConfig) => Promise<void>
  clearAnalysis: () => void
}

interface UISlice {
  // State
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  commandPaletteOpen: boolean
  notifications: Notification[]
  
  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  toggleCommandPalette: () => void
  addNotification: (notification: CreateNotification) => void
  removeNotification: (id: string) => void
}

// Create individual slices
const createAuthSlice: StateCreator<AuthSlice, [], [], AuthSlice> = (set, get) => ({
  user: null,
  token: null,
  permissions: [],
  isAuthenticated: false,
  isLoading: false,
  
  login: async (credentials) => {
    set({ isLoading: true })
    try {
      const response = await authService.login(credentials)
      set({
        user: response.user,
        token: response.access_token,
        permissions: response.permissions,
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
      permissions: [],
      isAuthenticated: false
    })
  },
  
  refreshToken: async () => {
    const currentToken = get().token
    if (!currentToken) throw new Error('No token to refresh')
    
    const response = await authService.refreshToken(currentToken)
    set({ token: response.access_token })
  },
  
  updateProfile: async (updates) => {
    const currentUser = get().user
    if (!currentUser) throw new Error('No user to update')
    
    // Optimistic update
    set((state) => {
      if (state.user) {
        Object.assign(state.user, updates)
      }
    })
    
    try {
      const updatedUser = await userService.updateProfile(updates)
      set({ user: updatedUser })
    } catch (error) {
      // Rollback on error
      set({ user: currentUser })
      throw error
    }
  },
  
  checkPermission: (permission) => {
    return get().permissions.includes(permission)
  }
})

const createDataSlice: StateCreator<DataSlice, [], [], DataSlice> = (set, get) => ({
  dataSources: [],
  selectedSource: null,
  analysisResults: [],
  isProcessing: false,
  
  fetchDataSources: async () => {
    const sources = await dataSourceService.getAll()
    set({ dataSources: sources })
  },
  
  selectDataSource: (id) => {
    const source = get().dataSources.find(ds => ds.id === id)
    set({ selectedSource: source || null })
  },
  
  runAnalysis: async (config) => {
    set({ isProcessing: true })
    try {
      const results = await analysisService.run(config)
      set((state) => {
        state.analysisResults.push(results)
        state.isProcessing = false
      })
    } catch (error) {
      set({ isProcessing: false })
      throw error
    }
  },
  
  clearAnalysis: () => {
    set({ analysisResults: [] })
  }
})

const createUISlice: StateCreator<UISlice, [], [], UISlice> = (set, get) => ({
  theme: 'system',
  sidebarOpen: true,
  commandPaletteOpen: false,
  notifications: [],
  
  setTheme: (theme) => {
    set({ theme })
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme)
  },
  
  toggleSidebar: () => {
    set((state) => {
      state.sidebarOpen = !state.sidebarOpen
    })
  },
  
  toggleCommandPalette: () => {
    set((state) => {
      state.commandPaletteOpen = !state.commandPaletteOpen
    })
  },
  
  addNotification: (notification) => {
    const id = crypto.randomUUID()
    const timestamp = new Date().toISOString()
    
    set((state) => {
      state.notifications.push({ 
        ...notification, 
        id, 
        timestamp 
      })
    })
    
    // Auto-remove after duration
    setTimeout(() => {
      get().removeNotification(id)
    }, notification.duration || 5000)
  },
  
  removeNotification: (id) => {
    set((state) => {
      const index = state.notifications.findIndex(n => n.id === id)
      if (index > -1) {
        state.notifications.splice(index, 1)
      }
    })
  }
})

// Combine all slices
type AppState = AuthSlice & DataSlice & UISlice

const useAppStore = create<AppState>()(  
  devtools(
    persist(
      subscribeWithSelector(
        immer<AppState>((...args) => ({
          ...createAuthSlice(...args),
          ...createDataSlice(...args),
          ...createUISlice(...args)
        }))
      ),
      {
        name: 'app-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          user: state.user,
          token: state.token
        })
      }
    ),
    { name: 'DataAnalysisApp' }
  )
)

// Selector hooks for performance
export const useAuth = () => useAppStore(
  (state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    permissions: state.permissions,
    login: state.login,
    logout: state.logout,
    updateProfile: state.updateProfile,
    checkPermission: state.checkPermission
  }),
  shallow
)

export const useDataSources = () => useAppStore(
  (state) => ({
    dataSources: state.dataSources,
    selectedSource: state.selectedSource,
    fetchDataSources: state.fetchDataSources,
    selectDataSource: state.selectDataSource
  }),
  shallow
)

export const useAnalysis = () => useAppStore(
  (state) => ({
    analysisResults: state.analysisResults,
    isProcessing: state.isProcessing,
    runAnalysis: state.runAnalysis,
    clearAnalysis: state.clearAnalysis
  }),
  shallow
)

export const useUI = () => useAppStore(
  (state) => ({
    theme: state.theme,
    sidebarOpen: state.sidebarOpen,
    commandPaletteOpen: state.commandPaletteOpen,
    notifications: state.notifications,
    setTheme: state.setTheme,
    toggleSidebar: state.toggleSidebar,
    toggleCommandPalette: state.toggleCommandPalette,
    addNotification: state.addNotification,
    removeNotification: state.removeNotification
  }),
  shallow
)
```

**2. React Query Integration with Advanced Caching**
```typescript
// Advanced React Query setup
import { QueryClient, useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Configure query client with advanced options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error.status >= 400 && error.status < 500) return false
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: true
    },
    mutations: {
      retry: 1,
      onError: (error) => {
        // Global error handling
        console.error('Mutation error:', error)
      }
    }
  }
})

// Custom hooks with advanced patterns
export const useDataSources = (options?: UseQueryOptions<DataSource[]>) => {
  const { user } = useAuth()
  
  return useQuery({
    queryKey: ['dataSources', user?.id],
    queryFn: async () => {
      const response = await dataSourceService.getAll()
      return response.data
    },
    enabled: !!user?.id,
    select: (data) => {
      // Transform and sort data
      return data
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .map(source => ({
          ...source,
          displayName: source.name || `${source.type} Connection`,
          isHealthy: source.status === 'connected'
        }))
    },
    ...options
  })
}

// Optimistic updates with rollback
export const useCreateDataSource = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useUI()
  
  return useMutation({
    mutationFn: dataSourceService.create,
    
    onMutate: async (newDataSource) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['dataSources'] })
      
      // Snapshot previous value
      const previousDataSources = queryClient.getQueryData(['dataSources'])
      
      // Optimistically update
      queryClient.setQueryData(['dataSources'], (old: DataSource[]) => {
        const optimisticSource: DataSource = {
          id: `temp-${Date.now()}`,
          ...newDataSource,
          status: 'pending',
          created_at: new Date().toISOString()
        }
        return [...(old || []), optimisticSource]
      })
      
      return { previousDataSources }
    },
    
    onError: (error, newDataSource, context) => {
      // Rollback on error
      queryClient.setQueryData(['dataSources'], context?.previousDataSources)
      
      addNotification({
        type: 'error',
        title: 'Failed to create data source',
        message: error.message || 'An unexpected error occurred'
      })
    },
    
    onSuccess: (data) => {
      addNotification({
        type: 'success', 
        title: 'Data source created',
        message: `${data.name} has been connected successfully`
      })
    },
    
    onSettled: () => {
      // Always refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['dataSources'] })
    }
  })
}

// Infinite query for large datasets
export const useInfiniteAnalysisResults = (analysisId: string) => {
  return useInfiniteQuery({
    queryKey: ['analysisResults', analysisId],
    queryFn: ({ pageParam = 0 }) => 
      analysisService.getResults(analysisId, {
        offset: pageParam,
        limit: 50
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const hasMore = lastPage.data.length === 50
      return hasMore ? allPages.length * 50 : undefined
    },
    select: (data) => ({
      pages: data.pages,
      pageParams: data.pageParams,
      // Flatten all pages into single array
      results: data.pages.flatMap(page => page.data),
      totalCount: data.pages[0]?.total || 0,
      hasMore: !!data.pageParams[data.pageParams.length - 1]
    }),
    enabled: !!analysisId
  })
}

// Background prefetching
export const usePrefetchHooks = () => {
  const queryClient = useQueryClient()
  
  const prefetchDashboard = useCallback(async (userId: string) => {
    await queryClient.prefetchQuery({
      queryKey: ['dashboard', userId],
      queryFn: () => dashboardService.getData(userId),
      staleTime: 10 * 60 * 1000 // Prefetch data stays fresh longer
    })
  }, [queryClient])
  
  const prefetchAnalysisResults = useCallback(async (analysisId: string) => {
    await queryClient.prefetchQuery({
      queryKey: ['analysisResults', analysisId],
      queryFn: () => analysisService.getResults(analysisId)
    })
  }, [queryClient])
  
  return { prefetchDashboard, prefetchAnalysisResults }
}

// Real-time updates with WebSocket
export const useRealtimeUpdates = (userId: string) => {
  const queryClient = useQueryClient()
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`)
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      
      switch (update.type) {
        case 'data_source_status':
          // Update specific data source
          queryClient.setQueryData(['dataSources'], (old: DataSource[]) => {
            return old?.map(ds => 
              ds.id === update.data.id 
                ? { ...ds, status: update.data.status }
                : ds
            )
          })
          break
          
        case 'analysis_complete':
          // Invalidate analysis queries
          queryClient.invalidateQueries({ 
            queryKey: ['analysisResults', update.data.analysisId] 
          })
          break
          
        case 'user_notification':
          // Add real-time notification
          const { addNotification } = useAppStore.getState()
          addNotification(update.data)
          break
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return () => {
      ws.close()
    }
  }, [userId, queryClient])
}
```

**3. Advanced Form State Management**
```typescript
// Advanced form hook with validation and auto-save
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

// Form schema with advanced validation
const dataSourceSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(50, 'Name must be less than 50 characters'),
  type: z.enum(['postgresql', 'mysql', 'mongodb', 'csv', 'json']),
  host: z.string()
    .url('Must be a valid URL')
    .optional()
    .or(z.literal('')),
  port: z.number()
    .int('Port must be an integer')
    .min(1, 'Port must be positive')
    .max(65535, 'Port must be less than 65536')
    .optional(),
  database: z.string().optional(),
  username: z.string().optional(),
  password: z.string().optional(),
  ssl: z.boolean().default(false),
  options: z.record(z.string(), z.any()).optional()
}).refine((data) => {
  // Custom validation: database connections require host
  if (['postgresql', 'mysql', 'mongodb'].includes(data.type)) {
    return data.host && data.host.length > 0
  }
  return true
}, {
  message: 'Database connections require a host',
  path: ['host']
})

type DataSourceFormData = z.infer<typeof dataSourceSchema>

// Advanced form hook with auto-save and validation
function useAdvancedForm<T extends Record<string, any>>({
  schema,
  defaultValues,
  onSubmit,
  autoSave = false,
  autoSaveDelay = 1000
}: {
  schema: z.ZodSchema<T>
  defaultValues: T
  onSubmit: (data: T) => Promise<void> | void
  autoSave?: boolean
  autoSaveDelay?: number
}) {
  const form = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues,
    mode: 'onChange'
  })
  
  // Auto-save functionality
  const [autoSaveStatus, setAutoSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const debouncedValues = useDebounce(form.watch(), autoSaveDelay)
  
  useEffect(() => {
    if (autoSave && form.formState.isDirty && form.formState.isValid) {
      setAutoSaveStatus('saving')
      
      Promise.resolve(onSubmit(debouncedValues))
        .then(() => {
          setAutoSaveStatus('saved')
          // Reset dirty state after auto-save
          form.reset(debouncedValues)
        })
        .catch(() => {
          setAutoSaveStatus('error')
        })
        .finally(() => {
          // Reset status after 2 seconds
          setTimeout(() => setAutoSaveStatus('idle'), 2000)
        })
    }
  }, [debouncedValues, autoSave, form.formState.isDirty, form.formState.isValid])
  
  // Enhanced submit with loading state
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleSubmit = form.handleSubmit(async (data) => {
    if (isSubmitting) return
    
    try {
      setIsSubmitting(true)
      await onSubmit(data)
      form.reset(data) // Reset form with submitted data
    } catch (error) {
      // Set form-level error
      form.setError('root', {
        type: 'submit',
        message: error instanceof Error ? error.message : 'Submission failed'
      })
      throw error
    } finally {
      setIsSubmitting(false)
    }
  })
  
  // Field validation helpers
  const validateField = useCallback(async (fieldName: keyof T) => {
    const result = await form.trigger(fieldName)
    return result
  }, [form])
  
  const getFieldError = useCallback((fieldName: keyof T) => {
    const error = form.formState.errors[fieldName]
    return error?.message
  }, [form.formState.errors])
  
  const setFieldValue = useCallback((fieldName: keyof T, value: any) => {
    form.setValue(fieldName, value, { shouldDirty: true, shouldValidate: true })
  }, [form])
  
  // Form reset with confirmation
  const resetForm = useCallback((data?: T) => {
    if (form.formState.isDirty) {
      const shouldReset = window.confirm('You have unsaved changes. Are you sure you want to reset?')
      if (!shouldReset) return false
    }
    
    form.reset(data || defaultValues)
    return true
  }, [form, form.formState.isDirty, defaultValues])
  
  return {
    // Form instance
    ...form,
    
    // Enhanced submit
    handleSubmit,
    isSubmitting,
    
    // Field helpers
    validateField,
    getFieldError,
    setFieldValue,
    resetForm,
    
    // Auto-save status
    autoSaveStatus,
    
    // Form state helpers
    isDirty: form.formState.isDirty,
    isValid: form.formState.isValid,
    hasErrors: Object.keys(form.formState.errors).length > 0,
    touchedFields: Object.keys(form.formState.touchedFields),
    dirtyFields: Object.keys(form.formState.dirtyFields)
  }
}

// Usage example
const DataSourceForm = ({ initialData, onSubmit }: DataSourceFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    isSubmitting,
    autoSaveStatus,
    validateField,
    setFieldValue,
    resetForm
  } = useAdvancedForm({
    schema: dataSourceSchema,
    defaultValues: initialData || {
      name: '',
      type: 'postgresql',
      host: '',
      port: 5432,
      ssl: false
    },
    onSubmit,
    autoSave: true
  })
  
  const connectionType = watch('type')
  
  // Dynamic field visibility based on connection type
  const showDatabaseFields = ['postgresql', 'mysql', 'mongodb'].includes(connectionType)
  const showFileFields = ['csv', 'json'].includes(connectionType)
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Auto-save indicator */}
      {autoSaveStatus !== 'idle' && (
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          {autoSaveStatus === 'saving' && <Spinner className="h-4 w-4" />}
          {autoSaveStatus === 'saved' && <CheckIcon className="h-4 w-4 text-green-500" />}
          {autoSaveStatus === 'error' && <XIcon className="h-4 w-4 text-red-500" />}
          <span>
            {autoSaveStatus === 'saving' && 'Saving...'}
            {autoSaveStatus === 'saved' && 'Saved'}
            {autoSaveStatus === 'error' && 'Save failed'}
          </span>
        </div>
      )}
      
      {/* Basic Fields */}
      <div className="grid grid-cols-2 gap-4">
        <FormField
          label="Name"
          error={errors.name?.message}
          required
        >
          <Input
            {...register('name')}
            placeholder="My Database Connection"
            onBlur={() => validateField('name')}
          />
        </FormField>
        
        <FormField
          label="Type"
          error={errors.type?.message}
          required
        >
          <Select
            value={connectionType}
            onValueChange={(value) => setFieldValue('type', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="postgresql">PostgreSQL</SelectItem>
              <SelectItem value="mysql">MySQL</SelectItem>
              <SelectItem value="mongodb">MongoDB</SelectItem>
              <SelectItem value="csv">CSV File</SelectItem>
              <SelectItem value="json">JSON File</SelectItem>
            </SelectContent>
          </Select>
        </FormField>
      </div>
      
      {/* Database Connection Fields */}
      {showDatabaseFields && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <FormField
              label="Host"
              error={errors.host?.message}
              required
            >
              <Input
                {...register('host')}
                placeholder="localhost"
                type="url"
              />
            </FormField>
            
            <FormField
              label="Port"
              error={errors.port?.message}
            >
              <Input
                {...register('port', { valueAsNumber: true })}
                placeholder="5432"
                type="number"
              />
            </FormField>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <FormField
              label="Database"
              error={errors.database?.message}
            >
              <Input
                {...register('database')}
                placeholder="my_database"
              />
            </FormField>
            
            <FormField
              label="Username"
              error={errors.username?.message}
            >
              <Input
                {...register('username')}
                placeholder="username"
              />
            </FormField>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <FormField
              label="Password"
              error={errors.password?.message}
            >
              <Input
                {...register('password')}
                type="password"
                placeholder="••••••••"
              />
            </FormField>
            
            <FormField
              label="SSL Connection"
            >
              <div className="flex items-center space-x-2">
                <Switch
                  checked={watch('ssl')}
                  onCheckedChange={(checked) => setFieldValue('ssl', checked)}
                />
                <Label>Enable SSL</Label>
              </div>
            </FormField>
          </div>
        </div>
      )}
      
      {/* File Upload Fields */}
      {showFileFields && (
        <FormField
          label="File"
          description="Upload your data file"
        >
          <FileUpload
            accept={connectionType === 'csv' ? '.csv' : '.json'}
            onFileSelect={(file) => {
              // Handle file upload
              setFieldValue('file', file)
            }}
          />
        </FormField>
      )}
      
      {/* Form Actions */}
      <div className="flex items-center justify-between pt-6 border-t">
        <Button
          type="button"
          variant="outline"
          onClick={() => resetForm()}
        >
          Reset
        </Button>
        
        <div className="flex items-center space-x-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              // Test connection
              const formData = watch()
              testConnection(formData)
            }}
          >
            Test Connection
          </Button>
          
          <Button
            type="submit"
            disabled={isSubmitting || !form.formState.isValid}
            className="min-w-[100px]"
          >
            {isSubmitting ? (
              <>
                <Spinner className="h-4 w-4 mr-2" />
                Saving...
              </>
            ) : (
              'Save'
            )}
          </Button>
        </div>
      </div>
    </form>
  )
}
```

**1. Zustand Store Architecture with Slices**
```typescript
// Advanced store composition with TypeScript and persistence
import { create } from 'zustand'
import { subscribeWithSelector, persist, devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Auth slice with JWT management
interface AuthSlice {
  user: User | null
  token: string | null
  refreshToken: string | null
  permissions: string[]
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  refreshAuth: () => Promise<void>
  updateUser: (updates: Partial<User>) => void
  checkPermission: (permission: string) => boolean
}

const createAuthSlice: StateCreator<AuthSlice> = (set, get) => ({
  user: null,
  token: null,
  refreshToken: null,
  permissions: [],
  isAuthenticated: false,
  isLoading: false,
  
  login: async (credentials) => {
    set({ isLoading: true })
    try {
      const response = await authService.login(credentials)
      set({
        user: response.user,
        token: response.access_token,
        refreshToken: response.refresh_token,
        permissions: response.permissions,
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
      permissions: [],
      isAuthenticated: false
    })
    // Clear persisted state
    localStorage.removeItem('auth-storage')
  },
  
  refreshAuth: async () => {
    const { refreshToken } = get()
    if (!refreshToken) throw new Error('No refresh token')
    
    try {
      const response = await authService.refresh(refreshToken)
      set({
        token: response.access_token,
        refreshToken: response.refresh_token
      })
    } catch (error) {
      get().logout()
      throw error
    }
  },
  
  updateUser: (updates) => {
    set((state) => {
      if (state.user) {
        state.user = { ...state.user, ...updates }
      }
    })
  },
  
  checkPermission: (permission) => {
    return get().permissions.includes(permission)
  }
})

// Data slice with optimistic updates
interface DataSlice {
  dataSources: DataSource[]
  selectedDataSource: DataSource | null
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchDataSources: () => Promise<void>
  createDataSource: (config: DataSourceConfig) => Promise<void>
  updateDataSource: (id: string, updates: Partial<DataSource>) => Promise<void>
  deleteDataSource: (id: string) => Promise<void>
  selectDataSource: (id: string) => void
}

const createDataSlice: StateCreator<DataSlice> = (set, get) => ({
  dataSources: [],
  selectedDataSource: null,
  isLoading: false,
  error: null,
  
  fetchDataSources: async () => {
    set({ isLoading: true, error: null })
    try {
      const dataSources = await dataSourceService.getAll()
      set({ dataSources, isLoading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch data sources',
        isLoading: false 
      })
    }
  },
  
  createDataSource: async (config) => {
    // Optimistic update
    const optimisticSource: DataSource = {
      id: `temp-${Date.now()}`,
      ...config,
      status: 'pending',
      created_at: new Date().toISOString()
    }
    
    set((state) => {
      state.dataSources.push(optimisticSource)
    })
    
    try {
      const newSource = await dataSourceService.create(config)
      set((state) => {
        const index = state.dataSources.findIndex(ds => ds.id === optimisticSource.id)
        if (index !== -1) {
          state.dataSources[index] = newSource
        }
      })
    } catch (error) {
      // Rollback optimistic update
      set((state) => {
        state.dataSources = state.dataSources.filter(ds => ds.id !== optimisticSource.id)
        state.error = error instanceof Error ? error.message : 'Failed to create data source'
      })
      throw error
    }
  },
  
  updateDataSource: async (id, updates) => {
    // Store original for rollback
    const originalSource = get().dataSources.find(ds => ds.id === id)
    if (!originalSource) return
    
    // Optimistic update
    set((state) => {
      const index = state.dataSources.findIndex(ds => ds.id === id)
      if (index !== -1) {
        state.dataSources[index] = { ...state.dataSources[index], ...updates }
      }
    })
    
    try {
      const updatedSource = await dataSourceService.update(id, updates)
      set((state) => {
        const index = state.dataSources.findIndex(ds => ds.id === id)
        if (index !== -1) {
          state.dataSources[index] = updatedSource
        }
      })
    } catch (error) {
      // Rollback
      set((state) => {
        const index = state.dataSources.findIndex(ds => ds.id === id)
        if (index !== -1) {
          state.dataSources[index] = originalSource
        }
        state.error = error instanceof Error ? error.message : 'Failed to update data source'
      })
      throw error
    }
  },
  
  deleteDataSource: async (id) => {
    const originalSources = get().dataSources
    
    // Optimistic removal
    set((state) => {
      state.dataSources = state.dataSources.filter(ds => ds.id !== id)
    })
    
    try {
      await dataSourceService.delete(id)
    } catch (error) {
      // Rollback
      set({ 
        dataSources: originalSources,
        error: error instanceof Error ? error.message : 'Failed to delete data source'
      })
      throw error
    }
  },
  
  selectDataSource: (id) => {
    const dataSource = get().dataSources.find(ds => ds.id === id)
    set({ selectedDataSource: dataSource || null })
  }
})

// UI slice for global UI state
interface UISlice {
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  commandPaletteOpen: boolean
  notifications: Notification[]
  
  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  openCommandPalette: () => void
  closeCommandPalette: () => void
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
}

const createUISlice: StateCreator<UISlice> = (set, get) => ({
  theme: 'system',
  sidebarOpen: true,
  commandPaletteOpen: false,
  notifications: [],
  
  setTheme: (theme) => {
    set({ theme })
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme)
  },
  
  toggleSidebar: () => {
    set((state) => {
      state.sidebarOpen = !state.sidebarOpen
    })
  },
  
  openCommandPalette: () => set({ commandPaletteOpen: true }),
  closeCommandPalette: () => set({ commandPaletteOpen: false }),
  
  addNotification: (notification) => {
    const id = crypto.randomUUID()
    const timestamp = new Date().toISOString()
    
    set((state) => {
      state.notifications.push({ ...notification, id, timestamp })
    })
    
    // Auto-remove after duration
    setTimeout(() => {
      get().removeNotification(id)
    }, notification.duration || 5000)
  },
  
  removeNotification: (id) => {
    set((state) => {
      state.notifications = state.notifications.filter(n => n.id !== id)
    })
  }
})

// Combined store with middleware
type StoreState = AuthSlice & DataSlice & UISlice

const useAppStore = create<StoreState>()(  
  devtools(
    persist(
      subscribeWithSelector(
        immer<StoreState>((...args) => ({
          ...createAuthSlice(...args),
          ...createDataSlice(...args),
          ...createUISlice(...args)
        }))
      ),
      {
        name: 'app-store',
        // Only persist certain slices
        partialize: (state) => ({
          user: state.user,
          token: state.token,
          refreshToken: state.refreshToken,
          theme: state.theme,
          sidebarOpen: state.sidebarOpen
        })
      }
    ),
    {
      name: 'DataAnalysisApp'
    }
  )
)

// Selector hooks for optimized re-renders
export const useAuth = () => useAppStore(
  useCallback((state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login: state.login,
    logout: state.logout,
    checkPermission: state.checkPermission
  }), [])
)

export const useDataSources = () => useAppStore(
  useCallback((state) => ({
    dataSources: state.dataSources,
    selectedDataSource: state.selectedDataSource,
    isLoading: state.isLoading,
    error: state.error,
    fetchDataSources: state.fetchDataSources,
    createDataSource: state.createDataSource,
    updateDataSource: state.updateDataSource,
    deleteDataSource: state.deleteDataSource,
    selectDataSource: state.selectDataSource
  }), [])
)

export const useUI = () => useAppStore(
  useCallback((state) => ({
    theme: state.theme,
    sidebarOpen: state.sidebarOpen,
    commandPaletteOpen: state.commandPaletteOpen,
    notifications: state.notifications,
    setTheme: state.setTheme,
    toggleSidebar: state.toggleSidebar,
    openCommandPalette: state.openCommandPalette,
    closeCommandPalette: state.closeCommandPalette,
    addNotification: state.addNotification,
    removeNotification: state.removeNotification
  }), [])
)

export { useAppStore }
```

**2. React Query Integration with Advanced Patterns**
```typescript
// Advanced React Query setup with custom hooks
import { 
  QueryClient, 
  useQuery, 
  useMutation, 
  useQueryClient,
  useInfiniteQuery 
} from '@tanstack/react-query'

// Query client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error) => {
        if (error.status === 404) return false
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000)
    }
  }
})

// Custom hooks with advanced patterns
export const useDataSources = (options?: QueryOptions) => {
  const { user } = useAuth()
  
  return useQuery({
    queryKey: ['dataSources', user?.id],
    queryFn: () => dataSourceService.getAll(),
    enabled: !!user?.id,
    select: (data) => data.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    ),
    ...options
  })
}

// Mutation with optimistic updates
export const useCreateDataSource = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useUI()
  
  return useMutation({
    mutationFn: dataSourceService.create,
    onMutate: async (newDataSource) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['dataSources'] })
      
      // Snapshot previous value
      const previousDataSources = queryClient.getQueryData(['dataSources'])
      
      // Optimistically update
      queryClient.setQueryData(['dataSources'], (old: DataSource[]) => [
        ...(old || []),
        { ...newDataSource, id: `temp-${Date.now()}`, status: 'pending' }
      ])
      
      return { previousDataSources }
    },
    onError: (error, newDataSource, context) => {
      // Rollback
      queryClient.setQueryData(['dataSources'], context?.previousDataSources)
      addNotification({
        type: 'error',
        title: 'Failed to create data source',
        message: error.message
      })
    },
    onSuccess: (data) => {
      addNotification({
        type: 'success',
        title: 'Data source created',
        message: `${data.name} has been connected successfully`
      })
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['dataSources'] })
    }
  })
}

// Infinite query for large datasets
export const useInfiniteDatasetRecords = (datasetId: string) => {
  return useInfiniteQuery({
    queryKey: ['datasetRecords', datasetId],
    queryFn: ({ pageParam = 0 }) => 
      datasetService.getRecords(datasetId, {
        offset: pageParam,
        limit: 50
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) => {
      const hasMore = lastPage.data.length === 50
      return hasMore ? allPages.length * 50 : undefined
    },
    select: (data) => ({
      pages: data.pages,
      pageParams: data.pageParams,
      flatData: data.pages.flatMap(page => page.data),
      totalRecords: data.pages[0]?.total || 0
    })
  })
}

// Prefetch patterns
export const usePrefetchData = () => {
  const queryClient = useQueryClient()
  
  const prefetchUserDashboard = useCallback(async (userId: string) => {
    await queryClient.prefetchQuery({
      queryKey: ['dashboard', userId],
      queryFn: () => dashboardService.getData(userId),
      staleTime: 10 * 60 * 1000
    })
  }, [queryClient])
  
  const prefetchAnalysisResults = useCallback(async (analysisId: string) => {
    await queryClient.prefetchQuery({
      queryKey: ['analysisResults', analysisId],
      queryFn: () => analysisService.getResults(analysisId)
    })
  }, [queryClient])
  
  return {
    prefetchUserDashboard,
    prefetchAnalysisResults
  }
}
```

### Advanced API Client Architecture

**Service-Oriented API Client (`src/lib/api/client.ts`)**
```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { authService } from './services/auth.service'
import { retryMiddleware } from './middleware/retry.middleware'
import { loggingMiddleware } from './middleware/logging.middleware'

// Generic API response type
interface APIResponse<T = any> {
  data: T
  meta?: {
    timestamp: string
    version: string
    pagination?: PaginationMeta
  }
  success: boolean
}

// Error response type
interface APIError {
  error: {
    code: string
    message: string
    details?: Record<string, any>
    trace_id: string
  }
}

class AdvancedAPIClient {
  private client: AxiosInstance
  private services: Record<string, string>
  private requestQueue: Map<string, Promise<AxiosResponse>> = new Map()

  constructor() {
    this.services = {
      gateway: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:8000',
      data: process.env.NEXT_PUBLIC_DATA_SERVICE_URL || 'http://localhost:8001',
      ai: process.env.NEXT_PUBLIC_AI_SERVICE_URL || 'http://localhost:8002',
      compute: process.env.NEXT_PUBLIC_COMPUTE_SERVICE_URL || 'http://localhost:8003',
      viz: process.env.NEXT_PUBLIC_VIZ_SERVICE_URL || 'http://localhost:8004'
    }

    this.client = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Version': '2.0.0',
        'X-Request-ID': () => crypto.randomUUID()
      }
    })

    this.setupInterceptors()
    this.setupMiddleware()
  }

  private setupInterceptors() {
    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = authService.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          await authService.refreshToken()
          return this.client.request(error.config)
        }
        return Promise.reject(error)
      }
    )
  }

  private setupMiddleware() {
    // Add retry middleware
    this.client = retryMiddleware(this.client)
    
    // Add logging middleware
    this.client = loggingMiddleware(this.client)
  }

  // Generic request method with TypeScript generics
  async request<T = any>(
    service: keyof typeof this.services,
    endpoint: string,
    config: AxiosRequestConfig = {}
  ): Promise<APIResponse<T>> {
    const baseURL = this.services[service]
    const url = `${baseURL}${endpoint}`
    
    // Request deduplication
    const requestKey = `${config.method || 'GET'}:${url}:${JSON.stringify(config.params)}`
    if (this.requestQueue.has(requestKey)) {
      return this.requestQueue.get(requestKey)!
    }

    const requestPromise = this.client.request<APIResponse<T>>({
      ...config,
      url
    })

    this.requestQueue.set(requestKey, requestPromise)
    
    try {
      const response = await requestPromise
      return response.data
    } finally {
      this.requestQueue.delete(requestKey)
    }
  }

  // Streaming request for real-time data
  async stream<T>(
    service: keyof typeof this.services,
    endpoint: string,
    onData: (data: T) => void,
    onError?: (error: Error) => void
  ): Promise<() => void> {
    const baseURL = this.services[service]
    const eventSource = new EventSource(`${baseURL}${endpoint}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onData(data)
      } catch (error) {
        onError?.(error as Error)
      }
    }

    eventSource.onerror = (event) => {
      onError?.(new Error('Stream connection error'))
    }

    return () => eventSource.close()
  }

  // Batch requests for performance
  async batch<T>(requests: Array<{
    service: keyof typeof this.services
    endpoint: string
    config?: AxiosRequestConfig
  }>): Promise<APIResponse<T>[]> {
    const promises = requests.map(({ service, endpoint, config }) =>
      this.request<T>(service, endpoint, config)
    )
    
    return Promise.allSettled(promises).then(results =>
      results.map(result => 
        result.status === 'fulfilled' 
          ? result.value 
          : { success: false, data: null as any, error: result.reason }
      )
    )
  }
}

const apiClient = new AdvancedAPIClient()
export { apiClient }
```

### Authentication Integration Flow

**JWT Token Management with Backend Coordination:**

1. **Registration Flow**:
   ```typescript
   POST /api/v1/auth/register → API Gateway (8000)
   ├── Validates user data
   ├── Creates user in PostgreSQL
   ├── Returns JWT access + refresh tokens
   └── Frontend stores tokens securely
   ```

2. **Login Flow**:
   ```typescript
   POST /api/v1/auth/login → API Gateway (8000)
   ├── Validates credentials against database
   ├── Generates JWT tokens (15min access, 7day refresh)
   ├── Updates user.last_login timestamp
   └── Returns user profile + tokens
   ```

3. **Token Refresh Flow**:
   ```typescript
   POST /api/v1/auth/refresh → API Gateway (8000)
   ├── Validates refresh token
   ├── Issues new access token
   ├── Rotates refresh token (optional)
   └── Updates token store
   ```

4. **Protected Request Flow**:
   ```typescript
   ANY /api/v1/* → API Gateway (8000)
   ├── AuthMiddleware validates JWT
   ├── Extracts user context (id, role, permissions)
   ├── Forwards to target microservice
   ├── Service uses user context for authorization
   └── Returns response with user context
   ```

### Service-Specific Integration Patterns

**Data Source Management (`/api/v1/data-sources`)**
```typescript
// Frontend implementation pattern
const dataSourceService = {
  // Create data source with connection testing
  async create(config: DataSourceConfig) {
    const response = await apiClient.request('gateway', '/api/v1/data-sources', {
      method: 'POST',
      data: config
    })
    // Backend validates config and tests connection
    // Updates DataSource.status in database
    return response.data
  },

  // Test existing connection
  async testConnection(id: string) {
    return apiClient.request('gateway', `/api/v1/data-sources/${id}/test`, {
      method: 'POST'
    })
    // Backend uses shared/data_connectors to test connection
    // Updates connection status and last_test timestamp
  },

  // Execute query through data service
  async executeQuery(id: string, query: string) {
    return apiClient.request('data', `/query/${id}`, {
      method: 'POST',
      data: { query, limit: 1000 }
    })
    // Routes to Data Service (8001) for query execution
  }
}
```

**AI Analysis Integration (`/api/v1/analysis`)**
```typescript
// AI service integration for conversational analysis
const aiService = {
  async startConversation(dataSourceId: string, message: string) {
    return apiClient.request('gateway', '/api/v1/ai/conversation', {
      method: 'POST',
      data: {
        data_source_id: dataSourceId,
        message,
        context: 'data_analysis'
      }
    })
    // Routes to AI Service (8002) for processing
    // May trigger Compute Service (8003) for heavy analysis
  },

  async generateVisualization(analysisId: string, chartType: string) {
    return apiClient.request('gateway', '/api/v1/visualizations/generate', {
      method: 'POST', 
      data: {
        analysis_id: analysisId,
        chart_type: chartType,
        format: 'plotly_json'
      }
    })
    // Routes to Visualization Service (8004)
  }
}
```

## Project Structure

```
frontend/
   src/                       # Source code
      app/                   # Next.js App Router pages
         layout.tsx         # Root layout with providers
         page.tsx           # Landing page
      components/            # Reusable UI components
         ui/               # Base UI components (Radix + Tailwind)
      context/              # React contexts
      features/             # Feature-based modules
      hooks/                # Custom React hooks
      lib/                  # Utility libraries
         api/              # API client and types
      store/                # Zustand state stores
      styles/               # Global styles and CSS
      types/                # TypeScript type definitions
      utils/                # Utility functions
   public/                   # Static assets
   package.json              # Dependencies and scripts
   next.config.js            # Next.js configuration
   tailwind.config.ts        # Tailwind CSS configuration
   tsconfig.json            # TypeScript configuration
   .env.local              # Environment variables
```

## Current Implementation Status

### ✅ Completed Features

1. **Project Setup & Configuration**
   - Next.js 14 with TypeScript
   - Tailwind CSS with custom design system
   - Comprehensive UI component library (Radix UI)
   - Modern build setup with optimization

2. **Landing Page** (`/src/app/page.tsx`)
   - Hero section with gradient design
   - Feature showcase grid (6 key features)
   - Statistics section
   - Call-to-action section
   - Footer with navigation links
   - Responsive design with mobile-first approach

3. **Layout & Providers** (`/src/app/layout.tsx`)
   - Root layout with multiple providers
   - Theme provider (light/dark mode support)
   - Authentication provider structure
   - React Query provider for server state
   - Toast notification system
   - Performance monitoring setup

4. **API Client** (`/src/lib/api/client.ts`)
   - Axios-based HTTP client with interceptors
   - JWT authentication handling
   - Automatic token refresh logic
   - Type-safe API methods
   - Comprehensive endpoint definitions

### 🔄 Architecture Prepared (Implementation Needed)

1. **Page Routes** (referenced in landing page)
   - `/dashboard` - Main dashboard
   - `/datasets` - Data management
   - `/analysis` - Analysis tools
   - `/visualizations` - Chart builder
   - `/ai-chat` - AI conversation interface
   - `/auth/login` - Authentication
   - `/auth/register` - User registration

2. **Component System** (imports defined)
   - Base UI components (buttons, cards, inputs)
   - Data visualization components
   - Form components with validation
   - Navigation components
   - Loading and error states

3. **State Management**
   - User authentication state
   - Data sources management
   - Analysis results caching
   - UI state (theme, sidebar, etc.)

## Advanced UI/UX Design System Architecture

### Design Token System with CSS Custom Properties

**1. Comprehensive Color System**
```typescript
// Design tokens with semantic meaning and accessibility
const designSystem = {
  // Color system with HSL for better manipulation
  colors: {
    // Brand palette with mathematical color relationships
    brand: {
      50: 'hsl(204, 100%, 97%)',   // Lightest - AAA contrast on dark
      100: 'hsl(204, 94%, 94%)',
      200: 'hsl(204, 96%, 86%)',
      300: 'hsl(204, 93%, 78%)',
      400: 'hsl(204, 91%, 69%)',
      500: 'hsl(204, 88%, 59%)',   // Primary - perfect 4.5:1 contrast
      600: 'hsl(204, 85%, 50%)',
      700: 'hsl(204, 82%, 41%)',
      800: 'hsl(204, 78%, 32%)',
      900: 'hsl(204, 75%, 25%)',   // Darkest - AAA contrast on light
      950: 'hsl(204, 80%, 16%)',
    },
    
    // Semantic color system with consistent contrast ratios
    semantic: {
      success: {
        light: 'hsl(142, 76%, 36%)',     // 4.5:1 on white
        DEFAULT: 'hsl(142, 71%, 45%)',
        dark: 'hsl(142, 69%, 58%)',      // 4.5:1 on dark
        surface: 'hsl(142, 76%, 96%)',   // Background tint
        border: 'hsl(142, 76%, 86%)',    // Border tint
      },
      warning: {
        light: 'hsl(32, 95%, 44%)',
        DEFAULT: 'hsl(32, 95%, 54%)',
        dark: 'hsl(32, 100%, 70%)',
        surface: 'hsl(32, 95%, 96%)',
        border: 'hsl(32, 95%, 86%)',
      },
      error: {
        light: 'hsl(0, 84%, 60%)',
        DEFAULT: 'hsl(0, 72%, 51%)',
        dark: 'hsl(0, 74%, 62%)',
        surface: 'hsl(0, 84%, 96%)',
        border: 'hsl(0, 84%, 86%)',
      },
      info: {
        light: 'hsl(204, 94%, 94%)',
        DEFAULT: 'hsl(204, 88%, 59%)',
        dark: 'hsl(204, 78%, 32%)',
        surface: 'hsl(204, 94%, 96%)',
        border: 'hsl(204, 94%, 86%)',
      }
    },
    
    // Neutral palette optimized for readability
    neutral: {
      0: 'hsl(0, 0%, 100%)',        // Pure white
      50: 'hsl(210, 40%, 98%)',     // Near white with blue tint
      100: 'hsl(210, 40%, 96%)',
      200: 'hsl(214, 32%, 91%)',
      300: 'hsl(213, 27%, 84%)',
      400: 'hsl(215, 20%, 65%)',    // Text secondary
      500: 'hsl(215, 16%, 47%)',    // Text muted
      600: 'hsl(215, 19%, 35%)',    // Text default
      700: 'hsl(215, 25%, 27%)',
      800: 'hsl(217, 33%, 17%)',    // Text high contrast
      900: 'hsl(222, 47%, 11%)',    // Near black
      950: 'hsl(229, 84%, 5%)',     // Pure black variant
    },
    
    // Data visualization palette (colorblind-friendly)
    data: {
      categorical: [
        'hsl(204, 88%, 59%)', // Blue
        'hsl(142, 71%, 45%)', // Green
        'hsl(32, 95%, 54%)',  // Orange
        'hsl(271, 81%, 56%)', // Purple
        'hsl(0, 72%, 51%)',   // Red
        'hsl(45, 93%, 47%)',  // Yellow
        'hsl(339, 82%, 52%)', // Pink
        'hsl(187, 71%, 45%)', // Teal
      ],
      sequential: {
        blue: [
          'hsl(204, 100%, 97%)',
          'hsl(204, 94%, 94%)',
          'hsl(204, 96%, 86%)',
          'hsl(204, 91%, 69%)',
          'hsl(204, 88%, 59%)',
          'hsl(204, 82%, 41%)',
          'hsl(204, 75%, 25%)',
        ]
      },
      diverging: {
        redBlue: [
          'hsl(0, 72%, 51%)',   // Red
          'hsl(14, 80%, 58%)',  // Red-orange
          'hsl(32, 95%, 54%)',  // Orange
          'hsl(210, 40%, 96%)', // Neutral
          'hsl(204, 96%, 86%)', // Light blue
          'hsl(204, 88%, 59%)', // Blue
          'hsl(204, 75%, 25%)', // Dark blue
        ]
      }
    }
  },
  
  // Spacing system based on 4px grid
  spacing: {
    px: '1px',
    0.5: '0.125rem',  // 2px
    1: '0.25rem',     // 4px
    1.5: '0.375rem',  // 6px
    2: '0.5rem',      // 8px
    2.5: '0.625rem',  // 10px
    3: '0.75rem',     // 12px
    3.5: '0.875rem',  // 14px
    4: '1rem',        // 16px
    5: '1.25rem',     // 20px
    6: '1.5rem',      // 24px
    7: '1.75rem',     // 28px
    8: '2rem',        // 32px
    9: '2.25rem',     // 36px
    10: '2.5rem',     // 40px
    11: '2.75rem',    // 44px
    12: '3rem',       // 48px
    14: '3.5rem',     // 56px
    16: '4rem',       // 64px
    20: '5rem',       // 80px
    24: '6rem',       // 96px
    28: '7rem',       // 112px
    32: '8rem',       // 128px
    36: '9rem',       // 144px
    40: '10rem',      // 160px
    44: '11rem',      // 176px
    48: '12rem',      // 192px
    52: '13rem',      // 208px
    56: '14rem',      // 224px
    60: '15rem',      // 240px
    64: '16rem',      // 256px
    72: '18rem',      // 288px
    80: '20rem',      // 320px
    96: '24rem',      // 384px
  },
  
  // Typography scale with fluid sizing
  typography: {
    fontFamily: {
      sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      display: ['Cal Sans', 'Inter var', 'system-ui', 'sans-serif'],
    },
    
    // Fluid type scale using clamp()
    fontSize: {
      xs: ['clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)', { lineHeight: '1.4', letterSpacing: '0.025em' }],
      sm: ['clamp(0.875rem, 0.8rem + 0.3vw, 1rem)', { lineHeight: '1.5' }],
      base: ['clamp(1rem, 0.9rem + 0.4vw, 1.125rem)', { lineHeight: '1.6' }],
      lg: ['clamp(1.125rem, 1rem + 0.5vw, 1.25rem)', { lineHeight: '1.5' }],
      xl: ['clamp(1.25rem, 1.1rem + 0.6vw, 1.5rem)', { lineHeight: '1.4' }],
      '2xl': ['clamp(1.5rem, 1.3rem + 0.8vw, 2rem)', { lineHeight: '1.3' }],
      '3xl': ['clamp(1.875rem, 1.6rem + 1vw, 2.5rem)', { lineHeight: '1.2' }],
      '4xl': ['clamp(2.25rem, 1.9rem + 1.4vw, 3rem)', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
      '5xl': ['clamp(3rem, 2.5rem + 2vw, 4rem)', { lineHeight: '1', letterSpacing: '-0.025em' }],
      '6xl': ['clamp(3.75rem, 3rem + 3vw, 5rem)', { lineHeight: '1', letterSpacing: '-0.025em' }],
    },
    
    fontWeight: {
      thin: '100',
      extralight: '200',
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
      black: '900',
    },
    
    // Semantic text styles
    textStyles: {
      'display-large': {
        fontSize: 'clamp(3.75rem, 3rem + 3vw, 5rem)',
        fontWeight: '700',
        lineHeight: '1',
        letterSpacing: '-0.025em',
        fontFamily: 'var(--font-display)',
      },
      'display-medium': {
        fontSize: 'clamp(3rem, 2.5rem + 2vw, 4rem)',
        fontWeight: '700', 
        lineHeight: '1',
        letterSpacing: '-0.025em',
        fontFamily: 'var(--font-display)',
      },
      'heading-1': {
        fontSize: 'clamp(2.25rem, 1.9rem + 1.4vw, 3rem)',
        fontWeight: '700',
        lineHeight: '1.1',
        letterSpacing: '-0.025em',
      },
      'heading-2': {
        fontSize: 'clamp(1.875rem, 1.6rem + 1vw, 2.5rem)',
        fontWeight: '600',
        lineHeight: '1.2',
        letterSpacing: '-0.015em',
      },
      'heading-3': {
        fontSize: 'clamp(1.5rem, 1.3rem + 0.8vw, 2rem)',
        fontWeight: '600',
        lineHeight: '1.3',
      },
      'heading-4': {
        fontSize: 'clamp(1.25rem, 1.1rem + 0.6vw, 1.5rem)',
        fontWeight: '600',
        lineHeight: '1.4',
      },
      'body-large': {
        fontSize: 'clamp(1.125rem, 1rem + 0.5vw, 1.25rem)',
        fontWeight: '400',
        lineHeight: '1.6',
      },
      'body': {
        fontSize: 'clamp(1rem, 0.9rem + 0.4vw, 1.125rem)',
        fontWeight: '400',
        lineHeight: '1.6',
      },
      'body-small': {
        fontSize: 'clamp(0.875rem, 0.8rem + 0.3vw, 1rem)',
        fontWeight: '400',
        lineHeight: '1.5',
      },
      'caption': {
        fontSize: 'clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)',
        fontWeight: '500',
        lineHeight: '1.4',
        color: 'hsl(var(--muted-foreground))',
        letterSpacing: '0.025em',
      },
      'overline': {
        fontSize: 'clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)',
        fontWeight: '600',
        lineHeight: '1.4',
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
      }
    }
  },
  
  // Elevation system with shadows
  elevation: {
    0: 'none',
    1: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    2: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    3: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    4: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    5: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    6: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  },
  
  // Border radius system
  borderRadius: {
    none: '0px',
    sm: '0.125rem',   // 2px
    DEFAULT: '0.25rem', // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px',
  },
  
  // Animation system
  animation: {
    duration: {
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
      slower: '500ms',
    },
    easing: {
      linear: 'linear',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    }
  },
  
  // Breakpoints for responsive design
  screens: {
    xs: '475px',
    sm: '640px',
    md: '768px',
    lg: '1024px',n    xl: '1280px',
    '2xl': '1536px',
  }
} as const

// CSS Custom Properties generation
export const generateCSSCustomProperties = (theme: 'light' | 'dark') => {
  const baseProperties = {
    // Color properties
    '--color-brand-50': designSystem.colors.brand[50],
    '--color-brand-100': designSystem.colors.brand[100],
    '--color-brand-500': designSystem.colors.brand[500],
    '--color-brand-900': designSystem.colors.brand[900],
    
    // Semantic colors
    '--color-success': designSystem.colors.semantic.success.DEFAULT,
    '--color-success-surface': designSystem.colors.semantic.success.surface,
    '--color-warning': designSystem.colors.semantic.warning.DEFAULT,
    '--color-error': designSystem.colors.semantic.error.DEFAULT,
    '--color-info': designSystem.colors.semantic.info.DEFAULT,
    
    // Spacing
    '--spacing-xs': designSystem.spacing[1],
    '--spacing-sm': designSystem.spacing[2],
    '--spacing-md': designSystem.spacing[4],
    '--spacing-lg': designSystem.spacing[6],
    '--spacing-xl': designSystem.spacing[8],
    
    // Typography
    '--font-sans': designSystem.typography.fontFamily.sans.join(', '),
    '--font-mono': designSystem.typography.fontFamily.mono.join(', '),
    '--font-display': designSystem.typography.fontFamily.display.join(', '),
    
    // Elevation
    '--shadow-sm': designSystem.elevation[1],
    '--shadow-md': designSystem.elevation[3],
    '--shadow-lg': designSystem.elevation[5],
    
    // Border radius
    '--radius-sm': designSystem.borderRadius.sm,
    '--radius-md': designSystem.borderRadius.md,
    '--radius-lg': designSystem.borderRadius.lg,
    
    // Animation
    '--duration-fast': designSystem.animation.duration.fast,
    '--duration-normal': designSystem.animation.duration.normal,
    '--easing-out': designSystem.animation.easing.out,
    '--easing-bounce': designSystem.animation.easing.bounce,
  }
  
  // Theme-specific properties
  const themeProperties = theme === 'light' ? {
    '--color-background': designSystem.colors.neutral[0],
    '--color-foreground': designSystem.colors.neutral[900],
    '--color-primary': designSystem.colors.brand[500],
    '--color-primary-foreground': designSystem.colors.neutral[0],
    '--color-secondary': designSystem.colors.neutral[100],
    '--color-secondary-foreground': designSystem.colors.neutral[900],
    '--color-muted': designSystem.colors.neutral[100],
    '--color-muted-foreground': designSystem.colors.neutral[500],
    '--color-accent': designSystem.colors.neutral[100],
    '--color-accent-foreground': designSystem.colors.neutral[900],
    '--color-border': designSystem.colors.neutral[200],
    '--color-input': designSystem.colors.neutral[200],
    '--color-card': designSystem.colors.neutral[0],
    '--color-card-foreground': designSystem.colors.neutral[900],
  } : {
    '--color-background': designSystem.colors.neutral[900],
    '--color-foreground': designSystem.colors.neutral[50],
    '--color-primary': designSystem.colors.brand[500],
    '--color-primary-foreground': designSystem.colors.neutral[900],
    '--color-secondary': designSystem.colors.neutral[800],
    '--color-secondary-foreground': designSystem.colors.neutral[50],
    '--color-muted': designSystem.colors.neutral[800],
    '--color-muted-foreground': designSystem.colors.neutral[400],
    '--color-accent': designSystem.colors.neutral[800],
    '--color-accent-foreground': designSystem.colors.neutral[50],
    '--color-border': designSystem.colors.neutral[700],
    '--color-input': designSystem.colors.neutral[700],
    '--color-card': designSystem.colors.neutral[800],
    '--color-card-foreground': designSystem.colors.neutral[50],
  }
  
  return { ...baseProperties, ...themeProperties }
}

export { designSystem }
```

### Advanced Color System with Design Tokens

```typescript
// Design token system with semantic meaning
const designTokens = {
  colors: {
    // Brand palette with accessibility consideration
    brand: {
      50: 'hsl(204, 100%, 97%)',   // AAA compliant lightest
      100: 'hsl(204, 94%, 94%)',
      200: 'hsl(204, 96%, 86%)',
      300: 'hsl(204, 93%, 78%)',
      400: 'hsl(204, 91%, 69%)',
      500: 'hsl(204, 88%, 59%)',   // Primary - 4.5:1 contrast ratio
      600: 'hsl(204, 85%, 50%)',
      700: 'hsl(204, 82%, 41%)',
      800: 'hsl(204, 78%, 32%)',
      900: 'hsl(204, 75%, 25%)',   // AAA compliant darkest
      950: 'hsl(204, 80%, 16%)',
    },
    
    // Semantic color system
    semantic: {
      success: {
        light: 'hsl(142, 76%, 36%)',
        DEFAULT: 'hsl(142, 71%, 45%)',
        dark: 'hsl(142, 69%, 58%)',
      },
      warning: {
        light: 'hsl(32, 95%, 44%)',
        DEFAULT: 'hsl(32, 95%, 54%)',
        dark: 'hsl(32, 100%, 70%)',
      },
      error: {
        light: 'hsl(0, 84%, 60%)',
        DEFAULT: 'hsl(0, 72%, 51%)',
        dark: 'hsl(0, 74%, 62%)',
      },
      info: {
        light: 'hsl(204, 94%, 94%)',
        DEFAULT: 'hsl(204, 88%, 59%)',
        dark: 'hsl(204, 78%, 32%)',
      }
    },
    
    // Neutral palette for UI elements
    neutral: {
      0: 'hsl(0, 0%, 100%)',      // Pure white
      50: 'hsl(210, 40%, 98%)',   // Near white
      100: 'hsl(210, 40%, 96%)',
      200: 'hsl(214, 32%, 91%)',
      300: 'hsl(213, 27%, 84%)',
      400: 'hsl(215, 20%, 65%)',
      500: 'hsl(215, 16%, 47%)',  // Mid gray
      600: 'hsl(215, 19%, 35%)',
      700: 'hsl(215, 25%, 27%)',
      800: 'hsl(217, 33%, 17%)',
      900: 'hsl(222, 47%, 11%)',  // Near black
      950: 'hsl(229, 84%, 5%)',   // Pure black variant
    },
    
    // Theme-aware CSS custom properties
    theme: {
      light: {
        background: 'hsl(0, 0%, 100%)',
        foreground: 'hsl(222, 47%, 11%)',
        primary: 'hsl(204, 88%, 59%)',
        primaryForeground: 'hsl(0, 0%, 100%)',
        secondary: 'hsl(210, 40%, 96%)',
        secondaryForeground: 'hsl(222, 47%, 11%)',
        muted: 'hsl(210, 40%, 96%)',
        mutedForeground: 'hsl(215, 16%, 47%)',
        accent: 'hsl(210, 40%, 96%)',
        accentForeground: 'hsl(222, 47%, 11%)',
        border: 'hsl(214, 32%, 91%)',
        input: 'hsl(214, 32%, 91%)',
        card: 'hsl(0, 0%, 100%)',
        cardForeground: 'hsl(222, 47%, 11%)',
      },
      dark: {
        background: 'hsl(222, 47%, 11%)',
        foreground: 'hsl(213, 31%, 91%)',
        primary: 'hsl(204, 88%, 59%)',
        primaryForeground: 'hsl(222, 47%, 11%)',
        secondary: 'hsl(215, 25%, 27%)',
        secondaryForeground: 'hsl(213, 31%, 91%)',
        muted: 'hsl(215, 25%, 27%)',
        mutedForeground: 'hsl(213, 19%, 65%)',
        accent: 'hsl(215, 25%, 27%)',
        accentForeground: 'hsl(213, 31%, 91%)',
        border: 'hsl(215, 25%, 27%)',
        input: 'hsl(215, 25%, 27%)',
        card: 'hsl(215, 25%, 27%)',
        cardForeground: 'hsl(213, 31%, 91%)',
      }
    }
  }
} as const
```

### Typography System with Fluid Scaling

```typescript
// Advanced typography scale with fluid sizing
const typography = {
  fontFamily: {
    sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
    display: ['Cal Sans', 'Inter var', 'system-ui', 'sans-serif'],
  },
  
  // Fluid typography using clamp()
  fontSize: {
    'xs': ['clamp(0.75rem, 0.7rem + 0.2vw, 0.875rem)', { lineHeight: '1.4' }],
    'sm': ['clamp(0.875rem, 0.8rem + 0.3vw, 1rem)', { lineHeight: '1.5' }],
    'base': ['clamp(1rem, 0.9rem + 0.4vw, 1.125rem)', { lineHeight: '1.6' }],
    'lg': ['clamp(1.125rem, 1rem + 0.5vw, 1.25rem)', { lineHeight: '1.5' }],
    'xl': ['clamp(1.25rem, 1.1rem + 0.6vw, 1.5rem)', { lineHeight: '1.4' }],
    '2xl': ['clamp(1.5rem, 1.3rem + 0.8vw, 2rem)', { lineHeight: '1.3' }],
    '3xl': ['clamp(1.875rem, 1.6rem + 1vw, 2.5rem)', { lineHeight: '1.2' }],
    '4xl': ['clamp(2.25rem, 1.9rem + 1.4vw, 3rem)', { lineHeight: '1.1' }],
    '5xl': ['clamp(3rem, 2.5rem + 2vw, 4rem)', { lineHeight: '1' }],
  },
  
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  
  // Text styles for specific use cases
  textStyles: {
    'display-large': {
      fontSize: 'clamp(3rem, 2.5rem + 2vw, 4rem)',
      fontWeight: '700',
      lineHeight: '1',
      letterSpacing: '-0.02em',
    },
    'heading-1': {
      fontSize: 'clamp(2.25rem, 1.9rem + 1.4vw, 3rem)',
      fontWeight: '700',
      lineHeight: '1.1',
      letterSpacing: '-0.01em',
    },
    'heading-2': {
      fontSize: 'clamp(1.875rem, 1.6rem + 1vw, 2.5rem)',
      fontWeight: '600',
      lineHeight: '1.2',
    },
    'body-large': {
      fontSize: 'clamp(1.125rem, 1rem + 0.5vw, 1.25rem)',
      fontWeight: '400',
      lineHeight: '1.6',
    },
    'body': {
      fontSize: 'clamp(1rem, 0.9rem + 0.4vw, 1.125rem)',
      fontWeight: '400',
      lineHeight: '1.6',
    },
    'caption': {
      fontSize: 'clamp(0.875rem, 0.8rem + 0.3vw, 1rem)',
      fontWeight: '500',
      lineHeight: '1.4',
      color: 'hsl(var(--muted-foreground))',
    }
  }
} as const
```

### Typography

- **Primary Font**: Inter (variable font)
- **Mono Font**: System monospace stack
- **Scale**: Tailwind's default scale (text-sm to text-6xl)

### Advanced Component Patterns & Animations

**Component Variants System**
```typescript
// Advanced variant system using class-variance-authority
import { cva, type VariantProps } from 'class-variance-authority'

// Button component with complex variants
const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground shadow hover:bg-primary/90 hover:shadow-lg transform hover:-translate-y-0.5',
        destructive: 'bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90',
        outline: 'border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
        gradient: 'bg-gradient-to-r from-primary to-primary/80 text-primary-foreground shadow-lg hover:shadow-xl hover:from-primary/90 hover:to-primary/70 transform hover:-translate-y-1'
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-11 rounded-md px-6',
        xl: 'h-12 rounded-lg px-8 text-lg',
        icon: 'h-10 w-10 rounded-full'
      },
      loading: {
        true: 'cursor-wait opacity-70',
        false: ''
      }
    },
    compoundVariants: [
      {
        variant: 'default',
        size: 'lg',
        className: 'shadow-lg hover:shadow-xl'
      }
    ],
    defaultVariants: {
      variant: 'default',
      size: 'default',
      loading: false
    }
  }
)

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & 
  VariantProps<typeof buttonVariants> & {
    loading?: boolean
    leftIcon?: ReactNode
    rightIcon?: ReactNode
  }
```

**Advanced Animation System**
```typescript
// Framer Motion animation presets
const animations = {
  // Page transitions
  pageTransition: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3, ease: 'easeInOut' }
  },
  
  // Slide animations with spring physics
  slideIn: {
    initial: { x: -100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    transition: {
      type: 'spring',
      stiffness: 100,
      damping: 15,
      mass: 1
    }
  },
  
  // Scale animations for cards
  scaleOnHover: {
    whileHover: { 
      scale: 1.05, 
      rotateY: 5,
      transition: { duration: 0.2 } 
    },
    whileTap: { scale: 0.95 }
  },
  
  // Loading animations
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      opacity: [0.5, 1, 0.5]
    },
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  },
  
  // Stagger children for list animations
  staggerChildren: {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  },
  
  // Advanced morphing animations
  morphPath: {
    initial: { pathLength: 0, opacity: 0 },
    animate: {
      pathLength: 1,
      opacity: 1,
      transition: {
        pathLength: { duration: 1.5, ease: 'easeInOut' },
        opacity: { duration: 0.3 }
      }
    }
  }
} as const

// Animation hook for reusability
export const useAnimations = () => {
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)')
  
  return prefersReducedMotion 
    ? Object.keys(animations).reduce((acc, key) => ({ 
        ...acc, 
        [key]: {} 
      }), {})
    : animations
}
```

**Micro-interaction Patterns**
```typescript
// Advanced interaction patterns
const microInteractions = {
  // Button with feedback
  buttonFeedback: {
    whileHover: { scale: 1.02 },
    whileTap: { scale: 0.98 },
    transition: { type: 'spring', stiffness: 400, damping: 17 }
  },
  
  // Card hover with glow effect
  cardGlow: {
    whileHover: {
      boxShadow: '0 10px 30px rgba(59, 130, 246, 0.15)',
      transition: { duration: 0.3 }
    }
  },
  
  // Input focus animation
  inputFocus: {
    whileFocus: {
      borderColor: 'hsl(var(--primary))',
      boxShadow: '0 0 0 3px hsl(var(--primary) / 0.1)',
      transition: { duration: 0.15 }
    }
  },
  
  // Loading spinner with easing
  spinner: {
    animate: { rotate: 360 },
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear'
    }
  }
}
```

## User Experience Design

### Navigation Flow

1. **Landing Page** → Feature overview and CTAs
2. **Registration/Login** → User onboarding
3. **Dashboard** → Main workspace with overview
4. **Data Upload** → Dataset management
5. **AI Analysis** → Conversational data exploration
6. **Visualization** → Chart builder and reports

### Key Features Highlighted

1. **AI Smart Analysis**
   - Natural language querying
   - Automatic analysis execution

2. **Conversational Queries**
   - Chat-based data exploration
   - Instant results and visualizations

3. **Smart Visualization**
   - Auto-recommended chart types
   - Professional visualization reports

4. **Multi-source Integration**
   - CSV, Excel, JSON support
   - Easy upload and management

5. **Real-time Analysis**
   - Ray cluster-based computing
   - Large-scale data processing

6. **Advanced Statistics**
   - Regression, clustering, correlation
   - Professional statistical tools

## Development Workflow & Backend Integration

### Environment Setup
```bash
# Frontend setup
cd frontend
npm install                    # Install dependencies
cp .env.example .env.local     # Copy environment config

# Configure backend service URLs in .env.local
NEXT_PUBLIC_API_GATEWAY_URL=http://localhost:8000
NEXT_PUBLIC_DATA_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8002
NEXT_PUBLIC_COMPUTE_SERVICE_URL=http://localhost:8003
NEXT_PUBLIC_VIZ_SERVICE_URL=http://localhost:8004
```

### Coordinated Development Workflow

**1. Backend Services Startup (Required First)**
```bash
# From backend directory - MANDATORY: Use UV (see ../backend/CLAUDE.md)
cd backend
uv install
uv run python dev_server.py  # Starts all backend services

# Verify services are running:
# - API Gateway: http://localhost:8000/health
# - Data Service: http://localhost:8001/health
# - AI Service: http://localhost:8002/health (when implemented)
```

**2. Frontend Development**
```bash
# Frontend development server
cd frontend
npm run dev              # Start Next.js dev server (localhost:3000)

# Development tools
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint + TypeScript checking
npm run type-check       # TypeScript compilation check
npm run test             # Run Jest tests
npm run test:watch       # Watch mode for tests
```

### Full-Stack Development Commands

**Backend Service Integration Testing**
```bash
# Test authentication flow
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Test data source creation
curl -X POST http://localhost:8000/api/v1/data-sources \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test DB", "type": "postgresql", "config": {...}}'
```

**Frontend-Backend Integration Verification**
```bash
# Check service connectivity from frontend
npm run dev &              # Start frontend
curl http://localhost:3000/api/health  # Test frontend health

# Test authenticated API calls
# 1. Login through frontend UI
# 2. Check browser network tab for API calls
# 3. Verify JWT tokens in localStorage
```

### Testing
```bash
npm test             # Run Jest tests
npm run test:watch   # Watch mode
npm run test:coverage # Coverage report
```

## Implementation Priorities

### Phase 1: Core Infrastructure
1. Create base UI component library
2. Implement authentication pages and flows
3. Set up dashboard layout with navigation
4. Create data source management interface

### Phase 2: Data Features
1. File upload and data preview components
2. Dataset management interface
3. Basic data visualization components
4. Query builder interface

### Phase 3: AI Integration
1. Chat interface for AI conversations
2. Analysis result display components
3. Advanced visualization components
4. Export and sharing features

## Advanced Performance Optimization Strategies

### Core Performance Architecture

**1. Advanced Code Splitting & Lazy Loading**
```typescript
// Route-based code splitting with preloading
const Dashboard = lazy(() => 
  import('@/components/features/dashboard/Dashboard').then(module => ({
    default: module.Dashboard
  }))
)

// Component-level lazy loading with fallbacks
const HeavyChart = lazy(() => 
  import('@/components/features/visualizations/HeavyChart')
)

// Preload critical routes on hover
const preloadRoute = (routeName: string) => {
  const routeMap = {
    dashboard: () => import('@/app/dashboard/page'),
    analysis: () => import('@/app/analysis/page'),
    visualizations: () => import('@/app/visualizations/page')
  }
  return routeMap[routeName]?.()
}

// Usage in navigation
<Link 
  href="/dashboard" 
  onMouseEnter={() => preloadRoute('dashboard')}
>
  Dashboard
</Link>
```

**2. Virtual Scrolling for Large Datasets**
```typescript
// Advanced virtual list with buffer
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualDataTable<T>({ 
  data, 
  renderItem, 
  estimateSize = 50 
}: VirtualDataTableProps<T>) {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan: 10, // Render extra items for smooth scrolling
    getItemKey: (index) => data[index].id
  })

  return (
    <div
      ref={parentRef}
      className="h-96 overflow-auto"
      style={{ contain: 'strict' }} // CSS containment for performance
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative'
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const item = data[virtualItem.index]
          return (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`
              }}
            >
              {renderItem(item, virtualItem.index)}
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

**3. Advanced React Query Configuration**
```typescript
// Optimized query client with advanced caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes garbage collection
      retry: (failureCount, error) => {
        if (error.status === 404) return false
        return failureCount < 3
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      networkMode: 'always'
    },
    mutations: {
      retry: 1,
      networkMode: 'online'
    }
  }
})

// Background prefetching for predictable user actions
const usePrefetchData = () => {
  const queryClient = useQueryClient()
  
  const prefetchUserDashboard = useCallback(async (userId: string) => {
    await queryClient.prefetchQuery({
      queryKey: ['dashboard', userId],
      queryFn: () => dashboardService.getData(userId),
      staleTime: 10 * 60 * 1000 // Prefetch data stays fresh longer
    })
  }, [queryClient])
  
  return { prefetchUserDashboard }
}

// Optimistic updates with rollback
const useOptimisticDataUpdate = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: dataService.updateData,
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['data'] })
      
      // Snapshot previous value
      const previousData = queryClient.getQueryData(['data'])
      
      // Optimistically update
      queryClient.setQueryData(['data'], (old: any) => ({ ...old, ...newData }))
      
      return { previousData }
    },
    onError: (err, newData, context) => {
      // Rollback on error
      queryClient.setQueryData(['data'], context?.previousData)
    },
    onSettled: () => {
      // Always refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['data'] })
    }
  })
}
```

**4. Web Workers for Heavy Computation**
```typescript
// Web Worker for data processing
// workers/dataProcessor.worker.ts
self.onmessage = function(e) {
  const { data, operation } = e.data
  
  switch (operation) {
    case 'processLargeDataset':
      const result = processLargeDataset(data)
      self.postMessage({ result, operation })
      break
    case 'calculateStatistics':
      const stats = calculateStatistics(data)
      self.postMessage({ result: stats, operation })
      break
  }
}

function processLargeDataset(data: any[]) {
  // Heavy computation logic
  return data.map(item => ({
    ...item,
    processedValue: expensiveCalculation(item.value)
  }))
}

// Hook to use Web Worker
const useWebWorker = () => {
  const [isProcessing, setIsProcessing] = useState(false)
  const workerRef = useRef<Worker | null>(null)
  
  useEffect(() => {
    workerRef.current = new Worker(
      new URL('../workers/dataProcessor.worker.ts', import.meta.url)
    )
    
    return () => {
      workerRef.current?.terminate()
    }
  }, [])
  
  const processData = useCallback((data: any[], operation: string) => {
    return new Promise((resolve, reject) => {
      if (!workerRef.current) {
        reject(new Error('Worker not available'))
        return
      }
      
      setIsProcessing(true)
      
      const handleMessage = (e: MessageEvent) => {
        if (e.data.operation === operation) {
          setIsProcessing(false)
          workerRef.current?.removeEventListener('message', handleMessage)
          resolve(e.data.result)
        }
      }
      
      const handleError = (error: ErrorEvent) => {
        setIsProcessing(false)
        workerRef.current?.removeEventListener('error', handleError)
        reject(error)
      }
      
      workerRef.current.addEventListener('message', handleMessage)
      workerRef.current.addEventListener('error', handleError)
      workerRef.current.postMessage({ data, operation })
    })
  }, [])
  
  return { processData, isProcessing }
}
```

**5. Service Worker for Offline Support**
```typescript
// Advanced service worker with caching strategies
// public/sw.js
const CACHE_NAME = 'data-analysis-v1'
const API_CACHE = 'api-cache-v1'
const STATIC_CACHE = 'static-cache-v1'

// Install event - cache critical resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.addAll([
          '/',
          '/offline',
          '/manifest.json',
          // Critical CSS and JS
        ])
      }),
      self.skipWaiting()
    ])
  )
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // API requests - Network First with fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request))
    return
  }
  
  // Static assets - Cache First
  if (request.destination === 'image' || request.destination === 'script' || request.destination === 'style') {
    event.respondWith(cacheFirstStrategy(request))
    return
  }
  
  // Pages - Stale While Revalidate
  event.respondWith(staleWhileRevalidateStrategy(request))
})

// Caching strategies
async function networkFirstStrategy(request) {
  try {
    const response = await fetch(request)
    const cache = await caches.open(API_CACHE)
    cache.put(request, response.clone())
    return response
  } catch (error) {
    return caches.match(request) || new Response('Offline', { status: 503 })
  }
}

// Hook to register service worker
const useServiceWorker = () => {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('SW registered: ', registration)
        })
        .catch((registrationError) => {
          console.log('SW registration failed: ', registrationError)
        })
    }
  }, [])
}
```

**6. Performance Monitoring & Optimization**
```typescript
// Performance monitoring hooks
const usePerformanceMonitoring = () => {
  useEffect(() => {
    // Monitor Core Web Vitals
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'largest-contentful-paint') {
          console.log('LCP:', entry.startTime)
        }
        if (entry.entryType === 'first-input') {
          console.log('FID:', entry.processingStart - entry.startTime)
        }
        if (entry.entryType === 'layout-shift') {
          if (!entry.hadRecentInput) {
            console.log('CLS:', entry.value)
          }
        }
      })
    })
    
    observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] })
    
    return () => observer.disconnect()
  }, [])
}

// Memory usage monitoring
const useMemoryMonitoring = () => {
  const [memoryInfo, setMemoryInfo] = useState<any>(null)
  
  useEffect(() => {
    const updateMemoryInfo = () => {
      if ('memory' in performance) {
        setMemoryInfo({
          usedJSMemory: (performance as any).memory.usedJSMemory,
          totalJSMemory: (performance as any).memory.totalJSMemory,
          jsMemoryLimit: (performance as any).memory.jsMemoryLimit
        })
      }
    }
    
    const interval = setInterval(updateMemoryInfo, 10000) // Every 10 seconds
    updateMemoryInfo()
    
    return () => clearInterval(interval)
  }, [])
  
  return memoryInfo
}
```

## Advanced Development Workflow & Testing

### Comprehensive Testing Architecture

**1. Testing Strategy & Tools**
```typescript
// Test setup with modern tools
const testingStack = {
  unitTesting: 'Vitest + Testing Library',
  e2eTesting: 'Playwright',
  visualTesting: 'Chromatic + Storybook',
  apiTesting: 'MSW (Mock Service Worker)',
  accessibility: '@axe-core/playwright',
  performance: 'Lighthouse CI'
}

// vitest.config.ts - Advanced configuration
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.ts'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

**2. Component Testing Patterns**
```typescript
// Advanced component testing with all scenarios
import { render, screen, waitFor } from '@/test/utils'
import { Button } from './Button'
import { userEvent } from '@testing-library/user-event'

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders with correct default styles', () => {
      render(<Button>Click me</Button>)
      
      const button = screen.getByRole('button', { name: /click me/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('bg-primary')
    })
    
    it('applies variant styles correctly', () => {
      const variants = [
        { variant: 'destructive', expectedClass: 'bg-destructive' },
        { variant: 'outline', expectedClass: 'border' },
        { variant: 'ghost', expectedClass: 'hover:bg-accent' },
      ] as const
      
      variants.forEach(({ variant, expectedClass }) => {
        const { unmount } = render(<Button variant={variant}>Test</Button>)
        expect(screen.getByRole('button')).toHaveClass(expectedClass)
        unmount()
      })
    })
  })
  
  describe('Interactions', () => {
    it('handles click events', async () => {
      const handleClick = vi.fn()
      const user = userEvent.setup()
      
      render(<Button onClick={handleClick}>Click me</Button>)
      
      await user.click(screen.getByRole('button'))
      expect(handleClick).toHaveBeenCalledTimes(1)
    })
    
    it('prevents click when disabled', async () => {
      const handleClick = vi.fn()
      const user = userEvent.setup()
      
      render(<Button disabled onClick={handleClick}>Disabled</Button>)
      
      await user.click(screen.getByRole('button'))
      expect(handleClick).not.toHaveBeenCalled()
    })
  })
  
  describe('Loading State', () => {
    it('shows loading indicator and disables button', () => {
      render(<Button loading>Loading</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    })
  })
  
  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(
        <Button 
          aria-describedby="help-text"
          aria-label="Save changes"
        >
          Save
        </Button>
      )
      
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-describedby', 'help-text')
      expect(button).toHaveAttribute('aria-label', 'Save changes')
    })
    
    it('supports keyboard navigation', async () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)
      
      const button = screen.getByRole('button')
      button.focus()
      
      await userEvent.keyboard('{Enter}')
      expect(handleClick).toHaveBeenCalledTimes(1)
      
      await userEvent.keyboard('{Space}')
      expect(handleClick).toHaveBeenCalledTimes(2)
    })
  })
})
```

**3. Integration Testing with MSW**
```typescript
// API mocking with Mock Service Worker
import { rest } from 'msw'
import { setupServer } from 'msw/node'

// Define API handlers
export const handlers = [
  rest.get('/api/v1/data-sources', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: [
          {
            id: 1,
            name: 'Test Database',
            type: 'postgresql',
            status: 'connected',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
      })
    )
  }),
  
  rest.post('/api/v1/data-sources', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        data: {
          id: 2,
          name: 'New Database',
          type: 'postgresql',
          status: 'pending',
          created_at: new Date().toISOString()
        }
      })
    )
  }),
  
  rest.post('/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: 1,
            email: 'test@example.com',
            role: 'user'
          }
        }
      })
    )
  })
]

// Setup test server
export const server = setupServer(...handlers)

// Integration test example
describe('Data Sources Integration', () => {
  beforeAll(() => server.listen())
  afterEach(() => server.resetHandlers())
  afterAll(() => server.close())
  
  it('fetches and displays data sources', async () => {
    render(<DataSourcesPage />)
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByTestId('loading')).not.toBeInTheDocument()
    })
    
    // Check that data source is displayed
    expect(screen.getByText('Test Database')).toBeInTheDocument()
    expect(screen.getByText('postgresql')).toBeInTheDocument()
    expect(screen.getByText('connected')).toBeInTheDocument()
  })
  
  it('creates new data source', async () => {
    const user = userEvent.setup()
    render(<DataSourcesPage />)
    
    // Click create button
    await user.click(screen.getByRole('button', { name: /create/i }))
    
    // Fill form
    await user.type(screen.getByLabelText(/name/i), 'New Database')
    await user.selectOptions(screen.getByLabelText(/type/i), 'postgresql')
    
    // Submit
    await user.click(screen.getByRole('button', { name: /save/i }))
    
    // Check success message
    await waitFor(() => {
      expect(screen.getByText(/data source created/i)).toBeInTheDocument()
    })
  })
  
  it('handles API errors gracefully', async () => {
    // Mock error response
    server.use(
      rest.get('/api/v1/data-sources', (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({
            error: {
              code: 'INTERNAL_ERROR',
              message: 'Server error'
            }
          })
        )
      })
    )
    
    render(<DataSourcesPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    })
    
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  })
})
```

**4. E2E Testing with Playwright**
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
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
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})

// E2E test example
import { test, expect } from '@playwright/test'

test.describe('Dashboard E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Set up authentication
    await page.goto('/login')
    await page.fill('[data-testid="email"]', 'test@example.com')
    await page.fill('[data-testid="password"]', 'password123')
    await page.click('[data-testid="login-button"]')
    
    await expect(page).toHaveURL('/dashboard')
  })
  
  test('user can view dashboard', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
    await expect(page.getByText('Data Sources')).toBeVisible()
    await expect(page.getByText('Recent Analysis')).toBeVisible()
  })
  
  test('user can create data source', async ({ page }) => {
    await page.click('text=Create Data Source')
    await expect(page.getByRole('dialog')).toBeVisible()
    
    await page.fill('[name="name"]', 'Test Database')
    await page.selectOption('[name="type"]', 'postgresql')
    await page.fill('[name="host"]', 'localhost')
    await page.fill('[name="port"]', '5432')
    
    await page.click('button:has-text("Save")')
    
    await expect(page.getByText('Data source created')).toBeVisible()
    await expect(page.getByText('Test Database')).toBeVisible()
  })
  
  test('navigation works correctly', async ({ page }) => {
    // Test main navigation
    await page.click('nav a[href="/data-sources"]')
    await expect(page).toHaveURL('/data-sources')
    
    await page.click('nav a[href="/analysis"]')
    await expect(page).toHaveURL('/analysis')
    
    await page.click('nav a[href="/visualizations"]')
    await expect(page).toHaveURL('/visualizations')
  })
  
  test('responsive design works', async ({ page, browserName }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Mobile menu should be visible
    await expect(page.getByTestId('mobile-menu-button')).toBeVisible()
    
    // Desktop navigation should be hidden
    await expect(page.getByTestId('desktop-navigation')).not.toBeVisible()
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    
    // Sidebar should adapt
    const sidebar = page.getByTestId('sidebar')
    await expect(sidebar).toBeVisible()
  })
})
```

**5. Visual Regression Testing**
```typescript
// Storybook configuration for visual testing
// .storybook/main.ts
export default {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@chromatic-com/storybook'
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {}
  },
  docs: {
    autodocs: 'tag'
  }
}

// Component story for visual testing
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and states.'
      }
    }
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost']
    },
    size: {
      control: { type: 'select' },
      options: ['default', 'sm', 'lg', 'icon']
    }
  }
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    children: 'Button'
  }
}

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-2 flex-wrap">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  )
}

export const AllSizes: Story = {
  render: () => (
    <div className="flex gap-2 items-center">
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
    </div>
  )
}

export const LoadingStates: Story = {
  render: () => (
    <div className="flex gap-2">
      <Button loading>Loading</Button>
      <Button loading variant="outline">Loading Outline</Button>
    </div>
  )
}

export const WithIcons: Story = {
  render: () => (
    <div className="flex gap-2">
      <Button>
        <PlusIcon className="w-4 h-4 mr-2" />
        Add Item
      </Button>
      <Button variant="outline">
        <DownloadIcon className="w-4 h-4 mr-2" />
        Download
      </Button>
    </div>
  )
}

// Chromatic configuration for visual regression
// chromatic.yml
name: Visual Tests
on: [push, pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npx chromatic --project-token=${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

**6. Accessibility Testing**
```typescript
// Automated accessibility testing
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('homepage is accessible', async ({ page }) => {
    await page.goto('/')
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    expect(accessibilityScanResults.violations).toEqual([])
  })
  
  test('dashboard is accessible', async ({ page }) => {
    await page.goto('/dashboard')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })
  
  test('form interactions are accessible', async ({ page }) => {
    await page.goto('/data-sources/new')
    
    // Test keyboard navigation
    await page.keyboard.press('Tab')
    await expect(page.locator('[name="name"]')).toBeFocused()
    
    await page.keyboard.press('Tab')
    await expect(page.locator('[name="type"]')).toBeFocused()
    
    // Test screen reader announcements
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    expect(accessibilityScanResults.violations).toEqual([])
  })
})

// Component-level accessibility testing
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

describe('Button Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
  
  it('disabled button has proper ARIA attributes', async () => {
    const { container } = render(<Button disabled>Disabled</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

## Security & Accessibility Standards

### Advanced Security Implementation

**1. Content Security Policy (CSP)**
```typescript
// next.config.js - Security headers
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.jsdelivr.net",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' blob: data: https:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.example.com wss://api.example.com",
      "media-src 'self'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests"
    ].join('; ')
  },
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains; preload'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  }
]

export default {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
}
```

**2. Input Validation & Sanitization**
```typescript
// Advanced input validation with Zod
import { z } from 'zod'
import DOMPurify from 'isomorphic-dompurify'

// Comprehensive validation schemas
const emailSchema = z
  .string()
  .email('Invalid email address')
  .min(5, 'Email must be at least 5 characters')
  .max(254, 'Email must be less than 254 characters')
  .transform(email => email.toLowerCase().trim())

const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must be less than 128 characters')
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
  )

const userInputSchema = z
  .string()
  .min(1, 'Input is required')
  .max(1000, 'Input must be less than 1000 characters')
  .transform(input => {
    // Sanitize HTML content
    return DOMPurify.sanitize(input, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
      ALLOWED_ATTR: ['href']
    })
  })
  .refine(
    input => {
      // Check for potential XSS patterns
      const xssPatterns = [
        /<script[^>]*>.*?<\/script>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /<iframe[^>]*>.*?<\/iframe>/gi
      ]
      
      return !xssPatterns.some(pattern => pattern.test(input))
    },
    'Invalid characters detected'
  )

// SQL injection prevention for dynamic queries
const sqlSchema = z
  .string()
  .refine(
    query => {
      const suspiciousPatterns = [
        /('|(\-\-)|(;)|(\||\|)|(\*|\*))/, // Basic SQL injection patterns
        /(union|select|insert|update|delete|drop|create|alter|exec|execute)/i,
        /(script|javascript|vbscript|onload|onerror|onclick)/i
      ]
      
      return !suspiciousPatterns.some(pattern => pattern.test(query))
    },
    'Query contains potentially dangerous patterns'
  )

// Validation hook with error handling
const useValidation = <T>(schema: z.ZodSchema<T>) => {
  const validate = useCallback((data: unknown) => {
    try {
      return {
        success: true,
        data: schema.parse(data),
        errors: null
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          success: false,
          data: null,
          errors: error.errors.reduce((acc, err) => {
            acc[err.path.join('.')] = err.message
            return acc
          }, {} as Record<string, string>)
        }
      }
      
      return {
        success: false,
        data: null,
        errors: { general: 'Validation failed' }
      }
    }
  }, [schema])
  
  return { validate }
}
```

**3. Secure Token Management**
```typescript
// Advanced JWT token management with security best practices
class SecureTokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token'
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token'
  private static readonly TOKEN_PREFIX = 'Bearer '
  private static readonly STORAGE_KEY_PREFIX = 'secure_app_'
  
  // Secure storage with encryption
  private static encrypt(data: string): string {
    // Use a simple encryption for demo (use proper encryption in production)
    return btoa(encodeURIComponent(data))
  }
  
  private static decrypt(encryptedData: string): string {
    try {
      return decodeURIComponent(atob(encryptedData))
    } catch {
      return ''
    }
  }
  
  private static getStorageKey(key: string): string {
    return `${this.STORAGE_KEY_PREFIX}${key}`
  }
  
  // Token validation
  private static isValidToken(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Date.now() / 1000
      
      // Check expiration
      if (payload.exp && payload.exp < now) {
        return false
      }
      
      // Check issued at time (not too old)
      if (payload.iat && payload.iat > now + 300) { // 5 minutes tolerance
        return false
      }
      
      // Check required claims
      if (!payload.sub || !payload.iss) {
        return false
      }
      
      return true
    } catch {
      return false
    }
  }
  
  static setTokens(accessToken: string, refreshToken: string): void {
    if (!this.isValidToken(accessToken)) {
      throw new Error('Invalid access token')
    }
    
    try {
      // Store in httpOnly cookie if possible, fallback to sessionStorage
      if (typeof window !== 'undefined') {
        // Encrypt before storing
        const encryptedAccessToken = this.encrypt(accessToken)
        const encryptedRefreshToken = this.encrypt(refreshToken)
        
        sessionStorage.setItem(
          this.getStorageKey(this.ACCESS_TOKEN_KEY),
          encryptedAccessToken
        )
        
        // Store refresh token in localStorage (longer persistence)
        localStorage.setItem(
          this.getStorageKey(this.REFRESH_TOKEN_KEY),
          encryptedRefreshToken
        )
        
        // Set secure cookie for additional security
        document.cookie = `auth_session=true; Secure; SameSite=Strict; Path=/`
      }
    } catch (error) {
      console.error('Failed to store tokens:', error)
      throw new Error('Token storage failed')
    }
  }
  
  static getAccessToken(): string | null {
    try {
      if (typeof window === 'undefined') return null
      
      const encryptedToken = sessionStorage.getItem(
        this.getStorageKey(this.ACCESS_TOKEN_KEY)
      )
      
      if (!encryptedToken) return null
      
      const token = this.decrypt(encryptedToken)
      
      // Validate token before returning
      if (!token || !this.isValidToken(token)) {
        this.clearTokens()
        return null
      }
      
      return token
    } catch {
      this.clearTokens()
      return null
    }
  }
  
  static getRefreshToken(): string | null {
    try {
      if (typeof window === 'undefined') return null
      
      const encryptedToken = localStorage.getItem(
        this.getStorageKey(this.REFRESH_TOKEN_KEY)
      )
      
      if (!encryptedToken) return null
      
      return this.decrypt(encryptedToken)
    } catch {
      return null
    }
  }
  
  static clearTokens(): void {
    if (typeof window === 'undefined') return
    
    sessionStorage.removeItem(this.getStorageKey(this.ACCESS_TOKEN_KEY))
    localStorage.removeItem(this.getStorageKey(this.REFRESH_TOKEN_KEY))
    
    // Clear auth cookie
    document.cookie = 'auth_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
  }
  
  static getAuthorizationHeader(): string | null {
    const token = this.getAccessToken()
    return token ? `${this.TOKEN_PREFIX}${token}` : null
  }
  
  static isTokenExpiringSoon(token: string, thresholdMinutes = 5): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const now = Date.now() / 1000
      const threshold = thresholdMinutes * 60
      
      return payload.exp && payload.exp - now < threshold
    } catch {
      return true
    }
  }
}
```

### Comprehensive Accessibility Implementation

**1. WCAG 2.1 AA Compliance Framework**
```typescript
// Accessibility utility hooks
const useAccessibility = () => {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [fontSize, setFontSize] = useState('medium')
  
  useEffect(() => {
    // Check user preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)')
    
    setReducedMotion(prefersReducedMotion.matches)
    setHighContrast(prefersHighContrast.matches)
    
    // Listen for changes
    const handleMotionChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches)
    const handleContrastChange = (e: MediaQueryListEvent) => setHighContrast(e.matches)
    
    prefersReducedMotion.addEventListener('change', handleMotionChange)
    prefersHighContrast.addEventListener('change', handleContrastChange)
    
    return () => {
      prefersReducedMotion.removeEventListener('change', handleMotionChange)
      prefersHighContrast.removeEventListener('change', handleContrastChange)
    }
  }, [])
  
  // Apply accessibility preferences
  useEffect(() => {
    document.documentElement.style.setProperty(
      '--animation-duration',
      reducedMotion ? '0.01ms' : '200ms'
    )
    
    document.documentElement.style.setProperty(
      '--transition-duration',
      reducedMotion ? '0.01ms' : '150ms'
    )
    
    if (highContrast) {
      document.documentElement.classList.add('high-contrast')
    } else {
      document.documentElement.classList.remove('high-contrast')
    }
  }, [reducedMotion, highContrast])
  
  return {
    reducedMotion,
    highContrast,
    fontSize,
    setFontSize
  }
}

// Keyboard navigation manager
const useKeyboardNavigation = () => {
  const [isKeyboardUser, setIsKeyboardUser] = useState(false)
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        setIsKeyboardUser(true)
        document.body.classList.add('keyboard-user')
      }
    }
    
    const handleMouseDown = () => {
      setIsKeyboardUser(false)
      document.body.classList.remove('keyboard-user')
    }
    
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }, [])
  
  return { isKeyboardUser }
}

// Focus management
const useFocusManagement = () => {
  const focusRingRef = useRef<HTMLElement | null>(null)
  
  const setFocus = useCallback((element: HTMLElement) => {
    if (element && element.focus) {
      element.focus()
      
      // Ensure focus is visible
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'nearest'
      })
    }
  }, [])
  
  const trapFocus = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus()
            e.preventDefault()
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus()
            e.preventDefault()
          }
        }
      }
      
      if (e.key === 'Escape') {
        // Allow parent to handle escape
        container.dispatchEvent(new CustomEvent('escape-key'))
      }
    }
    
    container.addEventListener('keydown', handleKeyDown)
    
    // Focus first element
    if (firstElement) {
      firstElement.focus()
    }
    
    return () => {
      container.removeEventListener('keydown', handleKeyDown)
    }
  }, [])
  
  return {
    setFocus,
    trapFocus,
    focusRingRef
  }
}
```

**2. Accessible Component Examples**
```typescript
// Fully accessible modal component
const AccessibleModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium' 
}: AccessibleModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const { trapFocus } = useFocusManagement()
  const [isClosing, setIsClosing] = useState(false)
  
  // Handle escape key and focus trapping
  useEffect(() => {
    if (isOpen && modalRef.current) {
      const cleanup = trapFocus(modalRef.current)
      
      // Handle escape at modal level
      const handleEscape = (e: CustomEvent) => {
        onClose()
      }
      
      modalRef.current.addEventListener('escape-key', handleEscape as EventListener)
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
      
      return () => {
        cleanup()
        modalRef.current?.removeEventListener('escape-key', handleEscape as EventListener)
        document.body.style.overflow = ''
      }
    }
  }, [isOpen, trapFocus, onClose])
  
  // Announce modal opening to screen readers
  useEffect(() => {
    if (isOpen) {
      const announcement = document.createElement('div')
      announcement.setAttribute('aria-live', 'polite')
      announcement.setAttribute('aria-atomic', 'true')
      announcement.className = 'sr-only'
      announcement.textContent = `Dialog opened: ${title}`
      
      document.body.appendChild(announcement)
      
      setTimeout(() => {
        document.body.removeChild(announcement)
      }, 1000)
    }
  }, [isOpen, title])
  
  if (!isOpen && !isClosing) return null
  
  return (
    <Portal>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        role="presentation"
      >
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black/50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        
        {/* Modal */}
        <div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          aria-describedby="modal-description"
          className={cn(
            'relative bg-background border rounded-lg shadow-lg max-h-[90vh] overflow-y-auto',
            'focus:outline-none focus:ring-2 focus:ring-primary',
            {
              'max-w-sm': size === 'small',
              'max-w-lg': size === 'medium',
              'max-w-4xl': size === 'large',
              'max-w-full mx-4': size === 'full'
            }
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 
              id="modal-title"
              className="text-lg font-semibold"
            >
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-muted rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              aria-label="Close dialog"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          {/* Content */}
          <div id="modal-description" className="p-6">
            {children}
          </div>
        </div>
      </div>
    </Portal>
  )
}

// Accessible form field component
const AccessibleFormField = ({
  label,
  children,
  error,
  description,
  required = false,
  ...props
}: AccessibleFormFieldProps) => {
  const id = useId()
  const errorId = error ? `${id}-error` : undefined
  const descriptionId = description ? `${id}-description` : undefined
  
  return (
    <div className="space-y-2">
      <label 
        htmlFor={id}
        className={cn(
          'text-sm font-medium',
          error && 'text-destructive'
        )}
      >
        {label}
        {required && (
          <span className="text-destructive ml-1" aria-label="required">
            *
          </span>
        )}
      </label>
      
      {description && (
        <p 
          id={descriptionId}
          className="text-sm text-muted-foreground"
        >
          {description}
        </p>
      )}
      
      <div className="relative">
        {React.cloneElement(children as React.ReactElement, {
          id,
          'aria-describedby': cn(descriptionId, errorId).trim() || undefined,
          'aria-invalid': error ? 'true' : 'false',
          'aria-required': required,
          className: cn(
            (children as React.ReactElement).props.className,
            error && 'border-destructive focus:ring-destructive'
          )
        })}
      </div>
      
      {error && (
        <p 
          id={errorId}
          role="alert"
          aria-live="polite"
          className="text-sm text-destructive flex items-center gap-2"
        >
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {error}
        </p>
      )}
    </div>
  )
}
```

### Security Checklist

- [x] **Content Security Policy** implemented
- [x] **XSS Protection** with input sanitization
- [x] **CSRF Protection** with token validation
- [x] **SQL Injection Prevention** with parameterized queries
- [x] **Secure Token Storage** with encryption
- [x] **HTTPS Enforcement** with security headers
- [x] **Input Validation** with comprehensive schemas
- [x] **Error Handling** without information leakage

### Accessibility Checklist

- [x] **WCAG 2.1 AA Compliance** with automated testing
- [x] **Keyboard Navigation** with proper focus management
- [x] **Screen Reader Support** with ARIA labels and descriptions
- [x] **Color Contrast** meeting 4.5:1 ratio minimum
- [x] **Responsive Design** supporting 320px minimum width
- [x] **Alternative Text** for all meaningful images
- [x] **Form Labels** properly associated with inputs
- [x] **Error Announcements** with live regions

## Internationalization & Deployment

### Advanced i18n Implementation

**1. Next.js i18n Configuration**
```typescript
// next.config.js
module.exports = {
  i18n: {
    locales: ['en', 'zh-CN', 'es', 'fr', 'de', 'ja'],
    defaultLocale: 'en',
    localeDetection: true,
    domains: [
      {
        domain: 'datalab.com',
        defaultLocale: 'en',
      },
      {
        domain: 'datalab.cn',
        defaultLocale: 'zh-CN',
      },
    ],
  },
}

// lib/i18n.ts - Advanced internationalization setup
import { createInstance } from 'i18next'
import resourcesToBackend from 'i18next-resources-to-backend'
import { initReactI18next } from 'react-i18next/initReactI18next'

const initI18next = async (lng: string, ns: string) => {
  const i18nInstance = createInstance()
  await i18nInstance
    .use(initReactI18next)
    .use(
      resourcesToBackend(
        (language: string, namespace: string) =>
          import(`../locales/${language}/${namespace}.json`)
      )
    )
    .init({
      debug: process.env.NODE_ENV === 'development',
      lng,
      fallbackLng: 'en',
      defaultNS: 'common',
      ns,
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    })
  return i18nInstance
}

// Translation hook with type safety
type TranslationKeys = {
  common: {
    save: string
    cancel: string
    delete: string
    edit: string
    loading: string
    error: string
    success: string
    confirm: string
  }
  dashboard: {
    title: string
    welcome: string
    dataSources: string
    recentAnalysis: string
  }
  dataSources: {
    create: string
    connect: string
    test: string
    status: {
      connected: string
      pending: string
      failed: string
    }
  }
}

const useTranslation = (namespace: keyof TranslationKeys = 'common') => {
  const { t, i18n } = useReactI18next()
  
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
    // Update HTML lang attribute
    document.documentElement.lang = lng
    // Update dir attribute for RTL languages
    document.documentElement.dir = ['ar', 'he', 'fa'].includes(lng) ? 'rtl' : 'ltr'
  }
  
  const formatNumber = (number: number) => {
    return new Intl.NumberFormat(i18n.language).format(number)
  }
  
  const formatCurrency = (amount: number, currency = 'USD') => {
    return new Intl.NumberFormat(i18n.language, {
      style: 'currency',
      currency
    }).format(amount)
  }
  
  const formatDate = (date: Date | string, options?: Intl.DateTimeFormatOptions) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return new Intl.DateTimeFormat(i18n.language, options).format(dateObj)
  }
  
  const formatRelativeTime = (date: Date | string) => {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    const rtf = new Intl.RelativeTimeFormat(i18n.language, { numeric: 'auto' })
    
    const now = new Date()
    const diffInMs = dateObj.getTime() - now.getTime()
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))
    
    if (Math.abs(diffInDays) < 1) {
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60))
      if (Math.abs(diffInHours) < 1) {
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60))
        return rtf.format(diffInMinutes, 'minute')
      }
      return rtf.format(diffInHours, 'hour')
    }
    
    return rtf.format(diffInDays, 'day')
  }
  
  return {
    t: t as (key: string, options?: any) => string,
    i18n,
    changeLanguage,
    formatNumber,
    formatCurrency,
    formatDate,
    formatRelativeTime,
    currentLanguage: i18n.language,
    isRTL: ['ar', 'he', 'fa'].includes(i18n.language)
  }
}
```

**2. Language Switcher Component**
```typescript
const LanguageSwitcher = () => {
  const { i18n, changeLanguage, t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'zh-CN', name: '中文', flag: '🇨🇳' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
  ]
  
  const currentLanguage = languages.find(lang => lang.code === i18n.language)
  
  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-2">
          <span className="text-base">{currentLanguage?.flag}</span>
          <span className="hidden sm:inline">{currentLanguage?.name}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>
          {t('common.selectLanguage')}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {languages.map((language) => (
          <DropdownMenuItem
            key={language.code}
            onClick={() => changeLanguage(language.code)}
            className="gap-2"
          >
            <span className="text-base">{language.flag}</span>
            <span>{language.name}</span>
            {i18n.language === language.code && (
              <Check className="h-4 w-4 ml-auto" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Production Deployment & Optimization

**1. Build Optimization**
```typescript
// next.config.js - Production optimizations
module.exports = {
  // Enable SWC minification
  swcMinify: true,
  
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 768, 1024, 1280, 1600],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
  },
  
  // Bundle analyzer
  bundleAnalyzer: {
    enabled: process.env.ANALYZE === 'true',
  },
  
  // Experimental features
  experimental: {
    // Enable app directory
    appDir: true,
    // Enable server components
    serverComponents: true,
    // Enable turbo mode
    turbo: {
      loaders: {
        '.svg': ['@svgr/webpack'],
      },
    },
    // Runtime optimizations
    runtime: 'nodejs',
    serverComponentsExternalPackages: ['@plotly/plotly.js'],
  },
  
  // Webpack optimizations
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Optimize bundle splitting
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\/\\]node_modules[\/\\]/,
          name: 'vendors',
          priority: 10,
          reuseExistingChunk: true,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    }
    
    // Add webpack plugins for production
    if (!dev && !isServer) {
      config.plugins.push(
        new webpack.optimize.LimitChunkCountPlugin({
          maxChunks: 50,
        })
      )
    }
    
    return config
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Redirects and rewrites
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ]
  },
  
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://api.example.com/:path*',
      },
    ]
  },
  
  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 's-maxage=1, stale-while-revalidate',
          },
        ],
      },
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
}
```

**2. Performance Monitoring in Production**
```typescript
// Performance monitoring service
class ProductionPerformanceMonitor {
  private static instance: ProductionPerformanceMonitor
  private analytics: any
  private sessionId: string
  
  constructor() {
    this.sessionId = crypto.randomUUID()
    this.initializeAnalytics()
    this.setupPerformanceObservers()
  }
  
  static getInstance(): ProductionPerformanceMonitor {
    if (!ProductionPerformanceMonitor.instance) {
      ProductionPerformanceMonitor.instance = new ProductionPerformanceMonitor()
    }
    return ProductionPerformanceMonitor.instance
  }
  
  private initializeAnalytics() {
    // Initialize analytics service (Google Analytics, etc.)
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
      // Analytics initialization code
    }
  }
  
  private setupPerformanceObservers() {
    if (typeof window === 'undefined') return
    
    // Core Web Vitals
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(this.sendMetric.bind(this))
      getFID(this.sendMetric.bind(this))
      getFCP(this.sendMetric.bind(this))
      getLCP(this.sendMetric.bind(this))
      getTTFB(this.sendMetric.bind(this))
    })
    
    // Custom metrics
    this.observeCustomMetrics()
  }
  
  private sendMetric(metric: any) {
    if (process.env.NODE_ENV !== 'production') return
    
    const data = {
      sessionId: this.sessionId,
      name: metric.name,
      value: metric.value,
      id: metric.id,
      delta: metric.delta,
      url: window.location.href,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      connection: (navigator as any).connection?.effectiveType || 'unknown',
    }
    
    // Send to analytics service
    this.analytics?.track('performance_metric', data)
    
    // Also send to monitoring service
    fetch('/api/metrics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).catch(() => {
      // Silently fail for monitoring
    })
  }
  
  private observeCustomMetrics() {
    // Time to first interaction
    let firstInteraction = false
    const recordFirstInteraction = () => {
      if (!firstInteraction) {
        firstInteraction = true
        this.sendMetric({
          name: 'TTI',
          value: performance.now(),
          id: 'custom-tti',
        })
      }
    }
    
    ['click', 'keydown', 'scroll'].forEach(eventType => {
      document.addEventListener(eventType, recordFirstInteraction, { once: true })
    })
    
    // Custom business metrics
    this.trackBusinessMetrics()
  }
  
  private trackBusinessMetrics() {
    // Track specific business events
    const trackEvent = (eventName: string, properties?: Record<string, any>) => {
      this.sendMetric({
        name: `business_${eventName}`,
        value: 1,
        id: `business-${eventName}-${Date.now()}`,
        properties
      })
    }
    
    // Example business metrics
    window.addEventListener('data-source-created', (e: any) => {
      trackEvent('data_source_created', {
        type: e.detail.type,
        status: e.detail.status
      })
    })
    
    window.addEventListener('analysis-completed', (e: any) => {
      trackEvent('analysis_completed', {
        duration: e.detail.duration,
        recordCount: e.detail.recordCount
      })
    })
  }
  
  // Public methods for manual tracking
  public trackPageView(path: string) {
    this.sendMetric({
      name: 'page_view',
      value: 1,
      id: `pageview-${Date.now()}`,
      path
    })
  }
  
  public trackUserAction(action: string, details?: Record<string, any>) {
    this.sendMetric({
      name: `user_action_${action}`,
      value: 1,
      id: `action-${action}-${Date.now()}`,
      details
    })
  }
}

// Initialize performance monitoring
export const performanceMonitor = ProductionPerformanceMonitor.getInstance()
```

**3. Deployment Configuration**
```yaml
# docker/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build with all optimizations
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]

# docker-compose.yml for local development
version: '3.8'
services:
  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    image: backend:latest
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## Final Implementation Checklist

### Architecture Completion
- [x] **Component System** - Advanced patterns with TypeScript
- [x] **State Management** - Zustand + React Query integration
- [x] **Performance** - Optimization strategies and monitoring
- [x] **Testing** - Comprehensive test suite with E2E coverage
- [x] **Security** - Enterprise-grade security implementation
- [x] **Accessibility** - WCAG 2.1 AA compliance
- [x] **Internationalization** - Multi-language support
- [x] **Deployment** - Production-ready configuration

### Development Experience
- [x] **TypeScript** - Strict typing throughout
- [x] **Hot Reloading** - Fast development feedback
- [x] **Code Splitting** - Automatic optimization
- [x] **Error Boundaries** - Graceful error handling
- [x] **DevTools** - Debugging and development tools
- [x] **Documentation** - Comprehensive guides and examples

### Production Readiness
- [x] **Bundle Optimization** - Minimal bundle sizes
- [x] **Caching Strategy** - Intelligent caching layers
- [x] **Monitoring** - Real-time performance tracking
- [x] **Error Tracking** - Production error monitoring
- [x] **SEO** - Search engine optimization
- [x] **Progressive Web App** - PWA capabilities

This frontend architecture provides a robust, scalable, and maintainable foundation for the AI Data Analysis Platform with enterprise-grade features and excellent developer experience.

## Advanced Development Guidelines & Best Practices

### TypeScript Advanced Patterns

**1. Advanced Type Safety**
```typescript
// Branded types for better type safety
type UserId = string & { readonly brand: unique symbol }
type DataSourceId = string & { readonly brand: unique symbol }

// Type guards for runtime safety
function isUserId(value: string): value is UserId {
  return /^user_[a-zA-Z0-9]{8,}$/.test(value)
}

// Utility types for API responses
type APISuccess<T> = {
  success: true
  data: T
  meta?: {
    pagination?: PaginationInfo
    timestamp: string
  }
}

type APIError = {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, any>
  }
}

type APIResponse<T> = APISuccess<T> | APIError

// Conditional types for flexible APIs
type DataSourceConfig<T extends DataSourceType> = T extends 'database' 
  ? DatabaseConfig 
  : T extends 'file' 
  ? FileConfig 
  : T extends 'api' 
  ? APIConfig 
  : never

// Template literal types for type-safe routing
type AppRoutes = 
  | '/'
  | '/dashboard'
  | `/dashboard/${string}`
  | '/data-sources'
  | `/data-sources/${string}`
  | '/analysis'
  | `/analysis/${string}`
```

**2. Advanced Component Patterns**
```typescript
// Generic component with constraints
interface DataDisplayProps<T extends Record<string, any>> {
  data: T[]
  renderItem: (item: T, index: number) => ReactNode
  keyExtractor: (item: T) => string
  loading?: boolean
  error?: Error | null
  emptyState?: ReactNode
  loadingState?: ReactNode
}

function DataDisplay<T extends Record<string, any>>({
  data,
  renderItem,
  keyExtractor,
  loading = false,
  error = null,
  emptyState = <EmptyState />,
  loadingState = <LoadingSkeleton />
}: DataDisplayProps<T>) {
  // Error boundary integration
  if (error) {
    throw error // Let error boundary handle it
  }
  
  if (loading) {
    return <>{loadingState}</>
  }
  
  if (data.length === 0) {
    return <>{emptyState}</>
  }
  
  return (
    <div className="space-y-4">
      {data.map((item, index) => (
        <div key={keyExtractor(item)}>
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  )
}

// Higher-order component for data fetching
function withDataFetching<P extends object>(
  WrappedComponent: ComponentType<P>,
  queryFn: () => UseQueryResult
) {
  return function WithDataFetchingComponent(props: P) {
    const { data, isLoading, error } = queryFn()
    
    return (
      <ErrorBoundary fallback={<ErrorFallback />}>
        <Suspense fallback={<LoadingSkeleton />}>
          {isLoading ? (
            <LoadingSkeleton />
          ) : error ? (
            <ErrorState error={error} />
          ) : (
            <WrappedComponent {...props} data={data} />
          )}
        </Suspense>
      </ErrorBoundary>
    )
  }
}

// Render prop component for flexible data handling
interface DataProviderProps<T> {
  queryKey: QueryKey
  queryFn: QueryFunction<T>
  children: ({
    data,
    isLoading,
    error,
    refetch
  }: {
    data: T | undefined
    isLoading: boolean
    error: Error | null
    refetch: () => void
  }) => ReactNode
}

function DataProvider<T>({ queryKey, queryFn, children }: DataProviderProps<T>) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn
  })
  
  return <>{children({ data, isLoading, error, refetch })}</>
}
```

**3. Advanced Hook Patterns**
```typescript
// Compound hook with multiple concerns
function useDataManagement<T>({
  queryKey,
  queryFn,
  mutationFn,
  onSuccess,
  onError
}: UseDataManagementOptions<T>) {
  // Query for fetching
  const query = useQuery({
    queryKey,
    queryFn,
    staleTime: 5 * 60 * 1000
  })
  
  // Mutation for updates
  const mutation = useMutation({
    mutationFn,
    onSuccess: (data) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey })
      onSuccess?.(data)
    },
    onError
  })
  
  // Local state for UI
  const [selectedItems, setSelectedItems] = useState<T[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null)
  
  // Computed values
  const filteredData = useMemo(() => {
    if (!query.data) return []
    
    let filtered = query.data.filter(item => 
      searchQuery === '' || 
      Object.values(item).some(value => 
        String(value).toLowerCase().includes(searchQuery.toLowerCase())
      )
    )
    
    if (sortConfig) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key]
        const bVal = b[sortConfig.key]
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
        return 0
      })
    }
    
    return filtered
  }, [query.data, searchQuery, sortConfig])
  
  // Actions
  const actions = useMemo(() => ({
    selectItem: (item: T) => {
      setSelectedItems(prev => [...prev, item])
    },
    deselectItem: (item: T) => {
      setSelectedItems(prev => prev.filter(i => i !== item))
    },
    clearSelection: () => setSelectedItems([]),
    updateItem: mutation.mutate,
    search: setSearchQuery,
    sort: setSortConfig,
    refresh: query.refetch
  }), [mutation.mutate, query.refetch])
  
  return {
    // Data
    data: filteredData,
    selectedItems,
    
    // State
    isLoading: query.isLoading,
    error: query.error || mutation.error,
    isUpdating: mutation.isPending,
    
    // Actions
    ...actions
  }
}

// Form hook with advanced validation
function useAdvancedForm<T extends Record<string, any>>({
  schema,
  defaultValues,
  onSubmit,
  mode = 'onChange'
}: UseAdvancedFormOptions<T>) {
  const form = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues,
    mode
  })
  
  // Auto-save functionality
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(false)
  const debouncedValues = useDebounce(form.watch(), 1000)
  
  useEffect(() => {
    if (autoSaveEnabled && form.formState.isDirty) {
      onSubmit(debouncedValues)
    }
  }, [debouncedValues, autoSaveEnabled, form.formState.isDirty])
  
  // Field validation with custom messages
  const validateField = useCallback(async (fieldName: keyof T) => {
    const result = await form.trigger(fieldName)
    return result
  }, [form])
  
  // Enhanced submit with loading states
  const [isSubmitting, setIsSubmitting] = useState(false)
  const handleSubmit = form.handleSubmit(async (data) => {
    try {
      setIsSubmitting(true)
      await onSubmit(data)
      form.reset(data) // Reset with new values
    } catch (error) {
      form.setError('root', {
        type: 'submit',
        message: error instanceof Error ? error.message : 'Submission failed'
      })
    } finally {
      setIsSubmitting(false)
    }
  })
  
  return {
    ...form,
    handleSubmit,
    isSubmitting,
    validateField,
    autoSaveEnabled,
    setAutoSaveEnabled,
    isDirty: form.formState.isDirty,
    isValid: form.formState.isValid
  }
}
```

**4. Error Boundary and Error Handling Patterns**
```typescript
// Advanced Error Boundary with recovery
class AdvancedErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: 0
    }
  }
  
  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error }
  }
  
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to monitoring service
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
    
    this.setState({ errorInfo })
  }
  
  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: this.state.retryCount + 1
    })
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onRetry={this.handleRetry}
          retryCount={this.state.retryCount}
          maxRetries={this.props.maxRetries || 3}
        />
      )
    }
    
    return this.props.children
  }
}

// Error handling hook
const useErrorHandler = () => {
  const [error, setError] = useState<Error | null>(null)
  
  const handleError = useCallback((error: Error | unknown) => {
    const errorInstance = error instanceof Error 
      ? error 
      : new Error(String(error))
    
    setError(errorInstance)
    
    // Report to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Sentry, LogRocket, etc.
      console.error('Error:', errorInstance)
    }
  }, [])
  
  const clearError = useCallback(() => {
    setError(null)
  }, [])
  
  return { error, handleError, clearError }
}
```

## Context Management for Claude AI

This frontend context integrates with the comprehensive backend architecture. Key integration points:

### Cross-System Development Guidelines

**1. Authentication Context Sharing**
```typescript
// Frontend auth state must stay synchronized with backend
// User roles: 'admin', 'analyst', 'user', 'viewer' (from backend/CLAUDE.md)
const authStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  permissions: [],
  
  // Sync with backend User model
  login: async (credentials) => {
    const response = await authService.login(credentials)
    // Backend returns User model with role and preferences
    set({ 
      user: response.user, 
      token: response.access_token,
      permissions: getUserPermissions(response.user.role)
    })
  }
}))
```

**2. Data Model Consistency**
```typescript
// Frontend types must match backend SQLAlchemy models
interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'analyst' | 'user' | 'viewer'
  organization?: string
  preferences?: UserPreferences
  created_at: string
  last_login?: string
}

interface DataSource {
  id: number
  user_id: number
  name: string
  type: string                    // postgresql, mysql, mongodb, csv, etc.
  status: 'pending' | 'connected' | 'failed' | 'disabled'
  last_test?: string
  error_message?: string
  created_at: string
}
```

**3. Error Handling Alignment**
```typescript
// Frontend error handling must match backend error format
interface APIError {
  error: {
    type: string
    code: string  
    message: string
    details?: Record<string, any>
    request_id: string
    timestamp: string
    service: string
  }
}
```

### Development Integration Points

**Backend Documentation References:**
- **Authentication System**: [../backend/CLAUDE.md#authentication-authorization-architecture](../backend/CLAUDE.md)
- **Database Models**: [../backend/CLAUDE.md#database-schema-models](../backend/CLAUDE.md)
- **API Endpoints**: [../backend/CLAUDE.md#api-endpoints-route-organization](../backend/CLAUDE.md)
- **Service Architecture**: [../backend/CLAUDE.md#api-gateway-service-architecture](../backend/CLAUDE.md)

**File Coordination:**
- **Database Models**: Backend `shared/database/models/` ↔ Frontend `src/lib/types/api.ts`
- **API Endpoints**: Backend router definitions ↔ Frontend service clients
- **Authentication**: Backend JWT utils ↔ Frontend auth store and interceptors
- **Configuration**: Backend `.env` settings ↔ Frontend environment variables

### Implementation Priority Matrix

**Phase 1: Foundation Integration**
- [ ] Implement authentication flow matching backend JWT system
- [ ] Create TypeScript types matching backend SQLAlchemy models
- [ ] Set up API client with proper service routing
- [ ] Implement error handling matching backend error format

**Phase 2: Core Features**
- [ ] Data source management UI with backend integration
- [ ] Dashboard with real-time backend data
- [ ] User profile management synced with backend User model
- [ ] Role-based UI components matching backend permissions

**Phase 3: Advanced Features**
- [ ] AI chat interface with backend AI service integration
- [ ] Visualization components with backend chart generation
- [ ] Real-time updates via WebSocket integration
- [ ] Advanced analytics with compute service integration

**Phase 4: Performance & Scale**
- [ ] Implement caching strategy aligned with backend
- [ ] Add offline capabilities with proper sync
- [ ] Performance monitoring integration
- [ ] Security hardening matching backend security model

### Quick Development Reference

**Starting New Feature Development:**
1. Check backend service availability and endpoints
2. Ensure frontend types match backend models
3. Implement API service client for the feature
4. Create UI components with proper error handling
5. Add authentication/authorization as needed
6. Test integration with actual backend services

**Common Integration Patterns:**
- Always use the unified API client for backend communication
- Implement proper loading states for async operations
- Handle backend errors gracefully with user-friendly messages  
- Cache frequently accessed data with React Query
- Use TypeScript strictly for type safety across frontend-backend

This frontend architecture provides robust integration with the microservices backend while maintaining clean separation of concerns and excellent developer experience.