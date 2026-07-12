---
name: Aquatic Trust Design System
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#44474e'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#495f82'
  primary: '#001026'
  on-primary: '#ffffff'
  primary-container: '#0b2545'
  on-primary-container: '#778db2'
  inverse-primary: '#b1c7f0'
  secondary: '#006a62'
  on-secondary: '#ffffff'
  secondary-container: '#70f8e8'
  on-secondary-container: '#007168'
  tertiary: '#160e00'
  on-tertiary: '#ffffff'
  tertiary-container: '#312200'
  on-tertiary-container: '#b28400'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#b1c7f0'
  on-primary-fixed: '#001c3b'
  on-primary-fixed-variant: '#314769'
  secondary-fixed: '#70f8e8'
  secondary-fixed-dim: '#4fdbcc'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffdfa0'
  tertiary-fixed-dim: '#fbbc00'
  on-tertiary-fixed: '#261a00'
  on-tertiary-fixed-variant: '#5c4300'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
overrideColors:
  primary: '#0b2545'
  secondary: '#2ec4b6'
  tertiary: '#ffbf00'
  neutral: '#faf9f6'
typography:
  display-lg:
    fontFamily: Cairo
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 52px
  headline-lg:
    fontFamily: Cairo
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Cairo
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  title-md:
    fontFamily: Cairo
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Cairo
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Cairo
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Cairo
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.02em
  caption:
    fontFamily: Cairo
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 30px
  gutter: 20px
  margin-mobile: 16px
  margin-desktop: 30px
---

## Source
Synced from Stitch project **Aqua Course Registration** (`projects/1695359203304362819`), design system "Aquatic Trust Design System". Re-sync via Stitch MCP (`get_project`) if the design system changes upstream.

## Brand & Style
The design system is engineered for a premium swimming facility in Lebanon, balancing the technical precision of professional athletics with the warmth required for a child-centric service. The target audience is parents who value safety, reliability, and structured progress.

The visual style is **Corporate Modern with Tactile Softness**. It avoids the clinical coldness of healthcare systems by using fluid, organic roundedness and aquatic accents, yet maintains a rigorous professional hierarchy that conveys institutional trust. The interface uses a clean, high-contrast base to ensure readability for busy parents on the move.

## Colors
The palette is rooted in the deep authority of Navy, representing the facility's professional standards. Aqua/Teal is used strategically for interactive elements and accents to evoke a refreshing, aquatic feel.

- **Primary (Navy `#0B2545`):** Used for primary actions, headings, and core navigation.
- **Secondary (Aqua `#2EC4B6`):** Reserved for interactive states, selection indicators, and success highlights.
- **Background (Off-white `#FAF9F6`):** A soft, "paper" white that reduces eye strain compared to pure hex white.
- **Semantic Palette:** Functional colors for status tracking are slightly desaturated to maintain the professional aesthetic while providing clear feedback on registration states.

## Typography
This design system utilizes **Cairo** for its exceptional legibility in both Arabic and Latin scripts, essential for the Lebanese context.

The type hierarchy is generous. Body text is set at 16px-18px to ensure easy reading for parents during registration. Headlines use a bold weight to establish clear section breaks. For mobile views, display sizes scale down to prevent awkward line breaks while maintaining their weight for brand impact.

## Layout & Spacing
The system employs a **Fluid Grid** with a baseline unit of 8px.

- **Mobile:** 4-column layout with 16px side margins.
- **Desktop:** 12-column layout with a max-width of 1200px and 24px gutters.
- **Rhythm:** Vertical spacing between cards and sections should primarily use 24px (lg) to maintain an airy, approachable feel. Compact lists or internal card elements should use 16px (md).

## Elevation & Depth
Depth is created through **Ambient Shadows** and tonal layering rather than harsh borders.

- **Level 1 (Base Cards):** Use a very soft, diffused shadow (`0px 4px 20px rgba(11, 37, 69, 0.08)`) against the off-white background.
- **Level 2 (Active/Hover):** Increase shadow spread and add a 2px Aqua border to indicate selection.
- **Modals:** Use a heavy blur backdrop (8px) with a more pronounced shadow to focus attention on the registration flow.

## Shapes
The shape language is consistently **Rounded**.

Containers and registration cards use a 16px corner radius (`rounded-lg`) to feel friendly and safe. Smaller elements like buttons, inputs, and chips follow this logic but scale down to 8px or 12px to maintain visual harmony. Interactive components should never have sharp 90-degree corners.

## Components

### Buttons
- **Primary:** Full-width Navy (`#0B2545`) with white text. 16px padding and 12px radius.
- **Secondary:** Transparent with Aqua (`#2EC4B6`) border and text.

### Registration Cards
Selectable cards used for choosing time slots or courses. They feature a 16px radius, a white fill, and a subtle shadow. Upon selection, the border transitions from neutral to 2px Aqua.

### Status Chips
Small, high-visibility badges with a 50px (pill) radius.
- **Pending:** Amber background with dark contrast text.
- **Confirmed:** Green background with white text.
- **Completed:** Blue-gray background with white text.

### Inputs & Segmented Controls
- **Inputs:** Large touch targets (min-height 56px) with a soft-gray border that turns Navy on focus.
- **Segmented Controls:** Used for toggling between "Current Courses" and "Past Courses." Use a Navy background for the active segment with a sliding animation for a premium feel.

### Progress Indicator
A thin Aqua bar at the top of the registration flow to guide parents through the multi-step signup process without cluttering the UI.

## Screens in Stitch project
Fetch HTML/screenshots for any of these via `get_screen` (Stitch MCP) using the project ID above:

- Registration Page — Desktop / Arabic (Desktop)
- Registration Success — Desktop / Arabic (Desktop)
- Admin Dashboard — Reorganized Layout
- Admin Settings — Unified Layout
- Course Cycles List — Realigned Layout
- Course Cycles — Delete Confirmation Modal
- Create Cycle Modal — Overlap Error
- Enrollment Management — Edit Details Modal / Record Payment Modal / Top Bar Update
- Participant Management — Delete Confirmation Modal / Edit & Delete Modals / Layout Fix & Header Restore
- Reservations Day Calendar — Sidebar Refresh
- New Reservation Drawer — Simplified Status
