# Vocabloom UX Design Specification

## Color Palette

### Primary Brand Colors

Our primary colors establish Vocabloom's visual identity and create emotional connections:

- **Primary Blue** (`#6690ff`): Represents trust, intelligence, and learning. Used for primary actions and key interface elements
- **Primary Orange** (`#e19f5d`): Conveys warmth, creativity, and energy. Used for secondary accents and highlights
- **Primary Yellow** (`#f2cd4a`): Symbolizes optimism and achievement. Used for special elements and positive reinforcement

### Semantic Color System

Colors that provide immediate visual feedback and guide user behavior:

- **Success Green** (`#4ade80`): Instills confidence and positive reinforcement for completed actions
- **Error Red** (`#f87171`): Clearly communicates issues and requires immediate attention
- **Warning Amber** (`#fbbf24`): Alerts users to important information without causing alarm
- **Info Cyan** (`#38bdf8`): Provides helpful guidance and educational content

### Supporting Colors

Colors that enhance the user experience and add visual interest:

- **Premium Purple** (`#a78bfa`): Indicates special features and premium content
- **Accent Pink** (`#f472b6`): Adds personality and highlights special moments

### Background System

Background colors create visual hierarchy and reduce cognitive load:

- **Background Primary** (`#f8fafc`): Creates a calm, focused learning environment
- **Background Surface** (`#ffffff`): Provides clear content separation and readability

### Typography Colors

Text colors optimize reading experience and information hierarchy:

- **Text Primary** (`#1e293b`): Ensures maximum readability for important content
- **Text Secondary** (`#64748b`): Provides comfortable reading for supporting information

### Interface Elements

Colors that define boundaries and create structure:

- **Border Color** (`#e2e8f0`): Provides subtle definition without visual noise
- **Blue Hover** (`#4a7aff`): Offers clear feedback for interactive elements

### Dark Mode Support

Dark mode provides an alternative viewing experience that:
- Reduces eye strain in low-light environments
- Maintains the same emotional and functional color associations
- Preserves accessibility and readability standards

**Dark Mode Colors:**
- **Background Primary**: `#0f172a`
- **Background Surface**: `#1e293b`
- **Text Primary**: `#e2e8f0`
- **Text Secondary**: `#cbd5e1`
- **Border Color**: `#334155`
- **Blue Hover**: `#6366f1`

## Design System

### Typography Scale

Consistent typography hierarchy ensures readability and visual hierarchy:

- **Heading 1** (`h1`): `2rem` (32px), `font-weight: 700`
- **Heading 2** (`h2`): `1.5rem` (24px), `font-weight: 600`
- **Heading 3** (`h3`): `1.25rem` (20px), `font-weight: 600`
- **Body Large** (`.text-lg`): `1.125rem` (18px), `font-weight: 500`
- **Body** (`.text-base`): `1rem` (16px), `font-weight: 400`
- **Body Small** (`.text-sm`): `0.875rem` (14px), `font-weight: 400`
- **Caption** (`.text-xs`): `0.75rem` (12px), `font-weight: 500`

### Spacing Scale

Consistent spacing creates visual rhythm and improves readability:

- **4px** (0.25rem): Minimal spacing for tight layouts
- **8px** (0.5rem): Small spacing for related elements
- **12px** (0.75rem): Medium spacing for grouped elements
- **16px** (1rem): Standard spacing for content sections
- **24px** (1.5rem): Large spacing for major sections
- **32px** (2rem): Extra large spacing for page sections
- **48px** (3rem): Maximum spacing for page-level separation

### Border Radius Scale

Consistent border radius creates visual harmony:

- **4px** (0.25rem): Small radius for buttons and inputs
- **6px** (0.375rem): Medium radius for cards and badges
- **8px** (0.5rem): Large radius for modals and major containers
- **12px** (0.75rem): Extra large radius for special elements

### Shadow System

Consistent shadows create depth and hierarchy:

- **Shadow Small**: `0 1px 2px rgba(0, 0, 0, 0.05)`
- **Shadow Medium**: `0 4px 6px rgba(0, 0, 0, 0.1)`
- **Shadow Large**: `0 10px 15px rgba(0, 0, 0, 0.1)`
- **Shadow Extra Large**: `0 20px 25px rgba(0, 0, 0, 0.15)`

## Component Design System

### Modal System

All modals follow a consistent structure and styling:

**Base Classes:**
- `.modal-overlay`: Full-screen overlay with backdrop blur
- `.modal-content`: Centered modal container with shadow
- `.modal-header`: Header with title and close button
- `.modal-body`: Main content area
- `.modal-footer`: Footer with action buttons

**Styling:**
- Overlay: `background: rgba(0, 0, 0, 0.5)`, `backdrop-filter: blur(4px)`
- Content: `background: var(--bg-surface)`, `border-radius: 8px`, `shadow: shadow-large`
- Header: `padding: 24px 24px 16px`, `border-bottom: 1px solid var(--border-color)`
- Body: `padding: 16px 24px`
- Footer: `padding: 16px 24px 24px`, `border-top: 1px solid var(--border-color)`

### Badge System

Unified badge system for consistent information display:

**Base Badge Class:**
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
}
```

**Badge Variants:**
- **Language Badge** (`.badge--language`): `background: var(--primary-blue)`, `color: white`
- **Age Badge** (`.badge--age`): `background: var(--info-cyan)`, `color: white`
- **Content Type Badge** (`.badge--content-type`): `background: var(--premium-purple)`, `color: white`
- **Theme Badge** (`.badge--theme`): `background: var(--primary-orange)`, `color: white`
- **Status Badge** (`.badge--status`): Semantic colors based on state
  - Success: `background: var(--success-green)`, `color: white`
  - Warning: `background: var(--warning-amber)`, `color: #92400e`
  - Error: `background: var(--error-red)`, `color: white`

### Button System

Consistent button hierarchy and styling:

**Base Button Class:**
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}
```

**Button Variants:**
- **Primary Button** (`.btn--primary`): `background: var(--primary-blue)`, `color: white`
- **Secondary Button** (`.btn--secondary`): `background: transparent`, `color: var(--text-primary)`, `border: 1px solid var(--border-color)`
- **Google Button** (`.btn--google`): Google's standard styling with icon
- **Icon Button** (`.btn--icon`): Square button for actions, `padding: 8px`

**Button States:**
- Hover: `transform: translateY(-1px)`, `shadow: shadow-medium`
- Disabled: `opacity: 0.6`, `cursor: not-allowed`
- Loading: Show spinner, disable interaction

### Form System

Consistent form elements for better user experience:

**Form Group:**
```css
.form-group {
  margin-bottom: 16px;
}
```

**Form Label:**
```css
.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}
```

**Form Input:**
```css
.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.875rem;
  background: var(--bg-surface);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(102, 144, 255, 0.1);
}
```

### Word/Translation System

Unified system for displaying word pairs and translations:

**Word Chip:**
```css
.word-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.word-chip.selected {
  background: var(--primary-blue);
  color: white;
  border-color: var(--primary-blue);
}
```

**Word Pair Container:**
```css
.word-pair {
  display: flex;
  align-items: center;
  gap: 8px;
}

.word-pair__original {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.word-pair__translation {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.word-pair__divider {
  color: var(--text-secondary);
  font-weight: 400;
}
```

**Words Display:**
```css
.words-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
```

### Card System

Consistent card styling for content containers:

**Base Card:**
```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  box-shadow: shadow-small;
  transition: all 0.2s;
}

.card:hover {
  box-shadow: shadow-medium;
  transform: translateY(-1px);
}
```

**Card Header:**
```css
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 4px 0 0 0;
}
```

**Card Meta:**
```css
.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 12px;
}
```

### Loading States

Consistent loading indicators:

**Spinner:**
```css
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner--large {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

**Skeleton Loading:**
```css
.skeleton {
  background: linear-gradient(90deg, var(--border-color) 25%, var(--bg-primary) 50%, var(--border-color) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

## Implementation Guidelines

### CSS Class Naming Convention

Use BEM (Block Element Modifier) methodology for consistent class naming:

- **Block**: `.modal`, `.badge`, `.btn`, `.form`
- **Element**: `.modal__header`, `.badge__icon`, `.btn__text`
- **Modifier**: `.btn--primary`, `.badge--language`, `.modal--large`

### Responsive Design

All components should be responsive with mobile-first approach:

- **Mobile**: Default styles (320px+)
- **Tablet**: `@media (min-width: 768px)`
- **Desktop**: `@media (min-width: 1024px)`
- **Large Desktop**: `@media (min-width: 1280px)`

### Accessibility

All components must meet WCAG 2.1 AA standards:

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus Indicators**: Visible focus states for all interactive elements
- **Keyboard Navigation**: All interactive elements must be keyboard accessible
- **Screen Reader Support**: Proper ARIA labels and semantic HTML

### Performance

Design system implementation should prioritize performance:

- **CSS Variables**: Use CSS custom properties for theming
- **Minimal CSS**: Avoid unnecessary styles and selectors
- **Efficient Animations**: Use `transform` and `opacity` for animations
- **Lazy Loading**: Implement lazy loading for non-critical components 