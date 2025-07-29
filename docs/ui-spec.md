# Vocabloom UI Specification

This document serves as the source of truth for all UI design decisions, component specifications, and design system guidelines for the Vocabloom application.

## Color Palette

### Light Mode
```css
:root {
  --primary-blue: #6690ff;
  --primary-orange: #e19f5d;
  --primary-yellow: #f2cd4a;
  --success-green: #4ade80;
  --warning-amber: #fbbf24;
  --error-red: #f87171;
  --premium-purple: #a78bfa;
  --info-cyan: #38bdf8;
  --accent-pink: #f472b6;
  --bg-primary: #f8fafc;
  --bg-surface: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
  --blue-hover: #4a7aff;
}
```

### Dark Mode
```css
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-surface: #1e293b;
  --text-primary: #e2e8f0;
  --text-secondary: #cbd5e1;
  --border-color: #334155;
  --blue-hover: #6366f1;
}
```

### Color Usage Guidelines

#### Primary Colors
- **Primary Blue** (`#6690ff`): Main brand color, used for primary actions, links, and key UI elements
- **Primary Orange** (`#e19f5d`): Secondary brand color, used for accents and highlights
- **Primary Yellow** (`#f2cd4a`): Tertiary brand color, used for warnings and attention-grabbing elements

#### Semantic Colors
- **Success Green** (`#4ade80`): Success states, positive feedback, completed actions
- **Warning Amber** (`#fbbf24`): Warning states, cautionary messages, pending actions
- **Error Red** (`#f87171`): Error states, destructive actions, validation failures
- **Info Cyan** (`#38bdf8`): Informational messages, help text, neutral feedback

#### Premium/Accent Colors
- **Premium Purple** (`#a78bfa`): Premium features, special highlights
- **Accent Pink** (`#f472b6`): Special accents, decorative elements

#### Background Colors
- **Background Primary** (`#f8fafc`): Main page background
- **Background Surface** (`#ffffff`): Card backgrounds, modal backgrounds, elevated surfaces

#### Text Colors
- **Text Primary** (`#1e293b`): Main text, headings, important content
- **Text Secondary** (`#64748b`): Secondary text, descriptions, less important content

#### Border Colors
- **Border Color** (`#e2e8f0`): Default borders, dividers, subtle separators

### Implementation Notes

1. **CSS Variables**: All colors should be implemented using CSS custom properties (variables) for consistency and easy theming
2. **Dark Mode Support**: The application should support both light and dark modes using the `[data-theme="dark"]` selector
3. **Accessibility**: All color combinations should meet WCAG 2.1 AA contrast requirements
4. **Hover States**: Use `--blue-hover` for interactive elements in their hover state

### Color Combinations

#### Primary Actions
- Background: `var(--primary-blue)`
- Text: White
- Hover: `var(--blue-hover)`

#### Secondary Actions
- Background: `var(--bg-surface)`
- Text: `var(--primary-blue)`
- Border: `var(--primary-blue)`

#### Success States
- Background: `var(--success-green)`
- Text: White or dark text depending on contrast

#### Warning States
- Background: `var(--warning-amber)`
- Text: Dark text for readability

#### Error States
- Background: `var(--error-red)`
- Text: White for maximum contrast

---

## Typography

*[To be defined]*

## Spacing System

*[To be defined]*

## Component Specifications

*[To be defined]*

## Layout Guidelines

*[To be defined]*

## Accessibility Standards

*[To be defined]*

## Responsive Design

*[To be defined]*

## Animation & Transitions

*[To be defined]* 