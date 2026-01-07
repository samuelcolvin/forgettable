# Tailwind CSS with React Guide for AI Coding Agents

This comprehensive guide provides patterns, best practices, and utilities for using Tailwind CSS with React applications. Designed for AI coding assistants and app-building tools to generate high-quality, maintainable styled components.

---

## Table of Contents

1. [Tailwind CSS v4 Overview](#tailwind-css-v4-overview)
2. [Installation & Setup](#installation--setup)
3. [The @theme Directive](#the-theme-directive)
4. [Core Utility Patterns](#core-utility-patterns)
5. [Responsive Design](#responsive-design)
6. [Container Queries](#container-queries)
7. [Dark Mode](#dark-mode)
8. [Component Styling Patterns](#component-styling-patterns)
9. [The cn Utility](#the-cn-utility)
10. [Class Variance Authority (CVA)](#class-variance-authority-cva)
11. [Animation & Transitions](#animation--transitions)
12. [Layout Patterns](#layout-patterns)
13. [Common UI Patterns](#common-ui-patterns)
14. [Performance & Best Practices](#performance--best-practices)
15. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
16. [Quick Reference](#quick-reference)

---

## Tailwind CSS v4 Overview

Tailwind CSS v4 (released January 2025) is a ground-up rewrite with significant improvements:

### Key Changes from v3

| Feature | v3 | v4 |
|---------|----|----|
| Configuration | `tailwind.config.js` | CSS-first with `@theme` |
| Build Speed | Fast | 5x faster (100x incremental) |
| Color Space | RGB | OKLCH |
| Container Queries | Plugin required | Built-in |
| Package Size | Baseline | 35% smaller |

### New Features

- **Oxide Engine**: Rust-powered for maximum performance
- **CSS-first configuration**: Use `@theme` directive instead of JavaScript config
- **Native container queries**: `@container` and `@sm:`, `@md:` variants built-in
- **Modern CSS features**: Cascade layers, `@property`, `color-mix()`
- **3D transforms**: New scale, rotate, and transform utilities
- **Automatic content detection**: No need to configure `content` paths

### Browser Support

Tailwind v4 requires: Safari 16.4+, Chrome 111+, Firefox 128+

---

## Installation & Setup

### Vite + React (Recommended)

```bash
# Create project
npm create vite@latest my-app -- --template react-ts
cd my-app

# Install Tailwind CSS v4
npm install tailwindcss @tailwindcss/vite
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

```css
/* src/index.css */
@import "tailwindcss";
```

### Path Aliases Setup

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

```typescript
// vite.config.ts
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

---

## The @theme Directive

The `@theme` directive is how you customize Tailwind in v4. Theme variables create corresponding utility classes.

### Basic Theme Configuration

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* Colors - generates bg-brand, text-brand, border-brand, etc. */
  --color-brand: oklch(0.7 0.15 250);
  --color-brand-light: oklch(0.85 0.1 250);
  --color-brand-dark: oklch(0.5 0.2 250);

  /* Fonts - generates font-display, font-body */
  --font-display: "Cal Sans", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;

  /* Spacing - generates p-18, m-18, gap-18, etc. */
  --spacing-18: 4.5rem;
  --spacing-128: 32rem;

  /* Breakpoints - generates sm:, md:, lg:, etc. */
  --breakpoint-xs: 30rem;
  --breakpoint-3xl: 120rem;

  /* Border radius */
  --radius-4xl: 2rem;

  /* Shadows */
  --shadow-soft: 0 2px 15px -3px rgb(0 0 0 / 0.1);

  /* Animations */
  --animate-fade-in: fade-in 0.3s ease-out;

  /* Easing */
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Theme Variable Namespaces

| Namespace | Generates | Example |
|-----------|-----------|---------|
| `--color-*` | Color utilities | `--color-success` → `bg-success`, `text-success` |
| `--font-*` | Font family | `--font-mono` → `font-mono` |
| `--spacing-*` | Spacing utilities | `--spacing-18` → `p-18`, `m-18`, `gap-18` |
| `--breakpoint-*` | Responsive prefixes | `--breakpoint-3xl` → `3xl:` |
| `--radius-*` | Border radius | `--radius-pill` → `rounded-pill` |
| `--shadow-*` | Box shadows | `--shadow-soft` → `shadow-soft` |
| `--animate-*` | Animations | `--animate-spin` → `animate-spin` |
| `--ease-*` | Timing functions | `--ease-bounce` → `ease-bounce` |

### @theme inline for CSS Variables

Use `@theme inline` when referencing CSS variables that change dynamically:

```css
@import "tailwindcss";

/* Define theme tokens that reference CSS variables */
@theme inline {
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
}

/* Define the actual values */
:root {
  --primary: oklch(0.7 0.15 250);
  --primary-foreground: oklch(0.98 0 0);
  --background: oklch(0.98 0 0);
  --foreground: oklch(0.1 0 0);
}

.dark {
  --primary: oklch(0.8 0.12 250);
  --primary-foreground: oklch(0.1 0 0);
  --background: oklch(0.1 0 0);
  --foreground: oklch(0.98 0 0);
}
```

---

## Core Utility Patterns

### Spacing

```tsx
// Padding
<div className="p-4">All sides</div>
<div className="px-4 py-2">Horizontal/Vertical</div>
<div className="pt-4 pr-2 pb-4 pl-2">Individual sides</div>

// Margin
<div className="m-4">All sides</div>
<div className="mx-auto">Center horizontally</div>
<div className="mt-8 mb-4">Top/Bottom</div>
<div className="-mt-4">Negative margin</div>

// Gap (for flex/grid)
<div className="flex gap-4">Uniform gap</div>
<div className="grid gap-x-4 gap-y-2">Different gaps</div>

// Space between children
<div className="space-y-4">Vertical spacing</div>
<div className="space-x-2">Horizontal spacing</div>
```

### Typography

```tsx
// Font size
<p className="text-xs">12px</p>
<p className="text-sm">14px</p>
<p className="text-base">16px</p>
<p className="text-lg">18px</p>
<p className="text-xl">20px</p>
<p className="text-2xl">24px</p>
<p className="text-4xl">36px</p>

// Font weight
<p className="font-normal">400</p>
<p className="font-medium">500</p>
<p className="font-semibold">600</p>
<p className="font-bold">700</p>

// Line height
<p className="leading-tight">1.25</p>
<p className="leading-normal">1.5</p>
<p className="leading-relaxed">1.625</p>

// Text alignment
<p className="text-left">Left</p>
<p className="text-center">Center</p>
<p className="text-right">Right</p>

// Text color & decoration
<p className="text-gray-600">Gray text</p>
<p className="underline decoration-2">Underlined</p>
<p className="line-through">Strikethrough</p>
<p className="truncate">Truncate with ellipsis...</p>
```

### Colors

```tsx
// Background
<div className="bg-white">White background</div>
<div className="bg-gray-100">Light gray</div>
<div className="bg-blue-500">Blue</div>
<div className="bg-blue-500/50">50% opacity</div>

// Text
<p className="text-gray-900">Dark text</p>
<p className="text-blue-600">Blue text</p>

// Border
<div className="border border-gray-200">Default border</div>
<div className="border-2 border-blue-500">Thick blue border</div>

// Ring (focus outline)
<button className="ring-2 ring-blue-500 ring-offset-2">Focused</button>
```

### Sizing

```tsx
// Width
<div className="w-full">100%</div>
<div className="w-1/2">50%</div>
<div className="w-64">16rem / 256px</div>
<div className="w-screen">100vw</div>
<div className="max-w-md">max-width: 28rem</div>
<div className="min-w-0">min-width: 0</div>

// Height
<div className="h-full">100%</div>
<div className="h-screen">100vh</div>
<div className="h-64">16rem</div>
<div className="min-h-screen">min-height: 100vh</div>

// Aspect ratio
<div className="aspect-video">16:9</div>
<div className="aspect-square">1:1</div>
```

---

## Responsive Design

Tailwind uses a mobile-first breakpoint system. Unprefixed utilities apply to all screen sizes; prefixed utilities apply at that breakpoint and above.

### Default Breakpoints

| Prefix | Min-width | CSS |
|--------|-----------|-----|
| `sm:` | 640px (40rem) | `@media (min-width: 640px)` |
| `md:` | 768px (48rem) | `@media (min-width: 768px)` |
| `lg:` | 1024px (64rem) | `@media (min-width: 1024px)` |
| `xl:` | 1280px (80rem) | `@media (min-width: 1280px)` |
| `2xl:` | 1536px (96rem) | `@media (min-width: 1536px)` |

### Common Patterns

```tsx
// Mobile-first column to row layout
<div className="flex flex-col md:flex-row gap-4">
  <div className="w-full md:w-1/3">Sidebar</div>
  <div className="w-full md:w-2/3">Main</div>
</div>

// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// Hide/show at breakpoints
<nav className="hidden md:flex">Desktop nav</nav>
<button className="md:hidden">Mobile menu</button>

// Responsive typography
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
  Responsive Heading
</h1>

// Responsive spacing
<section className="py-8 md:py-12 lg:py-16 px-4 md:px-8">
  Content with responsive padding
</section>

// Responsive positioning
<div className="relative md:static">
  <div className="absolute md:relative top-0 right-0">
    Element
  </div>
</div>
```

### Max-Width Breakpoints

```tsx
// Apply only below a breakpoint
<div className="max-md:hidden">Hidden on mobile, visible on md+</div>
<div className="max-lg:flex-col">Column on < lg, row on lg+</div>
```

### Custom Breakpoints (v4)

```css
@theme {
  --breakpoint-xs: 30rem;   /* 480px */
  --breakpoint-3xl: 120rem; /* 1920px */
}
```

```tsx
<div className="xs:text-sm 3xl:text-xl">Custom breakpoints</div>
```

---

## Container Queries

Container queries style elements based on parent container size, not viewport. Built into Tailwind v4.

### Basic Usage

```tsx
// Mark parent as container
<div className="@container">
  {/* Style based on container width */}
  <div className="flex flex-col @md:flex-row @lg:gap-8">
    <div className="@md:w-1/2">Left</div>
    <div className="@md:w-1/2">Right</div>
  </div>
</div>
```

### Container Breakpoints

| Prefix | Min-width |
|--------|-----------|
| `@xs:` | 20rem (320px) |
| `@sm:` | 24rem (384px) |
| `@md:` | 28rem (448px) |
| `@lg:` | 32rem (512px) |
| `@xl:` | 36rem (576px) |
| `@2xl:` | 42rem (672px) |

### Named Containers

```tsx
// Name the container
<div className="@container/sidebar">
  <div className="@md/sidebar:hidden">
    Hidden when sidebar is md or larger
  </div>
</div>
```

### Arbitrary Container Values

```tsx
<div className="@container">
  <div className="@[500px]:grid-cols-3">
    Grid at 500px container width
  </div>
</div>
```

### When to Use Container Queries

- **Component libraries**: Make components responsive regardless of where they're placed
- **Card layouts**: Cards that adapt to their grid cell size
- **Sidebars**: Content that adapts when sidebar expands/collapses
- **Modals/Drawers**: Content that adapts to modal size

```tsx
// Reusable card component
function ProductCard({ product }) {
  return (
    <article className="@container">
      <div className="flex flex-col @sm:flex-row gap-4">
        <img
          src={product.image}
          className="w-full @sm:w-32 @md:w-48 aspect-square object-cover rounded"
        />
        <div className="flex-1">
          <h3 className="text-lg @md:text-xl font-semibold">{product.name}</h3>
          <p className="text-gray-600 @sm:line-clamp-2 @md:line-clamp-none">
            {product.description}
          </p>
          <p className="text-xl font-bold mt-2">${product.price}</p>
        </div>
      </div>
    </article>
  );
}
```

---

## Dark Mode

### Class-Based Dark Mode (Recommended)

```css
/* index.css */
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));
```

```tsx
// Toggle dark mode by adding/removing .dark class on <html>
<html className="dark">

// Usage in components
<div className="bg-white dark:bg-gray-900">
  <p className="text-gray-900 dark:text-gray-100">
    Adapts to dark mode
  </p>
</div>
```

### Dark Mode Provider

```tsx
// hooks/useTheme.ts
import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (theme: Theme) => void;
} | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('theme') as Theme) || 'system';
    }
    return 'system';
  });

  useEffect(() => {
    const root = document.documentElement;
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      root.classList.add(systemDark ? 'dark' : 'light');
    } else {
      root.classList.add(theme);
    }

    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

### Common Dark Mode Patterns

```tsx
// Backgrounds
<div className="bg-white dark:bg-gray-900">
<div className="bg-gray-50 dark:bg-gray-800">
<div className="bg-gray-100 dark:bg-gray-700">

// Text
<p className="text-gray-900 dark:text-white">Primary text</p>
<p className="text-gray-600 dark:text-gray-400">Secondary text</p>
<p className="text-gray-500 dark:text-gray-500">Muted text</p>

// Borders
<div className="border-gray-200 dark:border-gray-700">
<div className="divide-gray-200 dark:divide-gray-700">

// Shadows (often hidden in dark mode)
<div className="shadow-lg dark:shadow-none dark:ring-1 dark:ring-gray-700">

// Hover states
<button className="hover:bg-gray-100 dark:hover:bg-gray-800">
```

---

## Component Styling Patterns

### Extracting Components (Not @apply)

Instead of using `@apply` to create reusable classes, create React components:

```tsx
// DON'T: @apply in CSS
// .btn-primary { @apply px-4 py-2 bg-blue-500 text-white rounded; }

// DO: React component
function Button({ variant = 'primary', size = 'md', children, ...props }) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        {
          primary: 'bg-blue-600 text-white hover:bg-blue-700',
          secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
          ghost: 'hover:bg-gray-100',
        }[variant],
        {
          sm: 'h-8 px-3 text-sm',
          md: 'h-10 px-4',
          lg: 'h-12 px-6 text-lg',
        }[size]
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

### When @apply Is Acceptable

Use `@apply` only for:
- Base typography styles in prose content
- Third-party component styling
- Complex pseudo-element styling

```css
/* Styling markdown content */
.prose h1 {
  @apply text-3xl font-bold mb-4;
}

.prose p {
  @apply text-gray-700 leading-relaxed mb-4;
}

/* Complex pseudo-elements */
.custom-checkbox::before {
  @apply absolute inset-0 flex items-center justify-center;
}
```

---

## The cn Utility

The `cn` utility combines `clsx` (conditional classes) with `tailwind-merge` (deduplication):

### Setup

```bash
npm install clsx tailwind-merge
```

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### Usage Patterns

```tsx
import { cn } from '@/lib/utils';

// Basic conditional classes
<div className={cn(
  'base-class',
  isActive && 'active-class',
  isDisabled && 'opacity-50 cursor-not-allowed'
)} />

// Object syntax
<div className={cn({
  'bg-blue-500': variant === 'primary',
  'bg-gray-500': variant === 'secondary',
  'opacity-50': isDisabled,
})} />

// Array syntax
<div className={cn([
  'base',
  condition1 && 'class1',
  condition2 && 'class2',
])} />

// Merging with external className prop
function Card({ className, children }) {
  return (
    <div className={cn(
      'rounded-lg border bg-white p-4 shadow-sm',
      className // Allows overriding defaults
    )}>
      {children}
    </div>
  );
}

// Usage - custom padding overrides default
<Card className="p-8">Large padding card</Card>
```

### Why tailwind-merge Matters

```tsx
// Without tailwind-merge
clsx('p-4', 'p-8') // => 'p-4 p-8' (both applied, unpredictable)

// With tailwind-merge
cn('p-4', 'p-8') // => 'p-8' (last wins, as expected)

// Complex merging
cn('px-4 py-2', 'p-6') // => 'p-6' (p-6 overrides both)
cn('text-red-500', 'text-blue-500') // => 'text-blue-500'
```

---

## Class Variance Authority (CVA)

CVA provides a structured way to define component variants with TypeScript support.

### Setup

```bash
npm install class-variance-authority
```

### Basic Usage

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base styles (always applied)
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500',
        outline: 'border border-gray-300 bg-transparent hover:bg-gray-100',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
        ghost: 'hover:bg-gray-100 hover:text-gray-900',
        link: 'text-blue-600 underline-offset-4 hover:underline',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4',
        lg: 'h-12 px-6 text-lg',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

// Extract types from CVA
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants>;

function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}

// Usage
<Button>Default</Button>
<Button variant="destructive" size="lg">Delete</Button>
<Button variant="outline" className="w-full">Custom width</Button>
```

### Compound Variants

Apply styles when multiple variant conditions are met:

```tsx
const alertVariants = cva(
  'rounded-lg border p-4',
  {
    variants: {
      variant: {
        default: 'bg-gray-50 border-gray-200',
        success: 'bg-green-50 border-green-200',
        warning: 'bg-yellow-50 border-yellow-200',
        error: 'bg-red-50 border-red-200',
      },
      size: {
        sm: 'text-sm p-3',
        md: 'text-base p-4',
        lg: 'text-lg p-6',
      },
      hasIcon: {
        true: 'pl-12',
        false: '',
      },
    },
    compoundVariants: [
      // When error + large, add extra emphasis
      {
        variant: 'error',
        size: 'lg',
        className: 'border-2 font-medium',
      },
      // When has icon, adjust padding based on size
      {
        hasIcon: true,
        size: 'sm',
        className: 'pl-10',
      },
    ],
    defaultVariants: {
      variant: 'default',
      size: 'md',
      hasIcon: false,
    },
  }
);
```

---

## Animation & Transitions

### Built-in Transitions

```tsx
// Transition properties
<div className="transition">All properties</div>
<div className="transition-colors">Colors only</div>
<div className="transition-opacity">Opacity only</div>
<div className="transition-transform">Transform only</div>
<div className="transition-shadow">Shadow only</div>

// Duration
<div className="transition duration-150">150ms</div>
<div className="transition duration-300">300ms</div>
<div className="transition duration-500">500ms</div>

// Easing
<div className="transition ease-in">Ease in</div>
<div className="transition ease-out">Ease out</div>
<div className="transition ease-in-out">Ease in-out</div>

// Common pattern: hover effect
<button className="transition-colors duration-200 bg-blue-500 hover:bg-blue-600">
  Hover me
</button>
```

### Built-in Animations

```tsx
<div className="animate-spin">Spinning</div>
<div className="animate-ping">Pinging</div>
<div className="animate-pulse">Pulsing</div>
<div className="animate-bounce">Bouncing</div>
```

### Custom Animations (v4)

```css
@theme {
  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

```tsx
<div className="animate-fade-in">Fades in</div>
<div className="animate-slide-up">Slides up</div>
```

### Transform Utilities

```tsx
// Scale
<div className="scale-95 hover:scale-100 transition-transform">
  Grows on hover
</div>

// Rotate
<div className="rotate-45">45 degrees</div>
<div className="hover:rotate-180 transition-transform duration-500">
  Spins on hover
</div>

// Translate
<div className="translate-x-4">Move right</div>
<div className="hover:-translate-y-1 transition-transform">
  Lift on hover
</div>

// Skew
<div className="skew-x-12">Skewed</div>

// 3D transforms (v4)
<div className="rotate-x-45">Rotate on X axis</div>
<div className="rotate-y-180">Rotate on Y axis</div>
<div className="perspective-500">Perspective container</div>
```

---

## Layout Patterns

### Flexbox

```tsx
// Basic flex container
<div className="flex">Horizontal row</div>
<div className="flex flex-col">Vertical column</div>
<div className="inline-flex">Inline flex</div>

// Direction & wrap
<div className="flex flex-row-reverse">Reversed row</div>
<div className="flex flex-wrap">Wrap items</div>

// Justify content (main axis)
<div className="flex justify-start">Start</div>
<div className="flex justify-center">Center</div>
<div className="flex justify-end">End</div>
<div className="flex justify-between">Space between</div>
<div className="flex justify-around">Space around</div>
<div className="flex justify-evenly">Space evenly</div>

// Align items (cross axis)
<div className="flex items-start">Top</div>
<div className="flex items-center">Center</div>
<div className="flex items-end">Bottom</div>
<div className="flex items-stretch">Stretch</div>
<div className="flex items-baseline">Baseline</div>

// Gap
<div className="flex gap-4">Uniform gap</div>
<div className="flex gap-x-4 gap-y-2">Different gaps</div>

// Child properties
<div className="flex-1">Grow to fill</div>
<div className="flex-none">Don't grow</div>
<div className="flex-shrink-0">Don't shrink</div>
<div className="self-center">Override alignment</div>
```

### Grid

```tsx
// Basic grid
<div className="grid grid-cols-3 gap-4">3 columns</div>
<div className="grid grid-cols-12 gap-4">12-column grid</div>

// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => <Card key={item.id} />)}
</div>

// Auto-fit/auto-fill
<div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  Auto-sizing columns
</div>

// Spanning
<div className="col-span-2">Span 2 columns</div>
<div className="col-span-full">Span all columns</div>
<div className="row-span-2">Span 2 rows</div>

// Placement
<div className="col-start-2 col-end-4">Columns 2-3</div>
<div className="row-start-1 row-end-3">Rows 1-2</div>

// Template rows
<div className="grid grid-rows-3 grid-flow-col">3 rows, fill columns</div>
```

### Common Layout Patterns

```tsx
// Centered content
<div className="flex items-center justify-center min-h-screen">
  Centered
</div>

// Sticky header layout
<div className="min-h-screen flex flex-col">
  <header className="sticky top-0 z-50 bg-white border-b">Header</header>
  <main className="flex-1">Content</main>
  <footer>Footer</footer>
</div>

// Sidebar layout
<div className="flex min-h-screen">
  <aside className="w-64 shrink-0 border-r">Sidebar</aside>
  <main className="flex-1 p-8">Main content</main>
</div>

// Holy grail layout
<div className="min-h-screen grid grid-rows-[auto_1fr_auto]">
  <header className="p-4 border-b">Header</header>
  <div className="grid grid-cols-[200px_1fr_200px]">
    <nav className="p-4 border-r">Nav</nav>
    <main className="p-4">Main</main>
    <aside className="p-4 border-l">Aside</aside>
  </div>
  <footer className="p-4 border-t">Footer</footer>
</div>

// Card grid with consistent heights
<div className="grid grid-cols-3 gap-4">
  <div className="flex flex-col">
    <div className="flex-1">Variable content</div>
    <div>Fixed footer</div>
  </div>
</div>
```

---

## Common UI Patterns

### Cards

```tsx
function Card({ title, description, image, children }) {
  return (
    <div className="rounded-lg border bg-white shadow-sm overflow-hidden">
      {image && (
        <img src={image} alt="" className="w-full h-48 object-cover" />
      )}
      <div className="p-6">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-gray-600 mt-2">{description}</p>
        {children}
      </div>
    </div>
  );
}
```

### Badges

```tsx
const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
  {
    variants: {
      variant: {
        default: 'bg-gray-100 text-gray-800',
        primary: 'bg-blue-100 text-blue-800',
        success: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);
```

### Form Inputs

```tsx
// Text input
<input
  type="text"
  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm
    placeholder:text-gray-400
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
    disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed"
  placeholder="Enter text..."
/>

// With error state
<input
  className={cn(
    'w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2',
    hasError
      ? 'border-red-500 focus:ring-red-500'
      : 'border-gray-300 focus:ring-blue-500'
  )}
/>

// Checkbox
<input
  type="checkbox"
  className="h-4 w-4 rounded border-gray-300 text-blue-600
    focus:ring-blue-500 focus:ring-offset-0"
/>
```

### Avatars

```tsx
function Avatar({ src, alt, size = 'md', fallback }) {
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
    xl: 'h-16 w-16 text-lg',
  };

  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={cn('rounded-full object-cover', sizes[size])}
      />
    );
  }

  return (
    <div className={cn(
      'rounded-full bg-gray-200 flex items-center justify-center font-medium text-gray-600',
      sizes[size]
    )}>
      {fallback}
    </div>
  );
}
```

### Loading States

```tsx
// Skeleton
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
</div>

// Spinner
<div className="animate-spin h-5 w-5 border-2 border-gray-300 border-t-blue-600 rounded-full" />

// Loading overlay
<div className="absolute inset-0 bg-white/80 flex items-center justify-center">
  <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full" />
</div>
```

---

## Performance & Best Practices

### 1. Keep Classes Complete

```tsx
// BAD: Dynamic class construction (won't be detected)
<div className={`text-${color}-500`}>

// GOOD: Complete class strings
<div className={cn({
  'text-red-500': color === 'red',
  'text-blue-500': color === 'blue',
  'text-green-500': color === 'green',
})}>
```

### 2. Use Semantic Color Names

```css
@theme {
  /* Semantic names */
  --color-primary: oklch(0.7 0.15 250);
  --color-secondary: oklch(0.6 0.1 200);
  --color-success: oklch(0.7 0.2 145);
  --color-warning: oklch(0.8 0.15 85);
  --color-error: oklch(0.65 0.2 25);
}
```

### 3. Extract Repeated Patterns

```tsx
// If you use this pattern more than twice:
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">

// Create a component:
function Button({ children, ...props }) {
  return (
    <button
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      {...props}
    >
      {children}
    </button>
  );
}
```

### 4. Organize Long Class Lists

```tsx
// Group related utilities with line breaks in template literals
<div className={`
  /* Layout */
  flex flex-col md:flex-row items-center gap-4
  /* Sizing */
  w-full max-w-4xl mx-auto
  /* Spacing */
  p-6 md:p-8
  /* Visual */
  bg-white rounded-lg shadow-sm border
  /* Typography */
  text-gray-900
`}>
```

### 5. Prefer Utilities Over Arbitrary Values

```tsx
// BAD: Arbitrary values
<div className="w-[327px] p-[13px] text-[15px]">

// GOOD: Use scale values
<div className="w-80 p-3 text-sm">

// OK: Arbitrary when necessary
<div className="grid-cols-[200px_1fr_200px]">
```

---

## Anti-Patterns to Avoid

### 1. Class Soup Without Organization

```tsx
// BAD: Unorganized mess
<div className="flex p-4 border text-sm items-center rounded-lg bg-white gap-2 shadow-sm justify-between hover:shadow-md transition-shadow">

// GOOD: Organized by concern
<div className={cn(
  // Layout
  'flex items-center justify-between gap-2',
  // Spacing
  'p-4',
  // Visual
  'bg-white border rounded-lg shadow-sm',
  // Typography
  'text-sm',
  // Interaction
  'hover:shadow-md transition-shadow'
)}>
```

### 2. Overusing @apply

```css
/* BAD: Recreating component systems in CSS */
.btn { @apply px-4 py-2 rounded; }
.btn-primary { @apply bg-blue-500 text-white; }
.btn-secondary { @apply bg-gray-100 text-gray-900; }
.btn-sm { @apply text-sm px-3 py-1; }
.btn-lg { @apply text-lg px-6 py-3; }
```

```tsx
// GOOD: Use CVA + React components instead
```

### 3. Not Using the cn Utility

```tsx
// BAD: String concatenation
<div className={'base-class ' + (isActive ? 'active' : '')}>

// BAD: Template literals with spacing issues
<div className={`base-class ${isActive && 'active'}`}>

// GOOD: cn utility
<div className={cn('base-class', isActive && 'active')}>
```

### 4. Ignoring Accessibility

```tsx
// BAD: Visual-only focus
<button className="focus:outline-none">

// GOOD: Visible focus indicator
<button className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
```

### 5. Not Allowing Style Overrides

```tsx
// BAD: Component doesn't accept className
function Card({ children }) {
  return <div className="p-4 rounded-lg border">{children}</div>;
}

// GOOD: Merge with external className
function Card({ className, children }) {
  return (
    <div className={cn('p-4 rounded-lg border', className)}>
      {children}
    </div>
  );
}
```

---

## Quick Reference

### Spacing Scale

| Class | Value |
|-------|-------|
| `*-0` | 0 |
| `*-1` | 0.25rem (4px) |
| `*-2` | 0.5rem (8px) |
| `*-3` | 0.75rem (12px) |
| `*-4` | 1rem (16px) |
| `*-5` | 1.25rem (20px) |
| `*-6` | 1.5rem (24px) |
| `*-8` | 2rem (32px) |
| `*-10` | 2.5rem (40px) |
| `*-12` | 3rem (48px) |
| `*-16` | 4rem (64px) |
| `*-20` | 5rem (80px) |
| `*-24` | 6rem (96px) |

### Common State Variants

| Variant | Description |
|---------|-------------|
| `hover:` | Mouse hover |
| `focus:` | Focus state |
| `focus-visible:` | Keyboard focus only |
| `active:` | Active/pressed |
| `disabled:` | Disabled state |
| `group-hover:` | Parent has hover |
| `peer-invalid:` | Sibling is invalid |
| `first:` | First child |
| `last:` | Last child |
| `odd:` | Odd children |
| `even:` | Even children |

### Essential Utilities Cheatsheet

```tsx
// Centering
<div className="flex items-center justify-center">
<div className="grid place-items-center">
<div className="mx-auto">

// Full height layouts
<div className="min-h-screen">
<div className="h-full">

// Truncate text
<p className="truncate">Single line with ellipsis</p>
<p className="line-clamp-2">Multi-line with ellipsis</p>

// Hide/show
<div className="hidden md:block">Hidden on mobile</div>
<div className="md:hidden">Visible only on mobile</div>

// Sticky positioning
<header className="sticky top-0 z-50">

// Absolute positioning
<div className="relative">
  <div className="absolute top-0 right-0">
  <div className="absolute inset-0">Full overlay</div>
</div>

// Screen reader only
<span className="sr-only">Accessible label</span>
```

---

*Last updated: January 2025 | Tailwind CSS v4*
