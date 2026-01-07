# React Development Guide for AI Coding Agents

This comprehensive guide provides patterns, best practices, and anti-patterns for building React applications. Designed for AI coding assistants and app-building tools to generate high-quality, maintainable React code.

---

## Table of Contents

1. [React 19 Features](#react-19-features)
2. [Project Structure](#project-structure)
3. [Component Patterns](#component-patterns)
4. [TypeScript Best Practices](#typescript-best-practices)
5. [State Management](#state-management)
6. [Data Fetching](#data-fetching)
7. [Forms & Validation](#forms--validation)
8. [Styling](#styling)
9. [Routing](#routing)
10. [Performance Optimization](#performance-optimization)
11. [Testing](#testing)
12. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
13. [Code Generation Rules](#code-generation-rules)

---

## React 19 Features

React 19 (stable December 2024) and React 19.2 (October 2025) introduced significant improvements:

### The `use` Hook
Read promises and context directly in render:

```tsx
// Async data fetching with use()
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Suspends until resolved
  return <h1>{user.name}</h1>;
}
```

### Server Components
Render components on the server, reducing client bundle size:

```tsx
// Server Component (default in Next.js App Router)
async function ProductList() {
  const products = await db.products.findMany();
  return (
    <ul>
      {products.map(p => <ProductCard key={p.id} product={p} />)}
    </ul>
  );
}
```

### Server Actions
Handle form submissions and mutations without API routes:

```tsx
// Server Action
async function createTodo(formData: FormData) {
  'use server';
  const title = formData.get('title');
  await db.todos.create({ data: { title } });
  revalidatePath('/todos');
}

// Client usage
<form action={createTodo}>
  <input name="title" />
  <button type="submit">Add</button>
</form>
```

### Refs as Props
No more `forwardRef` wrapper needed:

```tsx
// React 19: refs work as regular props
function Input({ ref, ...props }: { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
```

### Document Metadata
Native support for `<title>`, `<meta>`, and `<link>` in components:

```tsx
function BlogPost({ post }) {
  return (
    <>
      <title>{post.title}</title>
      <meta name="description" content={post.excerpt} />
      <article>{post.content}</article>
    </>
  );
}
```

### New Form Hooks
- `useFormStatus` - Get pending state of parent form
- `useFormState` - Manage form state with server actions
- `useOptimistic` - Optimistic UI updates

```tsx
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? 'Saving...' : 'Save'}</button>;
}

function LikeButton({ initialLikes }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (state, newLike) => state + 1
  );

  return (
    <form action={async () => {
      addOptimisticLike(1);
      await likePost();
    }}>
      <button>{optimisticLikes} Likes</button>
    </form>
  );
}
```

### Activity Component (React 19.2)
Hide/show parts of UI while preserving state:

```tsx
<Activity mode={isVisible ? 'visible' : 'hidden'}>
  <ExpensiveComponent />
</Activity>
```

---

## Project Structure

### Recommended Feature-Based Structure

```
src/
├── app/                    # App-level setup
│   ├── App.tsx
│   ├── routes.tsx
│   └── providers.tsx
├── features/               # Feature modules
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── api/
│   │   │   └── authApi.ts
│   │   ├── types.ts
│   │   └── index.ts        # Public exports
│   ├── dashboard/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── index.ts
│   └── settings/
├── components/             # Shared UI components
│   ├── ui/                 # Primitives (Button, Input, Card)
│   └── layout/             # Layout components (Header, Sidebar)
├── hooks/                  # Shared custom hooks
├── lib/                    # Utilities and helpers
│   ├── utils.ts
│   └── constants.ts
├── types/                  # Global TypeScript types
└── styles/                 # Global styles
```

### Key Principles

1. **Feature-based organization**: Group related files by feature, not by type
2. **Limit nesting to 2-3 levels**: Deep hierarchies cause import path issues
3. **Use barrel exports** (`index.ts`): Control public API of each feature
4. **Configure absolute imports**: Use `@/` path alias in tsconfig

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Component Patterns

### Functional Components (Default)

Always use functional components with hooks:

```tsx
interface UserCardProps {
  user: User;
  onSelect?: (id: string) => void;
}

function UserCard({ user, onSelect }: UserCardProps) {
  return (
    <div onClick={() => onSelect?.(user.id)}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}
```

### Compound Components Pattern

For complex components with shared state:

```tsx
// Usage
<Tabs defaultValue="tab1">
  <Tabs.List>
    <Tabs.Trigger value="tab1">Tab 1</Tabs.Trigger>
    <Tabs.Trigger value="tab2">Tab 2</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="tab1">Content 1</Tabs.Content>
  <Tabs.Content value="tab2">Content 2</Tabs.Content>
</Tabs>

// Implementation
const TabsContext = createContext<TabsContextValue | null>(null);

function Tabs({ defaultValue, children }) {
  const [activeTab, setActiveTab] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabsTrigger({ value, children }) {
  const { activeTab, setActiveTab } = useContext(TabsContext)!;
  return (
    <button
      data-active={activeTab === value}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
}

Tabs.List = TabsList;
Tabs.Trigger = TabsTrigger;
Tabs.Content = TabsContent;
```

### Custom Hooks Pattern

Extract reusable logic into custom hooks:

```tsx
// useLocalStorage.ts
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// useDebounce.ts
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// useMediaQuery.ts
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    () => window.matchMedia(query).matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

### Controlled vs Uncontrolled Pattern

Support both modes for flexibility:

```tsx
interface InputProps {
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
}

function Input({ value, defaultValue, onChange }: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    if (!isControlled) {
      setInternalValue(newValue);
    }
    onChange?.(newValue);
  };

  return <input value={currentValue} onChange={handleChange} />;
}
```

---

## TypeScript Best Practices

### Props Typing

```tsx
// DO: Explicit interface/type for props
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

function Button({
  variant = 'primary',
  size = 'md',
  isLoading,
  children,
  onClick
}: ButtonProps) {
  return (
    <button
      className={cn(variants[variant], sizes[size])}
      disabled={isLoading}
      onClick={onClick}
    >
      {isLoading ? <Spinner /> : children}
    </button>
  );
}

// DON'T: Use React.FC (adds implicit children)
const Button: React.FC<ButtonProps> = (props) => { ... }
```

### Children Typing

```tsx
// For any renderable content
interface CardProps {
  children: React.ReactNode;
}

// For single element (useful for cloning)
interface WrapperProps {
  children: React.ReactElement;
}

// Using PropsWithChildren utility
type CardProps = React.PropsWithChildren<{
  title: string;
}>;
```

### Event Handlers

```tsx
// Typed event handlers
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log(e.clientX, e.clientY);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
      <button onClick={handleClick}>Submit</button>
    </form>
  );
}
```

### Generic Components

```tsx
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage with type inference
<List
  items={users}
  renderItem={(user) => <span>{user.name}</span>}
  keyExtractor={(user) => user.id}
/>
```

### Discriminated Unions for Props

```tsx
type AlertProps =
  | { type: 'success'; message: string }
  | { type: 'error'; message: string; retry: () => void }
  | { type: 'loading' };

function Alert(props: AlertProps) {
  switch (props.type) {
    case 'success':
      return <div className="success">{props.message}</div>;
    case 'error':
      return (
        <div className="error">
          {props.message}
          <button onClick={props.retry}>Retry</button>
        </div>
      );
    case 'loading':
      return <div className="loading"><Spinner /></div>;
  }
}
```

---

## State Management

### Decision Tree

```
Do you need to share state?
├── No → useState
└── Yes → Is it server/async data?
    ├── Yes → TanStack Query / SWR
    └── No → How many components share it?
        ├── 2-3 nearby → Lift state up
        ├── Many scattered → useContext
        └── Complex logic → Zustand / Jotai
```

### useState for Local State

```tsx
function Counter() {
  const [count, setCount] = useState(0);

  // Functional updates for derived state
  const increment = () => setCount(prev => prev + 1);

  return <button onClick={increment}>{count}</button>;
}
```

### useReducer for Complex State

```tsx
type State = { count: number; step: number };
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'setStep'; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + state.step };
    case 'decrement':
      return { ...state, count: state.count - state.step };
    case 'setStep':
      return { ...state, step: action.payload };
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0, step: 1 });

  return (
    <>
      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({ type: 'setStep', payload: +e.target.value })}
      />
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <span>{state.count}</span>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
    </>
  );
}
```

### Context for Shared State

```tsx
// ThemeContext.tsx
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### Zustand (Recommended for Complex Apps)

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  totalPrice: () => number;
}

const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) => set((state) => ({
        items: [...state.items, item]
      })),
      removeItem: (id) => set((state) => ({
        items: state.items.filter(i => i.id !== id)
      })),
      clearCart: () => set({ items: [] }),
      totalPrice: () => get().items.reduce((sum, item) => sum + item.price, 0),
    }),
    { name: 'cart-storage' }
  )
);

// Usage with selector (prevents unnecessary re-renders)
function CartCount() {
  const count = useCartStore(state => state.items.length);
  return <span>{count}</span>;
}
```

### Jotai (Atomic State)

```tsx
import { atom, useAtom } from 'jotai';

// Primitive atoms
const countAtom = atom(0);
const doubleCountAtom = atom((get) => get(countAtom) * 2);

// Async atom
const userAtom = atom(async () => {
  const response = await fetch('/api/user');
  return response.json();
});

// Usage
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const [doubleCount] = useAtom(doubleCountAtom);

  return (
    <>
      <span>{count} × 2 = {doubleCount}</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </>
  );
}
```

---

## Data Fetching

### TanStack Query (Recommended)

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch data
function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <Skeleton />;
  if (error) return <Error message={error.message} />;
  return <Profile user={data} />;
}

// Mutations
function CreateTodo() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createTodo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      mutation.mutate({ title: e.target.title.value });
    }}>
      <input name="title" />
      <button disabled={mutation.isPending}>
        {mutation.isPending ? 'Adding...' : 'Add'}
      </button>
    </form>
  );
}

// Infinite queries
function InfiniteList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['items'],
    queryFn: ({ pageParam = 0 }) => fetchItems({ offset: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextOffset,
  });

  return (
    <>
      {data?.pages.map(page =>
        page.items.map(item => <Item key={item.id} {...item} />)
      )}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage ? 'Loading...' : 'Load More'}
      </button>
    </>
  );
}
```

### SWR (Simpler Alternative)

```tsx
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

function Profile() {
  const { data, error, isLoading, mutate } = useSWR('/api/user', fetcher);

  if (isLoading) return <Skeleton />;
  if (error) return <Error />;

  return (
    <>
      <h1>{data.name}</h1>
      <button onClick={() => mutate()}>Refresh</button>
    </>
  );
}
```

### Query Key Conventions

```tsx
// Hierarchical keys for easy invalidation
const queryKeys = {
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters: Filters) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
};

// Usage
useQuery({ queryKey: queryKeys.users.detail(userId), ... });

// Invalidate all user queries
queryClient.invalidateQueries({ queryKey: queryKeys.users.all });
```

---

## Forms & Validation

### React Hook Form + Zod (Recommended)

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain number'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type FormData = z.infer<typeof schema>;

function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    await createAccount(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('email')} placeholder="Email" />
        {errors.email && <span className="error">{errors.email.message}</span>}
      </div>

      <div>
        <input {...register('password')} type="password" placeholder="Password" />
        {errors.password && <span className="error">{errors.password.message}</span>}
      </div>

      <div>
        <input {...register('confirmPassword')} type="password" placeholder="Confirm" />
        {errors.confirmPassword && (
          <span className="error">{errors.confirmPassword.message}</span>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Creating...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

### Controlled Form with Validation

```tsx
function ContactForm() {
  const [values, setValues] = useState({ name: '', email: '', message: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!values.name) newErrors.name = 'Name is required';
    if (!values.email.includes('@')) newErrors.email = 'Invalid email';
    if (values.message.length < 10) newErrors.message = 'Message too short';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await submitForm(values);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (field: string) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setValues(prev => ({ ...prev, [field]: e.target.value }));
    setErrors(prev => ({ ...prev, [field]: '' }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={values.name}
        onChange={handleChange('name')}
        aria-invalid={!!errors.name}
        aria-describedby={errors.name ? 'name-error' : undefined}
      />
      {errors.name && <span id="name-error" role="alert">{errors.name}</span>}
      {/* ... other fields */}
    </form>
  );
}
```

---

## Styling

### Tailwind CSS (Recommended in 2025)

```tsx
// Button component with Tailwind + CVA
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        sm: 'h-9 px-3 text-sm',
        md: 'h-10 px-4',
        lg: 'h-11 px-8 text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)} {...props} />
  );
}
```

### CSS Modules (When Tailwind Isn't Available)

```tsx
// Button.module.css
.button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.primary {
  background: var(--color-primary);
  color: white;
}

.secondary {
  background: transparent;
  border: 1px solid var(--color-border);
}

// Button.tsx
import styles from './Button.module.css';

function Button({ variant = 'primary', children }) {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  );
}
```

### cn Utility Function

```tsx
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Usage
<div className={cn(
  'base-class',
  isActive && 'active-class',
  variant === 'large' && 'text-lg'
)} />
```

---

## Routing

### React Router v7

```tsx
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      { index: true, element: <Home /> },
      {
        path: 'users',
        element: <UsersLayout />,
        loader: async () => fetchUsers(),
        children: [
          { index: true, element: <UsersList /> },
          {
            path: ':userId',
            element: <UserDetail />,
            loader: async ({ params }) => fetchUser(params.userId),
          },
        ],
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

function RootLayout() {
  return (
    <>
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
```

### TanStack Router (Type-Safe)

```tsx
import { createRouter, createRoute, createRootRoute } from '@tanstack/react-router';

const rootRoute = createRootRoute({
  component: RootLayout,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Home,
});

const userRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/users/$userId',
  component: UserDetail,
  loader: async ({ params }) => fetchUser(params.userId),
});

const routeTree = rootRoute.addChildren([indexRoute, userRoute]);
const router = createRouter({ routeTree });

// Type-safe navigation
function Navigation() {
  const navigate = useNavigate();

  return (
    <button onClick={() => navigate({ to: '/users/$userId', params: { userId: '123' } })}>
      Go to User
    </button>
  );
}
```

---

## Performance Optimization

### React 19 Compiler

With React 19 Compiler, manual memoization is largely unnecessary. The compiler automatically:
- Memoizes pure components
- Stabilizes callback references
- Optimizes re-renders

**Only use manual memoization when:**
- Profiling shows a specific bottleneck
- Interfacing with external libraries that compare object identity
- Working with virtualized lists

### When Manual Optimization Is Needed

```tsx
// useMemo: Cache expensive calculations
function ExpensiveList({ items, filter }) {
  const filteredItems = useMemo(
    () => items.filter(item => expensiveFilter(item, filter)),
    [items, filter]
  );

  return <List items={filteredItems} />;
}

// useCallback: Stabilize callbacks for memoized children
function Parent() {
  const [count, setCount] = useState(0);

  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return (
    <>
      <span>{count}</span>
      <MemoizedChild onClick={handleClick} />
    </>
  );
}

// memo: Prevent re-renders when props unchanged
const ExpensiveChild = memo(function ExpensiveChild({ data }: { data: Data }) {
  return <ComplexVisualization data={data} />;
});
```

### Code Splitting

```tsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const Dashboard = lazy(() => import('./Dashboard'));
const Analytics = lazy(() => import('./Analytics'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

### Virtualization for Long Lists

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Testing

### Vitest + React Testing Library Setup

```tsx
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    globals: true,
  },
});

// src/test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

### Component Testing

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

describe('LoginForm', () => {
  it('submits with valid credentials', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
});
```

### Testing Hooks

```tsx
import { renderHook, act } from '@testing-library/react';

describe('useCounter', () => {
  it('increments count', () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });
});
```

### Testing with Providers

```tsx
function renderWithProviders(ui: React.ReactElement, options = {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        {ui}
      </ThemeProvider>
    </QueryClientProvider>,
    options
  );
}

// Usage
it('loads user data', async () => {
  renderWithProviders(<UserProfile userId="123" />);

  expect(screen.getByTestId('skeleton')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

---

## Anti-Patterns to Avoid

### 1. Storing Derived State

```tsx
// BAD: Redundant state
function FilteredList({ items }) {
  const [filter, setFilter] = useState('');
  const [filteredItems, setFilteredItems] = useState(items);

  useEffect(() => {
    setFilteredItems(items.filter(i => i.name.includes(filter)));
  }, [items, filter]);

  return <List items={filteredItems} />;
}

// GOOD: Compute during render
function FilteredList({ items }) {
  const [filter, setFilter] = useState('');
  const filteredItems = items.filter(i => i.name.includes(filter));

  return <List items={filteredItems} />;
}
```

### 2. Mutating State Directly

```tsx
// BAD: Direct mutation
const [items, setItems] = useState([{ id: 1, name: 'A' }]);
items[0].name = 'B';  // Won't trigger re-render!
setItems(items);      // Same reference, no update

// GOOD: Create new reference
setItems(items.map(item =>
  item.id === 1 ? { ...item, name: 'B' } : item
));
```

### 3. Using Index as Key

```tsx
// BAD: Index keys cause bugs with reordering/filtering
{items.map((item, index) => <Item key={index} {...item} />)}

// GOOD: Stable unique identifier
{items.map(item => <Item key={item.id} {...item} />)}
```

### 4. Creating Functions in JSX

```tsx
// BAD: New function every render (breaks memoization)
<MemoizedButton onClick={() => handleClick(id)} />

// GOOD: Stable reference
const handleButtonClick = useCallback(() => handleClick(id), [id]);
<MemoizedButton onClick={handleButtonClick} />

// Also GOOD for non-memoized children (simpler, no performance impact)
<Button onClick={() => handleClick(id)} />
```

### 5. Missing Cleanup in Effects

```tsx
// BAD: Memory leak
useEffect(() => {
  const subscription = api.subscribe(data => setData(data));
  // Missing cleanup!
}, []);

// GOOD: Proper cleanup
useEffect(() => {
  const subscription = api.subscribe(data => setData(data));
  return () => subscription.unsubscribe();
}, []);

// GOOD: AbortController for fetch
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') throw err;
    });

  return () => controller.abort();
}, []);
```

### 6. Prop Drilling

```tsx
// BAD: Passing through many levels
<App user={user}>
  <Layout user={user}>
    <Sidebar user={user}>
      <UserMenu user={user} />
    </Sidebar>
  </Layout>
</App>

// GOOD: Context or composition
<UserProvider user={user}>
  <App>
    <Layout>
      <Sidebar>
        <UserMenu />  {/* Uses useUser() hook */}
      </Sidebar>
    </Layout>
  </App>
</UserProvider>
```

### 7. Overusing Context

```tsx
// BAD: Everything in one context
<AppContext.Provider value={{ user, theme, cart, notifications, ... }}>

// GOOD: Split by concern
<AuthProvider>
  <ThemeProvider>
    <CartProvider>
      {children}
    </CartProvider>
  </ThemeProvider>
</AuthProvider>
```

### 8. Functions Named Like Hooks That Aren't Hooks

```tsx
// BAD: Misleading name (no hooks inside)
function useFormatDate(date: Date) {
  return date.toLocaleDateString();
}

// GOOD: Regular utility function
function formatDate(date: Date) {
  return date.toLocaleDateString();
}
```

---

## Code Generation Rules

When generating React code, follow these rules:

### Component Structure

1. **Order imports**: React → third-party → local (components → hooks → utils → types)
2. **Define types/interfaces** near the top, after imports
3. **Order within component**: hooks → derived state → handlers → early returns → JSX

```tsx
// 1. Imports
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui';
import { useAuth } from '@/hooks';
import { formatDate } from '@/lib/utils';
import type { User } from '@/types';

// 2. Types
interface ProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

// 3. Component
export function Profile({ userId, onUpdate }: ProfileProps) {
  // 3a. Hooks
  const { user: currentUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  // 3b. Derived state
  const isOwnProfile = currentUser?.id === userId;
  const displayName = user?.name ?? 'Unknown';

  // 3c. Handlers
  const handleEdit = () => setIsEditing(true);
  const handleSave = async (data: Partial<User>) => {
    await updateUser(userId, data);
    onUpdate?.(data);
    setIsEditing(false);
  };

  // 3d. Early returns
  if (isLoading) return <ProfileSkeleton />;
  if (!user) return <NotFound />;

  // 3e. JSX
  return (
    <div className="profile">
      <h1>{displayName}</h1>
      {isOwnProfile && <Button onClick={handleEdit}>Edit</Button>}
    </div>
  );
}
```

### File Naming Conventions

- Components: `PascalCase.tsx` (e.g., `UserProfile.tsx`)
- Hooks: `camelCase.ts` with `use` prefix (e.g., `useAuth.ts`)
- Utilities: `camelCase.ts` (e.g., `formatDate.ts`)
- Types: `camelCase.ts` or co-located (e.g., `types.ts`)
- Tests: `*.test.tsx` or `*.spec.tsx`

### Default Exports vs Named Exports

- **Prefer named exports** for components (better refactoring support)
- Use default exports only for pages/routes if framework requires

```tsx
// GOOD: Named exports
export function Button() { ... }
export function IconButton() { ... }

// Import
import { Button, IconButton } from './Button';
```

### Essential Patterns Checklist

When generating a new component, consider:

- [ ] TypeScript types for all props
- [ ] Default values for optional props
- [ ] Loading and error states
- [ ] Accessibility (aria labels, keyboard navigation)
- [ ] Responsive design considerations
- [ ] Error boundaries for complex components

### Recommended Library Choices (2025)

| Category | Primary Choice | Alternative |
|----------|----------------|-------------|
| State Management | Zustand | Jotai |
| Server State | TanStack Query | SWR |
| Forms | React Hook Form + Zod | - |
| Styling | Tailwind CSS | CSS Modules |
| Routing | TanStack Router | React Router v7 |
| Testing | Vitest + RTL | Jest + RTL |
| Animation | Framer Motion | React Spring |
| Tables | TanStack Table | - |
| Date Handling | date-fns | dayjs |

---

## Quick Reference

### Essential Hooks

| Hook | Purpose |
|------|---------|
| `useState` | Local component state |
| `useEffect` | Side effects (fetch, subscriptions, DOM) |
| `useContext` | Read context values |
| `useReducer` | Complex state logic |
| `useCallback` | Memoize functions |
| `useMemo` | Memoize expensive calculations |
| `useRef` | Persist values across renders, DOM refs |
| `useId` | Generate unique IDs for accessibility |
| `use` (React 19) | Read promises/context in render |
| `useOptimistic` (React 19) | Optimistic UI updates |
| `useFormStatus` (React 19) | Form pending state |

### JSX Patterns

```tsx
// Conditional rendering
{isLoggedIn && <Dashboard />}
{isLoggedIn ? <Dashboard /> : <Login />}

// List rendering
{items.map(item => <Item key={item.id} {...item} />)}

// Spread props
<Button {...buttonProps} />

// Children as function (render props)
<DataProvider>
  {(data) => <Display data={data} />}
</DataProvider>

// Fragment
<>
  <Header />
  <Main />
</>
```

---

*Last updated: January 2025 | React 19.2*
