# Design System Specification: The Academic Curator

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Curator"**
This design system moves away from the cluttered, bureaucratic feel of traditional university portals. Instead, it adopts the persona of a high-end academic journal or a curated gallery. The goal is to facilitate "Deep Work" by utilizing a high-contrast editorial hierarchy, intentional asymmetry, and a sense of "prestige through restraint."

By prioritizing breathing room and tonal depth over rigid lines, we transform a functional tool into an authoritative workspace. We break the "template" look by treating the interface as a series of layered, physical artifacts rather than flat digital boxes.

---

## 2. Colors & Surface Philosophy
The palette utilizes a sophisticated "Scholarly Oxblood" (`primary`) and "Guilded Accents" (`tertiary`) set against a multi-tonal grayscale foundation.

### The "No-Line" Rule
**Explicit Instruction:** 1px solid borders are strictly prohibited for sectioning or containment. Boundaries must be defined through:
1.  **Tonal Shifts:** Placing a `surface-container-low` component on a `surface` background.
2.  **Negative Space:** Using a rigorous 8px-based spacing scale to imply grouping.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of fine paper.
*   **Base:** `surface` (#f9f9f9) is your canvas.
*   **Structural Sections:** Use `surface-container` (#eeeeee) for sidebar backgrounds or large page sections.
*   **Interactive Cards:** Use `surface-container-lowest` (#ffffff) to make content "pop" forward naturally.
*   **Active Elements:** Use `surface-bright` for focused states.

### The "Glass & Gradient" Rule
To elevate the UI beyond standard dashboards:
*   **CTAs:** Use a subtle linear gradient on primary buttons (from `primary` #610000 to `primary_container` #8b0000) at 135 degrees.
*   **Floating Navigation:** Apply `backdrop-blur: 12px` with a 70% opacity `surface` fill to create a sophisticated glass effect for top navigation bars.

---

## 3. Typography: Editorial Authority
We pair **Manrope** (Display/Headlines) with **Inter** (UI/Body) to balance modern geometry with high legibility.

*   **The Power Scale:** Use `display-lg` (3.5rem) sparingly for dashboard greetings or milestone titles to create an editorial "Cover Page" feel.
*   **Rhythmic Contrast:** Always pair a `headline-sm` (Manrope, 1.5rem, Bold) with a `label-md` (Inter, 0.75rem, All-caps, tracked out 5%) to create an authoritative, metadata-rich look.
*   **Body Copy:** Use `body-lg` (1rem) for thesis abstracts and `body-md` (0.875rem) for functional UI elements.

---

## 4. Elevation & Depth
Depth is achieved through **Tonal Layering** rather than structural geometry.

*   **The Layering Principle:** Place a `surface-container-lowest` card on top of a `surface-container-low` background. This creates a "soft lift" that feels architectural rather than digital.
*   **Ambient Shadows:** For floating modals or "active" cards, use a multi-layered shadow:
    *   `box-shadow: 0 4px 20px rgba(26, 28, 28, 0.04), 0 12px 40px rgba(26, 28, 28, 0.06);`
    *   *Note:* Shadow color must be a tinted version of `on-surface` (#1a1c1c), never pure black.
*   **The "Ghost Border":** If accessibility requires a border, use `outline-variant` (#e3beb8) at 20% opacity. It should be felt, not seen.

---

## 5. Components

### Buttons
*   **Primary:** Solid `primary` fill. No border. `xl` (0.75rem) roundedness. 
*   **Secondary:** `secondary-container` fill with `on-secondary-container` text. High-end, low-friction.
*   **Tertiary (The "Accent"):** Use `tertiary_fixed` (#ffe16d) for high-importance academic alerts or "Submit" actions.

### Cards & Lists
*   **Forbid Dividers:** Do not use `<hr>` tags or border-bottoms. 
*   **Vertical Momentum:** Separate list items using 16px of vertical padding and a background shift on hover (`surface-container-high`).
*   **Academic Progress Cards:** Use a `primary` left-accent bar (4px width) on cards to denote "Current" or "Active" status.

### Input Fields
*   **Styling:** No bottom-line-only inputs. Use a full `surface-container-low` fill with `xl` (0.75rem) corners.
*   **Focus State:** Shift background to `surface-container-lowest` and apply a 2px `primary` ghost-border (20% opacity).

### Specialized Academic Components
*   **The Milestone Tracker:** A vertical line component using `outline-variant` with nodes that glow in `tertiary_fixed_dim` when completed.
*   **Document Preview:** A "Paper-Stack" component using `surface-container-lowest` with overlapping offsets to represent a thesis draft.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use asymmetrical layouts. A sidebar that is significantly wider than standard, or a header that spans 2/3 of the screen, creates an "expensive" custom feel.
*   **Do** use `tertiary` (Gold/Yellow) as a surgical strike. Use it only for "Success," "Milestone Reached," or "Gold-Star" feedback.
*   **Do** embrace white space. If a section feels crowded, double the padding instead of adding a divider.

### Don’t
*   **Don't** use 100% opaque borders. They create "visual noise" and make the app feel like a generic administration tool.
*   **Don't** use pure black (#000000) for text. Use `on-surface` (#1a1c1c) to maintain a soft, premium "ink-on-paper" contrast.
*   **Don't** use standard "Success Green." Use the `tertiary` gold palette to signify achievement, staying true to the university's prestigious branding.