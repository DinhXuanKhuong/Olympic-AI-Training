---
name: Serene Academic
colors:
  surface: '#fbf8fd'
  surface-dim: '#dbd9de'
  surface-bright: '#fbf8fd'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f2f8'
  surface-container: '#efedf2'
  surface-container-high: '#eae7ec'
  surface-container-highest: '#e4e1e7'
  on-surface: '#1b1b1f'
  on-surface-variant: '#504347'
  inverse-surface: '#303034'
  inverse-on-surface: '#f2f0f5'
  outline: '#827377'
  outline-variant: '#d4c2c6'
  surface-tint: '#834f62'
  primary: '#834f62'
  on-primary: '#ffffff'
  primary-container: '#d99aaf'
  on-primary-container: '#603143'
  inverse-primary: '#f6b4ca'
  secondary: '#7f5160'
  on-secondary: '#ffffff'
  secondary-container: '#fec2d3'
  on-secondary-container: '#7a4c5b'
  tertiary: '#2e694b'
  on-tertiary: '#ffffff'
  tertiary-container: '#7cb996'
  on-tertiary-container: '#064a2f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9e3'
  primary-fixed-dim: '#f6b4ca'
  on-primary-fixed: '#350d1e'
  on-primary-fixed-variant: '#68384a'
  secondary-fixed: '#ffd9e3'
  secondary-fixed-dim: '#f2b7c8'
  on-secondary-fixed: '#32101d'
  on-secondary-fixed-variant: '#653a48'
  tertiary-fixed: '#b2f0ca'
  tertiary-fixed-dim: '#96d4af'
  on-tertiary-fixed: '#002112'
  on-tertiary-fixed-variant: '#115135'
  background: '#fbf8fd'
  on-background: '#1b1b1f'
  surface-variant: '#e4e1e7'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 19px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2.5rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system delivers a calm, dignified, and visually soothing environment tailored for university scholars and students enduring demanding, multi-hour study and exam periods. It replaces the high-stress, gamified, and hyper-saturated visuals typical of modern ed-tech with an atmosphere of quiet intellectual focus and gentle warmth.

The aesthetic fuses contemporary academic minimalism with soft warmth. Powder pink serves not as an ornament or novelty, but as a low-wavelength, gentle accent that reduces ocular strain compared to harsh primary blues or stark black-and-white interfaces. The visual tone is mature, disciplined, and poised. There are no distracting micro-animations, floating illustrative blobs, gradients, or playful cartoonish motifs. Every container, border, and typographical choice serves clarity, retention, and focus.

## Colors

The palette is anchored by soft warm whites, muted blush tones, and deep charcoal text to provide optimal legibility without glare.

### Primary & Action Colors
- **Action Primary**: `#D99AAF` — Used for interactive buttons, primary toggles, and critical action triggers.
- **Action Hover**: `#C9829A` — Slightly deeper, reassuring state for hover interactions.
- **Action Active / Pressed**: `#C97C92` — Deepest rose state for depressed buttons and active selections.
- **Powder Pink Accent**: `#E8AEBF` — For non-text structural accents, progress fills, and active indicator rules.

### Surfaces & Neutral Grounds
- **Main Canvas**: `#FFFCFD` — Warm, off-white foundation that eliminates cold screen glare.
- **Card & Container Surface**: `#FFFFFF` — Crisp pure white used for resting cards, questions, and modular panels.
- **Selected Card Surface**: `#FDF4F7` — Very pale blush for selected multiple-choice options or active rows.
- **Tinted Container**: `#F5DCE4` — Delicate highlight fill for badges, banners, and toolbars.
- **Muted Surface**: `#F8F6F7` — Neutral foundation for sidebars, disabled areas, and secondary panels.
- **Structural Border**: `#EAE5E7` — Quiet, 1px border that delineates elements without high visual contrast.

### Typography
- **Primary Ink**: `#2F2F33` — Soft charcoal offering high contrast and readability without the harshness of pure `#000000`.
- **Secondary Ink**: `#73737A` — Balanced mid-tone for metadata, timestamps, section subtitles, and helper labels.

### Academic & Assessment Feedback
- **Correct / Complete**: Text `#4A8565`, Background `#F2F8F4`, Border `#BFE0CE`.
- **Incorrect / Flagged**: Text `#B85864`, Background `#FDF3F4`, Border `#EFC5CA`.
- **Pending / Cautionary**: Text `#B57F3A`, Background `#FEF9F0`, Border `#F3DEC2`.

## Typography

The design system employs **Inter** universally across all textual layers. With its neutral, highly engineered proportions, tall x-height, and crisp counters, Inter offers uninterrupted reading fluency for complex stems, formulas, and long-form analytical prose.

- **Headlines & Titles**: Keep tight tracking (`-0.015em` to `-0.01em`) and semibold weights (`600`) to anchor the hierarchy without appearing heavy.
- **Assessment Questions**: Use `headline-sm` (`19px`, `500`) with generous line-height (`28px`) to ensure cognitive parsing remains effortless during timed conditions.
- **Body Content**: Employs comfortable leading (e.g., `26px` on `16px` font) to maintain eye-tracking over multi-paragraph reading passages.
- **Labels & Microcopy**: Formatted with moderate weights (`500`) and slight positive letter-spacing (`0.02em`) on small scales to preserve legibility in badges, timers, and index pagers.

## Layout & Spacing

Layouts adhere to a disciplined 12-column grid system for desktop and tablet, shifting to a single-column stacked view on mobile. The content structure is centered, restrained, and purposeful, avoiding edge-to-edge sprawl that causes reading fatigue.

- **Desktop (1024px and above)**: The main exam canvas stays bounded within a maximum content container of `1160px`. Left or right toolbars (question matrices, timers, reference sheets) occupy fixed columns while the primary stem and response area occupies the central reading lane.
- **Tablet (768px – 1023px)**: Responsive reflow where side navigation condenses into a clean secondary header or drawer, preserving a minimum `640px` width for central question bodies.
- **Mobile (Below 768px)**: Canvas margins pull in to `1.25rem` (`margin-mobile`), full-width options, and bottom-pinned persistent action bars for progression.
- **Vertical Rhythm**: Built upon an 8px baseline. Paragraphs, options, and question blocks use `space-md` (`1rem`) and `space-lg` (`1.5rem`) gaps to keep sections neatly separated.

## Elevation & Depth

This system avoids dramatic dropshadows, glassmorphic blurs, and floating cards. Elevation is established through tonal layering, crisp borders, and subtle surface contrasts.

- **Zero-Shadow Default**: Primary interactive surfaces, inputs, and cards use flat fills bordered by `1px solid #EAE5E7` on top of the `#FFFCFD` canvas.
- **Restrained Overlay Shadow**: When a floating sheet, modal, or dropdown menu is strictly required (such as an academic formula sheet or calculator flyout), apply an ambient, warm-tinted shadow:
  `box-shadow: 0 4px 16px -2px rgba(47, 47, 51, 0.05), 0 2px 6px -1px rgba(47, 47, 51, 0.03);`
- **Active & Pressed State**: Deepens purely through color changes (`#D99AAF` -> `#C97C92`) rather than artificial inset bevels or neumorphic shifts.

## Shapes

The shape vocabulary uses moderate, soft-cornered geometry that feels calm and approachable while preserving structure.

- **Cards & Paneling**: `10px` to `12px` border radius provides a soft enclosure without appearing childlike or bubbly.
- **Buttons & Form Controls**: `8px` to `10px` border radius matches the structural cards and balances ergonomics with discipline.
- **Badges & Numerical Index Pills**: Standardize on `6px` to `8px` radius. Oversized, full pill shapes (`rounded-full`) are intentionally avoided to maintain academic maturity.

## Components

### Buttons
- **Primary Action**: Background `#D99AAF`, Text `#FFFFFF`, Border `none`, Radius `8px`, Font Weight `500`. Hover state transitions to `#C9829A`; active state transitions to `#C97C92`.
- **Secondary Action**: Background `#FFFFFF`, Text `#2F2F33`, Border `1px solid #EAE5E7`, Radius `8px`. Hover state changes background to `#F8F6F7`.
- **Ghost / Subtle**: Background `transparent`, Text `#73737A`. Hover state changes text to `#2F2F33` with background `#FDF4F7`.

### Answer Choice Cards (Single & Multiple Choice)
- **Resting**: Background `#FFFFFF`, Border `1px solid #EAE5E7`, Radius `10px`, Padding `16px 20px`. Text in `#2F2F33`.
- **Hover**: Border color shifts to `#D99AAF`.
- **Selected**: Background `#FDF4F7`, Border `1.5px solid #D99AAF`, Text `#2F2F33`. Left index badge (A, B, C, D) fills with `#D99AAF` and white text.
- **Correct Review State**: Background `#F2F8F4`, Border `1.5px solid #BFE0CE`.
- **Incorrect Review State**: Background `#FDF3F4`, Border `1.5px solid #EFC5CA`.

### Form Inputs & Text Areas
- Background `#FFFFFF`, Border `1px solid #EAE5E7`, Radius `8px`, Padding `10px 14px`, Text `#2F2F33`.
- **Focus**: Border `1.5px solid #D99AAF`, Box-shadow `none`, Outline `none`.
- **Placeholder**: Text `#73737A` at 60% opacity.

### Selection Controls (Checkboxes & Radios)
- Radios are `18px` circular controls, Checkboxes are `18px` with `4px` radius.
- Resting border is `1.5px solid #EAE5E7`.
- Selected state fills with `#D99AAF` and displays a white glyph or centered dot.

### Question Navigation Matrix
- Compact `36px x 36px` cells, radius `6px`, font size `13px`, medium weight.
- Unvisited: `#FFFFFF` border `1px solid #EAE5E7`, text `#73737A`.
- Answered: `#F5DCE4` background, border `1px solid #D99AAF`, text `#2F2F33`.
- Current: `#D99AAF` background, text `#FFFFFF`.
- Flagged: `#FEF9F0` background, border `1px solid #F3DEC2`, text `#B57F3A`.

### Timer & Session Header
- Contained within a `#FFFFFF` bar with a bottom `1px solid #EAE5E7` border.
- Digital time counters use tabular lining figures with subtle `#F8F6F7` backing badges.