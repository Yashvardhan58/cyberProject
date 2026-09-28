# UI/UX Design Document
## AI-Powered Adaptive UEBA -- React Dashboard

---

## 1. Design Principles

- Analyst-first: every design decision serves the security analyst's workflow
- Information density over decoration: no unnecessary animations or gradients
- Severity must be visually obvious at a glance (colour-coded throughout)
- Explanation text must look different from UI chrome -- use distinct typography

---

## 2. Color Palette (Tailwind CSS)

### Brand Colors
  Primary (Dark Blue):     #1E3A8A  (tailwind: blue-900)
  Accent (Medium Blue):    #2563EB  (tailwind: blue-600)
  Light Background:        #F1F5F9  (tailwind: slate-100)
  Card Background:         #FFFFFF  (tailwind: white)
  Border:                  #E2E8F0  (tailwind: slate-200)

### Severity Colors
  CRITICAL:  #DC2626  bg-red-600     text-white
  HIGH:      #EA580C  bg-orange-600  text-white
  MEDIUM:    #D97706  bg-amber-600   text-white
  LOW:       #16A34A  bg-green-600   text-white

### Score Gauge Colors
  0-30   (Low Risk):      #16A34A  green
  31-60  (Medium Risk):   #D97706  amber
  61-80  (High Risk):     #EA580C  orange
  81-100 (Critical Risk): #DC2626  red

### Neutral
  Text Primary:    #0F172A  slate-900
  Text Secondary:  #64748B  slate-500
  Divider:         #E2E8F0  slate-200

---

## 3. Typography

  Font Family:    Inter (Google Fonts) -- import in index.html
  Fallback:       system-ui, sans-serif

  Heading 1:      text-2xl font-bold text-slate-900     (page titles)
  Heading 2:      text-lg font-semibold text-slate-800  (section titles)
  Body:           text-sm text-slate-700                (standard text)
  Caption:        text-xs text-slate-500                (timestamps, labels)
  Monospace:      font-mono text-sm                     (feature names, scores)
  Explanation:    text-sm italic text-slate-700 leading-relaxed (LLM output text)

---

## 4. Layout System

  Sidebar width:     240px (fixed, left)
  Content area:      flex-1 (remaining width)
  Content max-width: 1280px (centered)
  Page padding:      p-6 (24px all sides)
  Card padding:      p-4 (16px all sides)
  Grid gap:          gap-4 (16px)

### Sidebar Navigation Items (top to bottom)
  [icon] Risk Dashboard
  [icon] Incident Timeline
  [icon] Analyst Feedback
  [icon] Admin Metrics
  ----separator----
  [icon] Settings (placeholder)

  Active state: bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600

---

## 5. Page Designs

---

### Page 1: Risk Dashboard  (route: /)

Layout: Two columns (left 60%, right 40%)

Left column:
  TOP RISK USERS LEADERBOARD
  - Table with columns: Rank | User | Role | Risk Score | Severity | Last Alert
  - Risk Score shown as coloured badge (red/orange/amber/green)
  - Clicking a row navigates to /users/:id
  - Paginated: 10 rows per page

Right column:
  RECENT ALERTS FEED
  - Vertical list of AlertCards
  - Each AlertCard shows: user name, severity badge, score, time ago, short reason
  - Clicking navigates to /alerts/:id/chat
  - Auto-refreshes every 30 seconds

Header bar (above both columns):
  - Total alerts today: [N]
  - Critical alerts: [N] (red)
  - New since last login: [N] (blue)

---

### Page 2: User Profile  (route: /users/:id)

Layout: Three sections stacked vertically

Section 1 -- User Header (full width)
  Left: user avatar initials circle (bg-blue-100 text-blue-700)
  Center: Name, Role, Department, Employee ID
  Right: Current Risk Score as large gauge (semicircle, 0-100)
  Gauge colour matches severity tier

Section 2 -- 30-Day Risk History (full width)
  Recharts LineChart
  X-axis: dates (last 30 days)
  Y-axis: risk score (0-100)
  Reference line at 60 (HIGH threshold) -- dashed orange
  Reference line at 80 (CRITICAL threshold) -- dashed red
  Tooltip shows: date, score, alert count

Section 3 -- Two columns

  Left: SHAP Feature Breakdown
  Horizontal bar chart (FeatureBar component)
  Top-5 features contributing to latest alert
  Positive SHAP = red bar (pushed score up)
  Negative SHAP = green bar (pushed score down)
  Feature names in monospace font

  Right: RECENT ALERTS for this user
  List of last 10 alerts, each showing severity and timestamp
  Each links to /alerts/:id/chat

---

### Page 3: Incident Timeline  (route: /timeline)

Layout: Full width table with filter bar at top

Filter bar:
  [Date range picker] [Severity dropdown] [User search box] [Apply button]

Table columns:
  Timestamp | User | Role | Severity | Risk Score | Top Feature | Action

Each row:
  - Timestamp formatted as: "2027-03-15 14:32" (monospace)
  - Severity as coloured badge
  - Top Feature: the #1 SHAP feature name
  - Action: [View Explanation] button -> navigates to ChatPanel

Pagination: 20 rows per page, page number shown

---

### Page 4: AI Chatbot Panel  (route: /alerts/:id/chat)

Layout: Two columns

Left column (40%) -- Alert Context Card
  Alert ID, User Name, Severity badge
  Risk Score (large number, colour-coded)
  Date/Time of alert
  ----divider----
  SHAP TOP 5 FEATURES (FeatureBar component)
  ----divider----
  7-DAY TREND SUMMARY
  Small Recharts LineChart showing 7-day score progression

Right column (60%) -- Chat Interface
  TOP: LLM Explanation Box
    Styled box (bg-blue-50 border border-blue-200 rounded-lg p-4)
    "AI Explanation" label in small caps
    Explanation text in italic, leading-relaxed typography
    "Generated by Claude API based on SHAP evidence only" -- small caption

  BELOW: Chat transcript
    Messages in bubble layout
    Analyst messages: right-aligned, bg-blue-600 text-white
    AI responses: left-aligned, bg-white border border-slate-200
    Timestamps below each bubble in text-xs text-slate-400

  BOTTOM: Input area
    Textarea (2 rows) + Send button
    Placeholder: "Ask a follow-up question about this alert..."
    Send button: bg-blue-600 hover:bg-blue-700 text-white

---

### Page 5: Analyst Feedback  (route: /feedback)

Layout: Full width

Header: "Alert Verdict Submission"
Subtitle: "Review alerts and mark each as True Positive or False Positive"

Table columns:
  Alert ID | User | Date | Severity | Risk Score | Verdict | Actions

Verdict column:
  - If no verdict: show [Mark TP] [Mark FP] buttons side by side
    TP button: bg-red-100 text-red-700 hover:bg-red-200
    FP button: bg-slate-100 text-slate-700 hover:bg-slate-200
  - If verdict submitted: show badge (TRUE POSITIVE or FALSE POSITIVE)

Filter: Show [All] [Pending] [TP] [FP] toggle buttons at top

---

### Page 6: Admin Metrics  (route: /admin/metrics)

Layout: Grid of cards

Row 1 -- Four metric cards (equal width)
  Card 1: Overall Precision (large number + label)
  Card 2: Overall Recall
  Card 3: F1 Score
  Card 4: AUC

Row 2 -- Two columns
  Left: Confusion Matrix (ConfusionMatrix component)
    2x2 grid showing: TP, FP, FN, TN
    TP cell: bg-green-100
    FP cell: bg-red-100
    FN cell: bg-orange-100
    TN cell: bg-slate-50

  Right: Experiment Results Table
    Columns: Experiment | Status | Key Result
    E1 | Complete | Best model: Hybrid (AUC: X.XXXX)
    E2 | Complete | Baseline contaminated at month N
    E3 | Complete | Detection rate maintained: XX%
    E4 | Complete | Drift classification accuracy: XX%
    E5 | Complete | Mean faithfulness score: X.XX

Row 3 -- Baseline Activity Chart
  BarChart (Recharts): baseline updates per week
  Suppressed updates shown in red, allowed updates in green

---

## 6. Shared Components

### RiskGauge
  Props: score (0-100), size (sm|md|lg)
  Renders: semicircle SVG gauge
  Colour: interpolates green -> amber -> orange -> red based on score
  Shows score number in center, severity label below

### AlertCard
  Props: alert object
  Renders: card with left severity border, user name, score badge, time
  Hover: slight shadow lift (hover:shadow-md transition-shadow)

### RiskChart
  Props: data (array of {date, score}), height
  Renders: Recharts LineChart with reference lines at 60 and 80

### FeatureBar
  Props: shapValues (array of {feature, value, direction})
  Renders: horizontal bar chart, red bars positive, green bars negative
  Feature names truncated to 20 chars with tooltip on hover

### ConfusionMatrix
  Props: tp, fp, fn, tn
  Renders: 2x2 table with coloured cells

### ChatMessage
  Props: role (user|assistant), content, timestamp
  Renders: bubble with appropriate alignment and colour

---

## 7. Recharts Configuration Conventions

All charts must:
  - Use ResponsiveContainer wrapper (width=100%, height as specified)
  - Use CartesianGrid with stroke="#E2E8F0" strokeDasharray="3 3"
  - Use XAxis with tick style: {fontSize: 11, fill: "#64748B"}
  - Use YAxis with tick style: {fontSize: 11, fill: "#64748B"}
  - Use Tooltip with contentStyle: {fontSize: 12, borderRadius: 6}
  - LineChart lines: strokeWidth=2, dot={r:3}

---

## 8. Loading & Error States

### Loading State
  Skeleton placeholder (animate-pulse bg-slate-200 rounded)
  Applied to: table rows, chart areas, card content

### Error State
  Red alert box: bg-red-50 border border-red-200 text-red-700 p-4 rounded
  Message: "Failed to load data. Please try again."
  Retry button: text-red-700 underline cursor-pointer

### Empty State
  Centered illustration placeholder (icon + message)
  Message: "No alerts found for this period."
