# Design

## Overall Style

The interface is a restrained technical product workbench. It should look useful at first glance: left navigation, dense module overview, rule/status panels, evidence cards, and clear primary actions. Visual weight comes from hierarchy, structure, and live data-like artifacts, not decorative illustration.

## Color

Use a neutral product palette with enough temperature contrast to avoid a flat single-hue surface. CSS tokens are authored in OKLCH.

- Background: `oklch(0.96 0.01 210)`
- Content surface: `oklch(0.99 0.003 210)`
- Sidebar surface: `oklch(0.91 0.012 185)`
- Border: `oklch(0.82 0.014 185)`
- Primary text: `oklch(0.24 0.018 185)`
- Muted text: `oklch(0.48 0.025 185)`
- Primary accent: `oklch(0.48 0.13 255)`
- Secondary accent: `oklch(0.55 0.13 65)`
- Success: `oklch(0.48 0.11 150)`
- Warning: `oklch(0.55 0.13 65)`
- Error: `oklch(0.48 0.16 28)`
- Info: `oklch(0.48 0.13 255)`

Accent colors are reserved for selection, state, and primary actions.

## Typography

Use a system sans stack for product UI:

```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Use a tight fixed rem scale. Avoid fluid type. Headings inside panels should stay compact.

## Layout

Default surface:

- App shell with persistent sidebar.
- Top toolbar for current cycle and command actions.
- Main content as a responsive grid of workbench panels.
- Right rail for development loop, evidence, and next actions.

Desktop should favor density. Mobile should collapse the sidebar into a top module list and stack panels vertically.

## Components

Core component vocabulary:

- Icon buttons for commands.
- Segmented controls for module modes.
- Tabs for views within a tool.
- Status chips with text and color.
- Compact cards for individual modules or evidence items.
- Tables/lists for rules, fixtures, and development tasks.
- Inline empty states and skeleton-like loading rows.

All controls need default, hover, focus-visible, active, disabled, and loading-friendly styling.

## Motion

Use short 150-200 ms transitions for hover, selection, and panel changes. Respect `prefers-reduced-motion`. Avoid decorative page-load motion.

## Imagery And Artifacts

The product uses technical artifacts as its visual material: schema snippets, rule graphs, before/after diff bars, validation traces, report status, and fixture previews. It does not rely on stock imagery.
