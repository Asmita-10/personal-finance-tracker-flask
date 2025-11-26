# Design Guidelines: Flask Expense Tracker

## Design Approach
**Selected Approach**: Design System-Based (Material Design 3)
**Rationale**: Expense tracking is a data-dense, utility-focused application requiring clear information hierarchy and efficient data entry. Material Design 3 provides excellent patterns for forms, tables, and dashboard layouts while maintaining visual polish.

**Inspiration References**: Mint, YNAB (You Need A Budget), Splitwise for expense management patterns

## Typography System

**Font Family**: 
- Primary: 'Inter' (Google Fonts) - Clean, highly legible for data display
- Monospace: 'JetBrains Mono' for currency amounts

**Hierarchy**:
- Page Headers: text-3xl font-bold (Dashboard, Expenses, Profile)
- Section Headers: text-xl font-semibold
- Card Titles: text-lg font-medium
- Body Text: text-base font-normal
- Labels/Metadata: text-sm font-medium
- Currency Amounts: text-2xl font-bold (monospace for alignment)
- Table Headers: text-xs font-semibold uppercase tracking-wide

## Layout System

**Spacing Primitives**: Tailwind units of 2, 4, 6, and 8 (p-2, m-4, gap-6, py-8)

**Structure**:
- Two-column layout: Sidebar (w-64) + Main content (flex-1)
- Sidebar: Fixed navigation, always visible on desktop, collapsible on mobile
- Main content: max-w-7xl mx-auto px-6 py-8
- Cards/Panels: Rounded corners (rounded-lg), consistent padding (p-6)
- Forms: max-w-2xl for optimal readability

**Grid Systems**:
- Expense cards: grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6
- Dashboard stats: grid-cols-2 md:grid-cols-4 gap-4
- Mobile: Always single column, stack elements vertically

## Component Library

### Navigation
**Sidebar Navigation**:
- Logo/app name at top (h-16 flex items-center px-4)
- Navigation links: py-3 px-4, rounded-md, with left-aligned icons (w-5 h-5)
- Active state: Distinct treatment with left border indicator
- User profile section at bottom with avatar, name, logout button

### Dashboard Components
**Stats Cards** (4 cards in grid):
- Total expenses this month
- Category breakdown (top 3)
- Recent transactions count
- Average daily spending
- Each card: p-6, icon top-left, large number display, label below

**Expense List Table**:
- Sticky header row with sorting indicators
- Columns: Date | Category | Description | Amount | Actions
- Alternating row treatment for readability
- Row height: py-4, hover state for interactivity
- Mobile: Collapse to card view (each expense as a stacked card)

### Forms
**Add/Edit Expense Form**:
- Organized in single column layout
- Input fields with floating labels pattern
- Amount input: Large, prominent, right-aligned with currency symbol prefix
- Category: Dropdown with icon previews
- Date: Native date picker with calendar icon
- Description: Optional textarea (2-3 rows)
- Action buttons: Primary "Save" + Secondary "Cancel" aligned right
- Field spacing: space-y-6

**Authentication Forms** (Login/Register):
- Centered card layout: max-w-md mx-auto
- Logo/brand at top
- Form fields: space-y-4
- Social divider: "or continue with email"
- Links: "Forgot password?" right-aligned, "Sign up" centered below
- Form width: w-full, max-w-sm

### Data Display
**Category Pills/Tags**:
- Inline badges with category names
- Rounded-full, px-3 py-1, text-xs font-medium
- Icon + label combination

**Amount Display**:
- Monospace font for alignment
- Large sizes (text-2xl) for prominent displays
- Negative/positive indicators where relevant
- Consistent decimal places (2 for currency)

**Empty States**:
- Centered content with icon (w-16 h-16 mx-auto)
- Heading + descriptive text
- Primary CTA button: "Add Your First Expense"

### Buttons & Actions
**Primary Button**: px-6 py-3, rounded-lg, font-medium
**Secondary Button**: px-6 py-3, rounded-lg, border treatment
**Icon Buttons**: p-2, rounded-md (for edit/delete actions)
**Button Groups**: gap-3, flex justify-end

### Overlays
**Modals** (for confirmations, quick add):
- Centered overlay: max-w-lg
- Header with title + close button (×)
- Content padding: p-6
- Footer with action buttons: border-top separator

**Notifications/Toasts**:
- Top-right positioning (fixed top-4 right-4)
- Auto-dismiss after 4 seconds
- Icons for success/error/info states

## Icons
**Library**: Heroicons (via CDN)
**Usage**:
- Navigation: outline style, w-5 h-5
- Actions: outline style, w-4 h-4
- Stats cards: solid style, w-8 h-8
- Empty states: outline style, w-16 h-16

## Responsive Behavior
**Breakpoints**:
- Mobile (base): Single column, stacked navigation (hamburger menu)
- Tablet (md: 768px): Two-column grids, visible sidebar with toggle
- Desktop (lg: 1024px): Full sidebar, three-column grids, expanded tables

**Mobile Optimizations**:
- Tables convert to card lists
- Sidebar becomes slide-out drawer
- Stats grid becomes 2-column instead of 4
- Form inputs: full width with larger touch targets (min-h-12)

## Accessibility
- Form labels always visible (not placeholder-only)
- Focus indicators: 2px ring with offset
- Error messages: text-sm, positioned below fields, with icon
- Keyboard navigation: Tab order follows visual hierarchy
- ARIA labels for icon-only buttons

This design creates a professional, data-focused expense tracker with excellent usability for frequent data entry while maintaining visual clarity for expense analysis.