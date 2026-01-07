# shadcn/ui Component Guide for AI Coding Agents

This comprehensive guide provides patterns, best practices, and usage examples for shadcn/ui components in React applications. Designed for AI coding assistants and app-building tools to generate high-quality, accessible UI.

---

## Table of Contents

1. [What is shadcn/ui](#what-is-shadcnui)
2. [Installation & Setup](#installation--setup)
3. [Theming & CSS Variables](#theming--css-variables)
4. [Core Components](#core-components)
5. [Form Components](#form-components)
6. [Data Display](#data-display)
7. [Feedback Components](#feedback-components)
8. [Overlay Components](#overlay-components)
9. [Navigation Components](#navigation-components)
10. [Layout Components](#layout-components)
11. [Form Handling with React Hook Form](#form-handling-with-react-hook-form)
12. [Data Tables](#data-tables)
13. [Patterns & Recipes](#patterns--recipes)
14. [Best Practices](#best-practices)
15. [Component Reference](#component-reference)

---

## What is shadcn/ui

shadcn/ui is **not a component library**—it's a collection of beautifully designed, accessible components that you copy into your project. Key principles:

- **Open Code**: Components are copied to your codebase, not installed as dependencies
- **Composition**: Built on Radix UI primitives with consistent APIs
- **Customizable**: Full control over styling and behavior
- **Accessible**: WCAG-compliant with keyboard navigation and screen reader support
- **AI-Ready**: Open code that LLMs can read and modify

### When to Use shadcn/ui

- Building custom design systems
- Need full control over component code
- Want accessible components out of the box
- Using Tailwind CSS for styling
- Building with React/Next.js

---

## Installation & Setup

### Vite + React Setup

```bash
# 1. Create Vite project
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# 2. Install Tailwind CSS v4
npm install tailwindcss @tailwindcss/vite

# 3. Configure Vite
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

```json
// tsconfig.json - add paths
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

```bash
# 4. Initialize shadcn/ui
npx shadcn@latest init
```

You'll be prompted for:
- Style (New York / Default)
- Base color (Slate, Gray, Zinc, Neutral, Stone)
- CSS variables for colors (Yes recommended)

### Adding Components

```bash
# Add individual components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input

# Add multiple components
npx shadcn@latest add button card input label

# Add all components (not recommended)
npx shadcn@latest add --all
```

### Project Structure After Setup

```
src/
├── components/
│   └── ui/              # shadcn components live here
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── ...
├── lib/
│   └── utils.ts         # cn() utility function
├── index.css            # Tailwind + CSS variables
└── App.tsx
```

---

## Theming & CSS Variables

### Default CSS Variables

shadcn/ui uses a `background`/`foreground` naming convention:

```css
/* src/index.css */
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.965 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.965 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.965 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.556 0 0);
}
```

### Custom Color Themes

```css
:root {
  /* Blue theme */
  --primary: oklch(0.546 0.245 262.881);
  --primary-foreground: oklch(0.985 0 0);

  /* Or use any color palette */
  --primary: oklch(0.637 0.237 25.331);  /* Orange */
  --primary: oklch(0.723 0.219 149.579); /* Green */
  --primary: oklch(0.606 0.25 292.717);  /* Purple */
}
```

### Dark Mode Toggle

```tsx
// hooks/useTheme.ts
import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
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
    const resolvedTheme = theme === 'system' ? (systemDark ? 'dark' : 'light') : theme;
    root.classList.add(resolvedTheme);

    localStorage.setItem('theme', theme);
  }, [theme]);

  return { theme, setTheme };
}

// components/ThemeToggle.tsx
import { Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/useTheme';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
```

---

## Core Components

### Button

```bash
npx shadcn@latest add button
```

```tsx
import { Button } from '@/components/ui/button';

// Variants
<Button>Default</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>
<Button size="icon"><PlusIcon /></Button>

// States
<Button disabled>Disabled</Button>
<Button className="w-full">Full Width</Button>

// With icon
<Button>
  <Mail className="mr-2 h-4 w-4" />
  Login with Email
</Button>

// Loading state
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Please wait
</Button>

// As child (render as different element)
<Button asChild>
  <a href="/login">Login</a>
</Button>
```

### Input

```bash
npx shadcn@latest add input label
```

```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

// Basic
<Input type="email" placeholder="Email" />

// With label
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="email">Email</Label>
  <Input type="email" id="email" placeholder="Email" />
</div>

// With helper text
<div className="grid w-full max-w-sm items-center gap-1.5">
  <Label htmlFor="email">Email</Label>
  <Input type="email" id="email" placeholder="Email" />
  <p className="text-sm text-muted-foreground">
    Enter your email address.
  </p>
</div>

// File input
<Input type="file" />

// Disabled
<Input disabled placeholder="Disabled" />
```

### Textarea

```bash
npx shadcn@latest add textarea
```

```tsx
import { Textarea } from '@/components/ui/textarea';

<Textarea placeholder="Type your message here." />

// With label
<div className="grid w-full gap-1.5">
  <Label htmlFor="message">Your message</Label>
  <Textarea id="message" placeholder="Type your message here." />
</div>
```

### Select

```bash
npx shadcn@latest add select
```

```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Select a fruit" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="apple">Apple</SelectItem>
    <SelectItem value="banana">Banana</SelectItem>
    <SelectItem value="orange">Orange</SelectItem>
  </SelectContent>
</Select>

// With groups
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select..." />
  </SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectLabel>Fruits</SelectLabel>
      <SelectItem value="apple">Apple</SelectItem>
      <SelectItem value="banana">Banana</SelectItem>
    </SelectGroup>
    <SelectSeparator />
    <SelectGroup>
      <SelectLabel>Vegetables</SelectLabel>
      <SelectItem value="carrot">Carrot</SelectItem>
      <SelectItem value="potato">Potato</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>
```

### Checkbox

```bash
npx shadcn@latest add checkbox
```

```tsx
import { Checkbox } from '@/components/ui/checkbox';

// Basic
<Checkbox id="terms" />

// With label
<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Accept terms and conditions</Label>
</div>

// Controlled
const [checked, setChecked] = useState(false);
<Checkbox checked={checked} onCheckedChange={setChecked} />
```

### Switch

```bash
npx shadcn@latest add switch
```

```tsx
import { Switch } from '@/components/ui/switch';

// Basic
<Switch />

// With label
<div className="flex items-center space-x-2">
  <Switch id="airplane-mode" />
  <Label htmlFor="airplane-mode">Airplane Mode</Label>
</div>

// Controlled
const [enabled, setEnabled] = useState(false);
<Switch checked={enabled} onCheckedChange={setEnabled} />
```

### Radio Group

```bash
npx shadcn@latest add radio-group
```

```tsx
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

<RadioGroup defaultValue="option-one">
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-one" id="option-one" />
    <Label htmlFor="option-one">Option One</Label>
  </div>
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-two" id="option-two" />
    <Label htmlFor="option-two">Option Two</Label>
  </div>
</RadioGroup>
```

---

## Form Components

### Complete Form with React Hook Form + Zod

```bash
npx shadcn@latest add form input button
npm install react-hook-form zod @hookform/resolvers
```

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';

const formSchema = z.object({
  username: z.string().min(2, 'Username must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
});

type FormValues = z.infer<typeof formSchema>;

export function ProfileForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      email: '',
    },
  });

  function onSubmit(values: FormValues) {
    console.log(values);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="johndoe" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
```

### Form with Select

```tsx
<FormField
  control={form.control}
  name="role"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Role</FormLabel>
      <Select onValueChange={field.onChange} defaultValue={field.value}>
        <FormControl>
          <SelectTrigger>
            <SelectValue placeholder="Select a role" />
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem value="admin">Admin</SelectItem>
          <SelectItem value="user">User</SelectItem>
          <SelectItem value="guest">Guest</SelectItem>
        </SelectContent>
      </Select>
      <FormMessage />
    </FormItem>
  )}
/>
```

### Form with Checkbox

```tsx
<FormField
  control={form.control}
  name="terms"
  render={({ field }) => (
    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
      <FormControl>
        <Checkbox
          checked={field.value}
          onCheckedChange={field.onChange}
        />
      </FormControl>
      <div className="space-y-1 leading-none">
        <FormLabel>Accept terms and conditions</FormLabel>
        <FormDescription>
          You agree to our Terms of Service and Privacy Policy.
        </FormDescription>
      </div>
    </FormItem>
  )}
/>
```

---

## Data Display

### Card

```bash
npx shadcn@latest add card
```

```tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card Content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

// Notification card example
<Card>
  <CardHeader className="pb-3">
    <CardTitle>Notifications</CardTitle>
    <CardDescription>You have 3 unread messages.</CardDescription>
  </CardHeader>
  <CardContent className="grid gap-4">
    {notifications.map((notification) => (
      <div key={notification.id} className="flex items-start gap-4">
        <BellIcon className="h-5 w-5 text-muted-foreground" />
        <div className="space-y-1">
          <p className="text-sm font-medium">{notification.title}</p>
          <p className="text-sm text-muted-foreground">
            {notification.description}
          </p>
        </div>
      </div>
    ))}
  </CardContent>
  <CardFooter>
    <Button className="w-full">Mark all as read</Button>
  </CardFooter>
</Card>
```

### Badge

```bash
npx shadcn@latest add badge
```

```tsx
import { Badge } from '@/components/ui/badge';

<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>

// Custom colors (extend in badge.tsx)
<Badge className="bg-green-500 hover:bg-green-600">Success</Badge>
<Badge className="bg-yellow-500 hover:bg-yellow-600">Warning</Badge>
```

### Avatar

```bash
npx shadcn@latest add avatar
```

```tsx
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>

// Sizes (use className)
<Avatar className="h-8 w-8">
  <AvatarImage src="/avatar.png" />
  <AvatarFallback>SM</AvatarFallback>
</Avatar>

<Avatar className="h-16 w-16">
  <AvatarImage src="/avatar.png" />
  <AvatarFallback className="text-lg">LG</AvatarFallback>
</Avatar>

// Avatar group
<div className="flex -space-x-4">
  {users.map((user) => (
    <Avatar key={user.id} className="border-2 border-background">
      <AvatarImage src={user.image} />
      <AvatarFallback>{user.initials}</AvatarFallback>
    </Avatar>
  ))}
</div>
```

### Table

```bash
npx shadcn@latest add table
```

```tsx
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

<Table>
  <TableCaption>A list of recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead className="w-[100px]">Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Method</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {invoices.map((invoice) => (
      <TableRow key={invoice.id}>
        <TableCell className="font-medium">{invoice.id}</TableCell>
        <TableCell>{invoice.status}</TableCell>
        <TableCell>{invoice.method}</TableCell>
        <TableCell className="text-right">{invoice.amount}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Skeleton

```bash
npx shadcn@latest add skeleton
```

```tsx
import { Skeleton } from '@/components/ui/skeleton';

// Basic shapes
<Skeleton className="h-4 w-[250px]" />
<Skeleton className="h-4 w-[200px]" />
<Skeleton className="h-12 w-12 rounded-full" />

// Card skeleton
<div className="flex flex-col space-y-3">
  <Skeleton className="h-[125px] w-[250px] rounded-xl" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>

// User row skeleton
<div className="flex items-center space-x-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

---

## Feedback Components

### Alert

```bash
npx shadcn@latest add alert
```

```tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from 'lucide-react';

// Default
<Alert>
  <Info className="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components to your app using the CLI.
  </AlertDescription>
</Alert>

// Destructive
<Alert variant="destructive">
  <AlertCircle className="h-4 w-4" />
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired. Please log in again.
  </AlertDescription>
</Alert>

// Success (custom styling)
<Alert className="border-green-500 text-green-700 [&>svg]:text-green-500">
  <CheckCircle2 className="h-4 w-4" />
  <AlertTitle>Success!</AlertTitle>
  <AlertDescription>Your changes have been saved.</AlertDescription>
</Alert>

// Warning
<Alert className="border-yellow-500 text-yellow-700 [&>svg]:text-yellow-500">
  <AlertTriangle className="h-4 w-4" />
  <AlertTitle>Warning</AlertTitle>
  <AlertDescription>This action cannot be undone.</AlertDescription>
</Alert>
```

### Toast (Sonner)

```bash
npx shadcn@latest add sonner
```

```tsx
// Add Toaster to your app root
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <>
      <MainContent />
      <Toaster />
    </>
  );
}

// Usage anywhere
import { toast } from 'sonner';

// Basic
toast('Event has been created');

// With description
toast('Event has been created', {
  description: 'Sunday, December 03, 2023 at 9:00 AM',
});

// Success
toast.success('Successfully saved!');

// Error
toast.error('Something went wrong');

// Warning
toast.warning('Please review your input');

// With action
toast('Event created', {
  action: {
    label: 'Undo',
    onClick: () => console.log('Undo'),
  },
});

// Promise toast
toast.promise(saveData(), {
  loading: 'Saving...',
  success: 'Saved successfully!',
  error: 'Failed to save',
});

// Custom duration
toast('Message', { duration: 5000 });

// Dismissible
const toastId = toast('Loading...');
toast.dismiss(toastId);
```

### Progress

```bash
npx shadcn@latest add progress
```

```tsx
import { Progress } from '@/components/ui/progress';

<Progress value={33} />

// Animated progress
const [progress, setProgress] = useState(0);

useEffect(() => {
  const timer = setInterval(() => {
    setProgress((prev) => (prev >= 100 ? 0 : prev + 10));
  }, 500);
  return () => clearInterval(timer);
}, []);

<Progress value={progress} />
```

---

## Overlay Components

### Dialog

```bash
npx shadcn@latest add dialog
```

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">Edit Profile</Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[425px]">
    <DialogHeader>
      <DialogTitle>Edit profile</DialogTitle>
      <DialogDescription>
        Make changes to your profile here. Click save when you're done.
      </DialogDescription>
    </DialogHeader>
    <div className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="name" className="text-right">Name</Label>
        <Input id="name" defaultValue="John Doe" className="col-span-3" />
      </div>
    </div>
    <DialogFooter>
      <DialogClose asChild>
        <Button variant="outline">Cancel</Button>
      </DialogClose>
      <Button type="submit">Save changes</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

// Controlled dialog
const [open, setOpen] = useState(false);

<Dialog open={open} onOpenChange={setOpen}>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Controlled Dialog</DialogTitle>
    </DialogHeader>
    <Button onClick={() => setOpen(false)}>Close</Button>
  </DialogContent>
</Dialog>
```

### Sheet (Slide-out Panel)

```bash
npx shadcn@latest add sheet
```

```tsx
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
  SheetClose,
} from '@/components/ui/sheet';

// Right side (default)
<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open</Button>
  </SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Edit profile</SheetTitle>
      <SheetDescription>
        Make changes to your profile here.
      </SheetDescription>
    </SheetHeader>
    <div className="py-4">
      {/* Content */}
    </div>
    <SheetFooter>
      <SheetClose asChild>
        <Button type="submit">Save changes</Button>
      </SheetClose>
    </SheetFooter>
  </SheetContent>
</Sheet>

// Different sides
<SheetContent side="left">Left panel</SheetContent>
<SheetContent side="top">Top panel</SheetContent>
<SheetContent side="bottom">Bottom panel</SheetContent>

// Mobile navigation example
<Sheet>
  <SheetTrigger asChild>
    <Button variant="ghost" size="icon" className="md:hidden">
      <Menu className="h-5 w-5" />
    </Button>
  </SheetTrigger>
  <SheetContent side="left" className="w-[300px]">
    <nav className="flex flex-col gap-4">
      <a href="/">Home</a>
      <a href="/about">About</a>
      <a href="/contact">Contact</a>
    </nav>
  </SheetContent>
</Sheet>
```

### Drawer (Mobile-friendly)

```bash
npx shadcn@latest add drawer
```

```tsx
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer';

<Drawer>
  <DrawerTrigger asChild>
    <Button variant="outline">Open Drawer</Button>
  </DrawerTrigger>
  <DrawerContent>
    <div className="mx-auto w-full max-w-sm">
      <DrawerHeader>
        <DrawerTitle>Move Goal</DrawerTitle>
        <DrawerDescription>Set your daily activity goal.</DrawerDescription>
      </DrawerHeader>
      <div className="p-4">
        {/* Content */}
      </div>
      <DrawerFooter>
        <Button>Submit</Button>
        <DrawerClose asChild>
          <Button variant="outline">Cancel</Button>
        </DrawerClose>
      </DrawerFooter>
    </div>
  </DrawerContent>
</Drawer>
```

### Responsive Dialog/Drawer Pattern

```tsx
import { useMediaQuery } from '@/hooks/useMediaQuery';

function ResponsiveModal({ children, ...props }) {
  const isDesktop = useMediaQuery('(min-width: 768px)');

  if (isDesktop) {
    return (
      <Dialog {...props}>
        <DialogContent>{children}</DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer {...props}>
      <DrawerContent>{children}</DrawerContent>
    </Drawer>
  );
}
```

### Alert Dialog (Confirmation)

```bash
npx shadcn@latest add alert-dialog
```

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

<AlertDialog>
  <AlertDialogTrigger asChild>
    <Button variant="destructive">Delete</Button>
  </AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone. This will permanently delete your
        account and remove your data from our servers.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction onClick={handleDelete}>
        Delete
      </AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

### Popover

```bash
npx shadcn@latest add popover
```

```tsx
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">Open popover</Button>
  </PopoverTrigger>
  <PopoverContent className="w-80">
    <div className="grid gap-4">
      <div className="space-y-2">
        <h4 className="font-medium leading-none">Dimensions</h4>
        <p className="text-sm text-muted-foreground">
          Set the dimensions for the layer.
        </p>
      </div>
      <div className="grid gap-2">
        <div className="grid grid-cols-3 items-center gap-4">
          <Label htmlFor="width">Width</Label>
          <Input id="width" defaultValue="100%" className="col-span-2 h-8" />
        </div>
      </div>
    </div>
  </PopoverContent>
</Popover>
```

### Tooltip

```bash
npx shadcn@latest add tooltip
```

```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

// Wrap app with TooltipProvider
<TooltipProvider>
  <App />
</TooltipProvider>

// Usage
<Tooltip>
  <TooltipTrigger asChild>
    <Button variant="outline" size="icon">
      <PlusIcon className="h-4 w-4" />
    </Button>
  </TooltipTrigger>
  <TooltipContent>
    <p>Add to library</p>
  </TooltipContent>
</Tooltip>

// Different sides
<TooltipContent side="right">Right tooltip</TooltipContent>
<TooltipContent side="bottom">Bottom tooltip</TooltipContent>
```

---

## Navigation Components

### Tabs

```bash
npx shadcn@latest add tabs
```

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

<Tabs defaultValue="account" className="w-[400px]">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    <Card>
      <CardHeader>
        <CardTitle>Account</CardTitle>
        <CardDescription>
          Make changes to your account here.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Account form */}
      </CardContent>
    </Card>
  </TabsContent>
  <TabsContent value="password">
    <Card>
      <CardHeader>
        <CardTitle>Password</CardTitle>
        <CardDescription>
          Change your password here.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Password form */}
      </CardContent>
    </Card>
  </TabsContent>
</Tabs>

// Controlled tabs
const [tab, setTab] = useState('account');
<Tabs value={tab} onValueChange={setTab}>
```

### Dropdown Menu

```bash
npx shadcn@latest add dropdown-menu
```

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '@/components/ui/dropdown-menu';

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent className="w-56">
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>
      <User className="mr-2 h-4 w-4" />
      <span>Profile</span>
      <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
    </DropdownMenuItem>
    <DropdownMenuItem>
      <Settings className="mr-2 h-4 w-4" />
      <span>Settings</span>
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem className="text-red-600">
      <LogOut className="mr-2 h-4 w-4" />
      <span>Log out</span>
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>

// With checkbox items
<DropdownMenuCheckboxItem
  checked={showStatusBar}
  onCheckedChange={setShowStatusBar}
>
  Status Bar
</DropdownMenuCheckboxItem>

// With radio items
<DropdownMenuRadioGroup value={position} onValueChange={setPosition}>
  <DropdownMenuRadioItem value="top">Top</DropdownMenuRadioItem>
  <DropdownMenuRadioItem value="bottom">Bottom</DropdownMenuRadioItem>
</DropdownMenuRadioGroup>

// With submenu
<DropdownMenuSub>
  <DropdownMenuSubTrigger>
    <UserPlus className="mr-2 h-4 w-4" />
    <span>Invite users</span>
  </DropdownMenuSubTrigger>
  <DropdownMenuSubContent>
    <DropdownMenuItem>Email</DropdownMenuItem>
    <DropdownMenuItem>Message</DropdownMenuItem>
  </DropdownMenuSubContent>
</DropdownMenuSub>
```

### Command (Command Palette)

```bash
npx shadcn@latest add command
```

```tsx
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';

// Inline command
<Command className="rounded-lg border shadow-md">
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>
        <Calendar className="mr-2 h-4 w-4" />
        <span>Calendar</span>
      </CommandItem>
      <CommandItem>
        <Smile className="mr-2 h-4 w-4" />
        <span>Search Emoji</span>
      </CommandItem>
    </CommandGroup>
    <CommandSeparator />
    <CommandGroup heading="Settings">
      <CommandItem>
        <User className="mr-2 h-4 w-4" />
        <span>Profile</span>
        <CommandShortcut>⌘P</CommandShortcut>
      </CommandItem>
    </CommandGroup>
  </CommandList>
</Command>

// Command dialog (⌘K style)
const [open, setOpen] = useState(false);

useEffect(() => {
  const down = (e: KeyboardEvent) => {
    if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((open) => !open);
    }
  };
  document.addEventListener('keydown', down);
  return () => document.removeEventListener('keydown', down);
}, []);

<CommandDialog open={open} onOpenChange={setOpen}>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Actions">
      <CommandItem onSelect={() => { /* action */ setOpen(false); }}>
        <Plus className="mr-2 h-4 w-4" />
        Create new...
      </CommandItem>
    </CommandGroup>
  </CommandList>
</CommandDialog>
```

### Breadcrumb

```bash
npx shadcn@latest add breadcrumb
```

```tsx
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/products">Products</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Current Page</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Pagination

```bash
npx shadcn@latest add pagination
```

```tsx
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#" isActive>2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">3</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

---

## Layout Components

### Separator

```bash
npx shadcn@latest add separator
```

```tsx
import { Separator } from '@/components/ui/separator';

<div>
  <h4 className="text-sm font-medium">Radix Primitives</h4>
  <p className="text-sm text-muted-foreground">
    An open-source UI component library.
  </p>
</div>
<Separator className="my-4" />
<div className="flex h-5 items-center space-x-4 text-sm">
  <div>Blog</div>
  <Separator orientation="vertical" />
  <div>Docs</div>
  <Separator orientation="vertical" />
  <div>Source</div>
</div>
```

### Scroll Area

```bash
npx shadcn@latest add scroll-area
```

```tsx
import { ScrollArea } from '@/components/ui/scroll-area';

<ScrollArea className="h-72 w-48 rounded-md border">
  <div className="p-4">
    <h4 className="mb-4 text-sm font-medium leading-none">Tags</h4>
    {tags.map((tag) => (
      <div key={tag} className="text-sm">{tag}</div>
    ))}
  </div>
</ScrollArea>

// Horizontal scroll
<ScrollArea className="w-96 whitespace-nowrap rounded-md border">
  <div className="flex w-max space-x-4 p-4">
    {items.map((item) => (
      <div key={item} className="w-[150px] shrink-0">{item}</div>
    ))}
  </div>
  <ScrollBar orientation="horizontal" />
</ScrollArea>
```

### Aspect Ratio

```bash
npx shadcn@latest add aspect-ratio
```

```tsx
import { AspectRatio } from '@/components/ui/aspect-ratio';

<div className="w-[450px]">
  <AspectRatio ratio={16 / 9}>
    <img
      src="https://images.unsplash.com/photo.jpg"
      alt="Photo"
      className="rounded-md object-cover w-full h-full"
    />
  </AspectRatio>
</div>

// Square
<AspectRatio ratio={1 / 1}>
  <img src="..." className="object-cover w-full h-full" />
</AspectRatio>
```

### Collapsible

```bash
npx shadcn@latest add collapsible
```

```tsx
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

const [isOpen, setIsOpen] = useState(false);

<Collapsible open={isOpen} onOpenChange={setIsOpen}>
  <div className="flex items-center justify-between space-x-4">
    <h4 className="text-sm font-semibold">@peduarte starred 3 repositories</h4>
    <CollapsibleTrigger asChild>
      <Button variant="ghost" size="sm">
        <ChevronsUpDown className="h-4 w-4" />
      </Button>
    </CollapsibleTrigger>
  </div>
  <div className="rounded-md border px-4 py-2 text-sm">@radix-ui/primitives</div>
  <CollapsibleContent className="space-y-2">
    <div className="rounded-md border px-4 py-2 text-sm">@radix-ui/colors</div>
    <div className="rounded-md border px-4 py-2 text-sm">@stitches/react</div>
  </CollapsibleContent>
</Collapsible>
```

### Accordion

```bash
npx shadcn@latest add accordion
```

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>
      Yes. It comes with default styles that match your theme.
    </AccordionContent>
  </AccordionItem>
</Accordion>

// Multiple open
<Accordion type="multiple" defaultValue={['item-1']}>
```

---

## Form Handling with React Hook Form

### Complete Registration Form

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';

const formSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirmPassword: z.string(),
  role: z.enum(['user', 'admin', 'moderator']),
  terms: z.boolean().refine(val => val === true, 'You must accept the terms'),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type FormValues = z.infer<typeof formSchema>;

export function RegistrationForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'user',
      terms: false,
    },
  });

  async function onSubmit(values: FormValues) {
    try {
      await registerUser(values);
      toast.success('Account created successfully!');
    } catch (error) {
      toast.error('Failed to create account');
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="firstName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input placeholder="John" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="lastName"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last Name</FormLabel>
                <FormControl>
                  <Input placeholder="Doe" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="moderator">Moderator</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="terms"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>
                  I agree to the terms and conditions
                </FormLabel>
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? 'Creating account...' : 'Sign up'}
        </Button>
      </form>
    </Form>
  );
}
```

---

## Data Tables

### Basic Data Table with TanStack Table

```bash
npx shadcn@latest add table
npm install @tanstack/react-table
```

```tsx
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  getFilteredRowModel,
  ColumnFiltersState,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
}

const columns: ColumnDef<User>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Name
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  {
    accessorKey: 'email',
    header: 'Email',
  },
  {
    accessorKey: 'role',
    header: 'Role',
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('status') as string;
      return (
        <Badge variant={status === 'active' ? 'default' : 'secondary'}>
          {status}
        </Badge>
      );
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => navigator.clipboard.writeText(row.original.id)}>
            Copy ID
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Edit</DropdownMenuItem>
          <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
  },
];

export function DataTable({ data }: { data: User[] }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    state: {
      sorting,
      columnFilters,
    },
  });

  return (
    <div className="space-y-4">
      {/* Filter */}
      <Input
        placeholder="Filter by name..."
        value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
        onChange={(e) => table.getColumn('name')?.setFilterValue(e.target.value)}
        className="max-w-sm"
      />

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Page {table.getState().pagination.pageIndex + 1} of{' '}
          {table.getPageCount()}
        </p>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

## Patterns & Recipes

### Login Page

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';

export function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>Sign in to your account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="name@example.com" />
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
              <a href="#" className="text-sm text-primary hover:underline">
                Forgot password?
              </a>
            </div>
            <Input id="password" type="password" />
          </div>
          <Button className="w-full">Sign in</Button>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <Separator />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button variant="outline">
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">...</svg>
              Google
            </Button>
            <Button variant="outline">
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">...</svg>
              GitHub
            </Button>
          </div>

          <p className="text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <a href="#" className="text-primary hover:underline">
              Sign up
            </a>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Settings Page with Tabs

```tsx
export function SettingsPage() {
  return (
    <div className="container max-w-4xl py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings</p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>
                This is how others will see you on the site.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-4">
                <Avatar className="h-20 w-20">
                  <AvatarImage src="/avatar.png" />
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
                <Button variant="outline">Change avatar</Button>
              </div>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Display name</Label>
                  <Input id="name" defaultValue="John Doe" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea id="bio" placeholder="Tell us about yourself" />
                </div>
              </div>
              <Button>Save changes</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other tab contents... */}
      </Tabs>
    </div>
  );
}
```

### Empty State

```tsx
function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mt-2">
        {description}
      </p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

// Usage
<EmptyState
  icon={FileText}
  title="No documents"
  description="Get started by creating your first document."
  action={<Button>Create document</Button>}
/>
```

### Loading States

```tsx
// Button loading
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Loading...
</Button>

// Page loading
function PageLoading() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
    </div>
  );
}

// Skeleton loading for cards
function CardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-5 w-[200px]" />
        <Skeleton className="h-4 w-[300px]" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-[200px] w-full" />
      </CardContent>
    </Card>
  );
}
```

---

## Best Practices

### 1. Component Customization

```tsx
// Extend existing components with custom variants
// In components/ui/button.tsx, add new variants:

const buttonVariants = cva(
  // ... existing base styles
  {
    variants: {
      variant: {
        // ... existing variants
        success: 'bg-green-600 text-white hover:bg-green-700',
        warning: 'bg-yellow-500 text-white hover:bg-yellow-600',
      },
    },
  }
);
```

### 2. Consistent Spacing

```tsx
// Use consistent spacing patterns
<Card>
  <CardHeader>...</CardHeader>
  <CardContent className="space-y-4">
    {/* Vertical spacing between items */}
  </CardContent>
  <CardFooter className="flex justify-between">
    {/* Horizontal layout */}
  </CardFooter>
</Card>
```

### 3. Accessibility

```tsx
// Always include proper labels
<Label htmlFor="email">Email</Label>
<Input id="email" type="email" aria-describedby="email-description" />
<p id="email-description" className="text-sm text-muted-foreground">
  We'll never share your email.
</p>

// Use sr-only for icon-only buttons
<Button size="icon" variant="ghost">
  <Settings className="h-4 w-4" />
  <span className="sr-only">Settings</span>
</Button>
```

### 4. Responsive Overlays

```tsx
// Use Sheet on mobile, Dialog on desktop
function ResponsiveDialog({ children }) {
  const isDesktop = useMediaQuery('(min-width: 768px)');

  if (isDesktop) {
    return <Dialog>{children}</Dialog>;
  }

  return (
    <Drawer>
      <DrawerContent>{children}</DrawerContent>
    </Drawer>
  );
}
```

### 5. Form Organization

```tsx
// Group related fields
<div className="grid grid-cols-2 gap-4">
  <FormField name="firstName" ... />
  <FormField name="lastName" ... />
</div>

// Use sections for long forms
<div className="space-y-8">
  <section>
    <h3 className="text-lg font-medium mb-4">Personal Information</h3>
    {/* Personal fields */}
  </section>
  <Separator />
  <section>
    <h3 className="text-lg font-medium mb-4">Contact Details</h3>
    {/* Contact fields */}
  </section>
</div>
```

---

## Component Reference

### Quick Import Guide

| Component | Install Command | Key Exports |
|-----------|-----------------|-------------|
| Button | `npx shadcn@latest add button` | `Button`, `buttonVariants` |
| Input | `npx shadcn@latest add input` | `Input` |
| Label | `npx shadcn@latest add label` | `Label` |
| Select | `npx shadcn@latest add select` | `Select`, `SelectTrigger`, `SelectValue`, `SelectContent`, `SelectItem` |
| Checkbox | `npx shadcn@latest add checkbox` | `Checkbox` |
| Switch | `npx shadcn@latest add switch` | `Switch` |
| Card | `npx shadcn@latest add card` | `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter` |
| Dialog | `npx shadcn@latest add dialog` | `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter` |
| Sheet | `npx shadcn@latest add sheet` | `Sheet`, `SheetTrigger`, `SheetContent`, `SheetHeader`, `SheetTitle` |
| Drawer | `npx shadcn@latest add drawer` | `Drawer`, `DrawerTrigger`, `DrawerContent`, `DrawerHeader`, `DrawerTitle` |
| Dropdown | `npx shadcn@latest add dropdown-menu` | `DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem` |
| Tabs | `npx shadcn@latest add tabs` | `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` |
| Table | `npx shadcn@latest add table` | `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell` |
| Form | `npx shadcn@latest add form` | `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage` |
| Toast | `npx shadcn@latest add sonner` | `Toaster`, `toast` |
| Alert | `npx shadcn@latest add alert` | `Alert`, `AlertTitle`, `AlertDescription` |
| Badge | `npx shadcn@latest add badge` | `Badge` |
| Avatar | `npx shadcn@latest add avatar` | `Avatar`, `AvatarImage`, `AvatarFallback` |
| Skeleton | `npx shadcn@latest add skeleton` | `Skeleton` |
| Separator | `npx shadcn@latest add separator` | `Separator` |
| Tooltip | `npx shadcn@latest add tooltip` | `Tooltip`, `TooltipTrigger`, `TooltipContent`, `TooltipProvider` |
| Popover | `npx shadcn@latest add popover` | `Popover`, `PopoverTrigger`, `PopoverContent` |
| Command | `npx shadcn@latest add command` | `Command`, `CommandInput`, `CommandList`, `CommandItem`, `CommandDialog` |

### Essential Dependencies

```json
{
  "dependencies": {
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.300.0",
    "@radix-ui/react-*": "various",
    "react-hook-form": "^7.50.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    "@tanstack/react-table": "^8.11.0",
    "sonner": "^1.4.0"
  }
}
```

---

*Last updated: January 2025 | shadcn/ui with Tailwind CSS v4*
