# Copilot Instructions for Adopt-a-Coral Website

## Project Overview

**Adopt-a-Coral** is a static GitHub Pages website for a citizen science initiative capturing Caribbean coral reefs via crowdsourced 3D imaging. The site is purely front-end HTML/CSS/JS with no backend. Domain: `adopt-a-coral.xyz` (via CNAME).

## Architecture & Structure

### Current Implementation
- **`index.html`** - **NEW: Comprehensive single-page site** covering mission, gaps, how-to, data workflow, partners & map, travel blog, team, resources, and FAQ
- **`single-page.html`** - Earlier single-page version (kept for reference)
- **`index-old.html`** - Original multi-page index (archived for reference)

### Legacy Multi-Page Structure (deprecated but archived)
- `adopt.html` - Instructions for participants (5-step workflow)
- `data-workflow.html` - Data handling, model submission process, embedded 3D viewer examples
- `partners-map.html` - Network of participating dive shops, NGOs, embedded Leaflet map
- `blog.html` - Matan's travel narrative and field notes
- `repository.html` - Git/data repository reference

All pages share identical header/nav structure (see **Common Pattern** below).

### Static Assets
- **`assets/css/style.css`** - Single unified stylesheet (203 lines) - ALL styling here
- **`assets/js/map.js`** - Currently empty; intended for Leaflet map initialization (partners-map.html)
- **`assets/img/`** - Images, favicons; `c/` subfolder (not yet explored)

## Key Patterns & Conventions

### 1. **Single-Page Navigation (New)**
The new `index.html` uses hash-based anchor links with smooth scrolling:
```html
<nav>
  <ul>
    <li><a href="#mission">Mission</a></li>
    <li><a href="#why-caribbean">Why Caribbean?</a></li>
    <li><a href="#how-to">How to adopt</a></li>
    <li><a href="#data">Data & workflow</a></li>
    <li><a href="#partners">Partners & map</a></li>
    <li><a href="#blog">Travel blog</a></li>
    <li><a href="#team">Team</a></li>
    <li><a href="#faq">FAQ</a></li>
  </ul>
</nav>

<section class="card" id="mission"><!-- Content --></section>
```

**Key features:**
- No page reloads; smooth scroll-to-section behavior
- Nav links auto-highlight active section on scroll (JavaScript in footer)
- All content in one continuous flow
- Scroll margin (80px) prevents sticky nav from covering section headings

### 2. **New Sections in index.html**

#### Team section
Uses `.team-grid` (responsive 3-column layout):
```html
<section class="card" id="team">
  <div class="team-grid">
    <div class="team-card">
      <h4>Name</h4>
      <div class="role">Role title</div>
      <p>Bio/description</p>
    </div>
  </div>
</section>
```

#### FAQ section (Expandable details)
Uses native `<details>` elements styled with `.faq-item`:
```html
<details class="faq-item">
  <summary>Question here?</summary>
  <p>Answer here.</p>
</details>
```
Styling: `.faq-item summary` shows pointer cursor and toggles color on `:hover` and `[open]`

#### Resources section
Lists external tools and platforms using `.resources-list` (styled as unstyle ul with metadata):
```html
<ul class="resources-list">
  <li>
    <strong><a href="https://...">Tool name</a></strong>
    <small>Description of tool</small>
  </li>
</ul>
```

#### Travel blog section
Uses `<article>` blocks with `<small class="muted">` date/location tags:
```html
<article>
  <h3>Blog post title</h3>
  <small class="muted">Location · Date · Field dispatch</small>
  <p>Narrative text with context...</p>
</article>
<hr>
```

### 3. **CSS Design System (Updated)**
Core variables in `:root`:
```css
--bg: #f8f3ea;              /* Warm beige background */
--card: #ffffff;            /* White content cards */
--accent: #ff8a4a;          /* Orange CTAs & highlights */
--accent-dark: #c85b1c;     /* Darker orange on hover */
--deep-blue: #043649;       /* Header/nav text, branding */
--text: #1f2933;            /* Body text */
```

**Key reusable classes:**
- `.card` - Main content container (rounded, shadow, padding)
- `.card.cta-card` - Gradient CTA card with accent border (use for call-to-action sections)
- `.grid-two` - 2-column layout (responsive: 1-col on <800px)
- `.grid-three` (planned) - 3-column layout via `.team-grid`
- `.team-grid` - Auto-fit 3-column grid for team/partner cards
- `.team-card` - Individual team member card with role, bio
- `.callout` - Highlighted info box (orange left border, beige bg)
- `.btn` - Orange button (use for CTAs like "Adopt Now")
- `.embed-wrapper` - Responsive iframe container (65% aspect ratio) for 3D models
- `.muted` - Small muted gray text
- `.resources-list` - Unstyled list with bold title + small description
- `.faq-item` - Expandable FAQ question (`<details>` element)
- `.faq-item summary` - Highlights on hover, changes color when `[open]`
- `.faq-item[open]` - Styling for expanded state

### 3. **Content Layout Structure**
Within `<main>` (max-width: 1000px, auto margins):
```html
<section class="card">
  <h2>Section Title</h2>
  <div class="grid-two">
    <div><!-- Left column --></div>
    <div class="callout"><!-- Sidebar highlight --></div>
  </div>
</section>
```

## Critical External Dependencies

- **Leaflet Map** (`partners-map.html`) - CDN link unpacked in `<head>`:
  ```html
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  ```
  `map.js` is placeholder; implement Leaflet initialization if map interactivity needed.

- **3D Model Embedding** (`data-workflow.html`) - KIRI Engine iframe:
  ```html
  <iframe src="https://www.kiriengine.app/share/embed/[ID]" />
  ```
  Embedded models are read-only; no user authentication required.

## Developer Workflows

### Local Viewing
- Open any `.html` file directly in browser (no build step required)
- Changes to `style.css` or content are live immediately

### Deployment
- Push to `main` branch → GitHub Pages auto-deploys
- CNAME file (`adopt-a-coral.xyz`) ensures custom domain routing
- No build, no dependencies, no CI/CD

## Content & Messaging Conventions

- **Tone:** Inclusive, science-forward, action-oriented (citizen science for conservation)
- **Coral Focus:** Emphasis on accessibility (any diver/snorkeler can participate) and open data
- **Geographic:** Caribbean-centric partnerships, local dive shops/NGOs featured
- **Technical Accuracy:** 3D reconstruction workflows (KIRI Engine, Luma), Creative Commons licensing, Zenodo archiving mentioned

## When Editing

1. **Page Content Update** → Edit `index.html` (now single-page)
2. **Add new sections** → Insert before the footer CTA with proper `id` attribute and nav link
3. **Styling Changes** → Modify `style.css` only (shared across all pages)
4. **New Colors/Tokens** → Add to `:root` in `style.css` first
5. **External Links** → Verify partner URLs/organizations are current (e.g., ReefMatters, Raising Corals links, Luma, KIRI Engine)
6. **Team/Partner info** → Update `.team-grid` and `#partners` sections with new names/bios
7. **Travel blog entries** → Add new `<article>` blocks with `<hr>` separators in `#blog` section
8. **FAQ items** → Add new `<details class="faq-item">` blocks in `#faq` section
9. **Resources** → Update `.resources-list` items with new tools/platforms in `#resources` section

**Legacy pages:** If updating old multi-page versions (adopt.html, blog.html, etc.) for backwards compatibility, maintain nav consistency across all files.

## File Dependencies

- All HTML files reference `assets/css/style.css` (critical—missing breaks all pages)
- All HTML files reference `assets/img/favicon.png` (optional but expected)
- `partners-map.html` requires Leaflet CSS/JS CDN + `map.js` initialization
- `data-workflow.html` embeds KIRI Engine iframe (no local dependency)

---

Last updated: December 2025
