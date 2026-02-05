# NextJS Todo Advanced UI Reference

This document provides detailed reference information for implementing advanced UI components for NextJS todo applications.

## Component Color Palettes

### Priority Badge Colors

Color specifications for priority badges:

- **High Priority**: `bg-red-500 text-white`
  - Background: `rgb(239, 68, 68)` (Red 500)
  - Text: White for contrast

- **Medium Priority**: `bg-orange-500 text-white`
  - Background: `rgb(249, 115, 22)` (Orange 500)
  - Text: White for contrast

- **Low Priority**: `bg-yellow-500 text-gray-900`
  - Background: `rgb(234, 179, 8)` (Yellow 500)
  - Text: Gray 900 for contrast

### Tag Chip Colors

Color specifications for tag chips:

- **Default Tag**: `bg-blue-100 text-blue-800 border border-blue-200`
  - Background: `rgb(219, 234, 254)` (Blue 100)
  - Text: `rgb(30, 64, 175)` (Blue 800)
  - Border: `rgb(191, 219, 254)` (Blue 200)

## Component Accessibility Guidelines

### ARIA Attributes

Each component should include appropriate ARIA attributes:

#### Priority Badge
```tsx
<span
  className="priority-badge"
  aria-label={`Priority: ${priorityLevel}`}
>
  {priorityLabel}
</span>
```

#### Tag Chips
```tsx
<span
  className="tag-chip"
  aria-label={`Tag: ${tagName}`}
>
  {tagName}
  <button
    type="button"
    className="remove-button"
    onClick={onRemove}
    aria-label={`Remove tag ${tagName}`}
  >
    ×
  </button>
</span>
```

#### Date Picker
```tsx
<Popover>
  <PopoverTrigger asChild>
    <Button
      variant="outline"
      aria-label={date ? `Selected date: ${format(date, 'PPP')}` : 'Pick a date'}
    >
      {date ? format(date, 'PPP') : <span>Pick a date</span>}
    </Button>
  </PopoverTrigger>
  <PopoverContent>
    <Calendar
      mode="single"
      selected={date}
      onSelect={setDate}
      initialFocus
    />
  </PopoverContent>
</Popover>
```

### Keyboard Navigation

Components should be keyboard accessible:

- Use `tabindex="0"` for focusable elements that aren't naturally focusable
- Implement proper focus management for popovers and dropdowns
- Ensure all interactive elements are reachable via Tab key
- Provide visible focus indicators

## Responsive Breakpoints

Use these Tailwind CSS breakpoints for responsive design:

- **Mobile**: `max-width: 640px` (using `sm:` prefix)
- **Tablet**: `max-width: 768px` (using `md:` prefix)
- **Desktop**: `min-width: 1024px` (using `lg:` and `xl:` prefixes)

### Responsive Component Adjustments

#### Date Picker
```tsx
<PopoverContent className="w-auto p-0 sm:w-[300px]">
  <Calendar
    mode="single"
    selected={date}
    onSelect={setDate}
    initialFocus
  />
</PopoverContent>
```

#### Form Layout
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  {/* Form fields arranged differently on mobile vs desktop */}
</div>
```

## Loading and Error States

### Loading States

Components should handle loading states gracefully:

```tsx
const [loading, setLoading] = useState(false);

return (
  <div>
    {loading && (
      <div className="flex items-center">
        <Spinner className="animate-spin h-4 w-4 mr-2" />
        <span>Loading...</span>
      </div>
    )}
    {!loading && (
      // Normal component content
    )}
  </div>
);
```

### Error States

Display errors clearly and accessibly:

```tsx
const [error, setError] = useState<string | null>(null);

return (
  <div>
    {error && (
      <div
        className="rounded-md bg-red-50 p-4 mb-4"
        role="alert"
        aria-live="assertive"
      >
        <div className="flex">
          <div className="flex-shrink-0">
            <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    )}
  </div>
);
```

## Integration with shadcn/ui

### Required shadcn/ui Components

The advanced UI components rely on these shadcn/ui components:

- `Button`: For interactive elements
- `Input`: For text inputs
- `Textarea`: For multi-line text inputs
- `Label`: For form labels
- `Switch`: For toggle switches
- `Select`: For dropdown menus
- `Calendar`: For date picking
- `Popover`: For date picker popup
- `Toast`: For notifications

### Installation Commands

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add label
npx shadcn-ui@latest add switch
npx shadcn-ui@latest add select
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add toast
```

## Dependency Requirements

### Required Packages

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "next": "^14.0.0",
    "tailwindcss": "^3.3.0",
    "date-fns": "^2.30.0",
    "lucide-react": "^0.263.0",
    "@radix-ui/react-switch": "^1.0.0",
    "@radix-ui/react-select": "^1.2.0",
    "@radix-ui/react-popover": "^1.0.0",
    "@radix-ui/react-slot": "^1.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
  }
}
```

## Testing Considerations

### Component Testing

Test components for:
- Visual appearance across different screen sizes
- Accessibility compliance (ARIA attributes, keyboard navigation)
- Proper form submission behavior
- Loading and error state handling
- Interaction with backend APIs

### Responsive Testing

Verify components work on:
- Mobile devices (iPhone SE, Pixel 5, etc.)
- Tablets (iPad, Surface, etc.)
- Desktop browsers at various resolutions
- Different zoom levels (100%, 125%, 150%)

## Performance Optimization

### Lazy Loading

Consider lazy loading complex components:

```tsx
import { lazy, Suspense } from 'react';

const DatePicker = lazy(() => import('@/components/DatePicker'));

return (
  <Suspense fallback={<div>Loading date picker...</div>}>
    <DatePicker date={date} setDate={setDate} />
  </Suspense>
);
```

### Memoization

Use React.memo for components that render frequently:

```tsx
const TagChips = React.memo(({ tags, onRemove }: TagChipsProps) => {
  // Component implementation
});
```
