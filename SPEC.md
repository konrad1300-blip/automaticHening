# AutomaticHening - Program do projektowania plandek

## 1. Project Overview

**Project Name:** AutomaticHening  
**Project Type:** Desktop Application (Python/PyQt6)  
**Core Functionality:** A CAD program for designing tarpaulins from STEP 3D files, generating 2D cutting patterns with reinforcements, seams, and attachment hardware.

## 2. UI/UX Specification

### 2.1 Window Structure

1. **Welcome Window** (Opera-style)
   - Full-screen splash with gradient background
   - "Otwórz plik STEP" button (primary)
   - "Ostatnie projekty" section (recent files)
   - App logo/title centered

2. **Main Window** (3D viewer)
   - Menu bar: Plik, Edycja, Widok, Generuj, Pomoc
   - Toolbar with icons
   - Central 3D viewport (PyQtGraph/OpenGL)
   - Status bar

3. **2D Pattern Window**
   - Generated tarp visualization
   - Controls sidebar
   - Export buttons

### 2.2 Visual Design

**Color Palette:**
- Primary: `#1E88E5` (blue)
- Secondary: `#424242` (dark gray)
- Accent: `#FF6F00` (orange)
- Background: `#FAFAFA` (light gray)
- Panel: `#FFFFFF` (white)
- Text: `#212121`

**Typography:**
- Font: Segoe UI / system default
- Headings: 16px bold
- Body: 12px regular
- Labels: 10px

**Spacing:**
- Base unit: 8px
- Margins: 16px
- Padding: 8px

### 2.3 Components

**Toolbar Icons:**
- Otwórz (folder icon)
- Obróć (rotate icon)
- Przybliż/oddal (zoom icons)
- Generuj plandekę (tarp icon)
- Eksportuj (export icon)

**Buttons:**
- Primary: Blue background, white text, rounded 4px
- Secondary: White background, blue border
- Hover: Slight darken

## 3. Functional Specification

### 3.1 Core Features

1. **STEP File Loading**
   - Support .step and .stp formats
   - Parse using OCCT or python-occ
   - Display 3D model in viewport

2. **3D Manipulation**
   - Rotate: Left mouse drag
   - Pan: Right mouse drag / middle mouse
   - Zoom: Scroll wheel
   - Reset view button

3. **Tarpaulin Generation Algorithm**
   - Find extreme vertices (boundary points)
   - Create face planes from vertices
   - Find plane intersections (edges)
   - Generate 2D unfold pattern
   - Calculate dimensions and angles

4. **Seam Allowance**
   - Toggle:Zszywana / Zgrzewana
   - Sewing: 1.5cm margin
   - Welding: 2.5cm margin

5. **Face Exclusion**
   - Checkbox to exclude each face
   - When excluded: show velcro config options
   - Velcro width: configurable (default 3cm)

6. **Reinforcements**
   - Auto-detect high-stress areas
   - Add reinforcement patches
   - Configurable size

7. **Strap Placement**
   - Click to place strap
   - Two types: Klamra Camet / Grzechotka (ladder lock)
   - Visual preview

8. **Export**
   - DXF format
   - PDF with dimensions
   - SVG for plotting

### 3.2 User Flows

```
Welcome Window → Open STEP → Main Window (3D view)
                                       ↓
                              Click "Generuj plandekę"
                                       ↓
                              2D Pattern Window
                                       ↓
                              Configure straps/reinforcements
                                       ↓
                              Export
```

### 3.3 Data Structures

- **Face:** vertices, plane equation, area
- **Edge:** two vertices, two adjacent faces
- **Pattern:** list of 2D polygons with dimensions
- **Strap:** position, type, rotation
- **Reinforcement:** position, size

## 4. Acceptance Criteria

1. ✅ Welcome window opens on app start
2. ✅ Can load STEP file and display 3D model
3. ✅ Can rotate/zoom/pan 3D model
4. ✅ "Generuj plandekę" button in menu works
5. ✅ 2D pattern window shows after generation
6. ✅ Can place straps on 2D pattern
7. ✅ Seam allowance (1.5cm / 2.5cm) works
8. ✅ Can exclude faces with velcro option
9. ✅ Can export to DXF/PDF
10. ✅ All windows have proper menu/toolbar

## 5. Technical Stack

- **GUI:** PyQt6
- **3D:** PyQtGraph + OpenGL or custom OCCT display
- **STEP Parsing:** python-occ
- **2D Graphics:** PyQt6 QGraphicsScene
- **Math:** NumPy, SciPy
- **Export:** ezdxf, reportlab