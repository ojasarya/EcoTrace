# 🌱 EcoTrace AI — Industrial Emissions Intelligence

**Find the emissions. Fix the process. Close the carbon loop.**

EcoTrace is an intelligent emissions monitoring and circular economy intervention platform designed for manufacturing facilities. It answers the critical question every industrial leader needs to know: **Where is my carbon coming from, and what should I do about it?**

*A Hackout 2026 Prototype*

---

## 📌 Problem Statement

Manufacturing industries face three challenges:

1. **Visibility Gap**: They don't know which processes contribute most to their emissions
2. **Decision Paralysis**: Too many potential interventions, unclear ROI and priority
3. **Circular Blindness**: Lack of actionable, cost-efficient, waste-reducing recommendations

Traditional carbon calculators answer *"How much?"* EcoTrace answers *"Where, why, what, and what if?"*

---

## 💡 Solution: The EcoTrace Approach

### The User Journey

Factory Data Input
↓
Data Validation & Normalization
↓
Emission Calculation (Activity × Emission Factor)
↓
Emission Breakdown by Category
↓
Hotspot Detection & Ranking
↓
Explain Why (Transparent Analysis)
↓
Circular Recommendations (Prioritized)
↓
Cost + CO₂ Comparison
↓
Carbon ROI Calculation
↓
What-If Simulation
↓
Prioritized Action Roadmap
↓
Progress Tracking & Reporting

---

## 🎯 Key Features

### 1. **Factory Data Input**

- Enter operational data: electricity consumption, raw materials, transportation, processes, waste
- Input validation with clear error messages
- **Load Demo Data** button for testing with illustrative data
- All data clearly labeled: *"Prototype Demonstration Data — Not Real Industrial Measurements"*

### 2. **Emission Calculation Engine**

- Centralized calculation system using: **Emissions = Activity × Emission Factor**
- Calculates emissions across 5 categories:
  - ⚡ Electricity
  - 📦 Raw Materials
  - 🚛 Transportation
  - 🏭 Processes
  - ♻️ Waste
- Transparent, configurable emission factors
- Prototype factors clearly distinguished from validated industry data

### 3. **Emission Analysis Dashboard**

- **Total Emissions**: Overall carbon footprint
- **Breakdown by Source**: Percentage contribution of each category
- **Trend Analysis**: Historical emissions vs. reduction targets
- **Emission Intensity**: kg CO₂e per unit of production

### 4. **Hotspot Detection & Analysis**

- **Automatic Ranking**: Categories sorted by calculated contribution
- **Severity Classification**: High, Moderate, Low severity labels
- **Dynamic Updates**: Hotspot ranking changes when factory data changes
- **Transparent Explanation**: Data-driven rationale for each hotspot

**Example Output:**

```text
1. Electricity — 4,200 kg CO₂e (42%) — High
2. Raw Materials — 2,500 kg CO₂e (25%) — High
3. Transportation — 1,500 kg CO₂e (15%) — Moderate
4. Processes — 1,000 kg CO₂e (10%) — Moderate
5. Waste — 800 kg CO₂e (8%) — Low
````

### 5. **Circular Recommendation Engine**

* **Intervention Knowledge Base**: ~25 circular economy recommendations across 4 categories:

  * **Materials**: Recycled material substitution, scrap reuse, material efficiency
  * **Energy**: Renewable electricity adoption, energy efficiency improvements
  * **Transportation**: Route optimization, load consolidation, lower-carbon alternatives
  * **Waste**: Waste reduction, material recovery, scrap reuse

* **Hotspot-Aware**: Recommendations prioritized based on actual hotspot analysis

* **Rich Metadata**:

  * Target emission source
  * Estimated CO₂ reduction (kg CO₂e)
  * Implementation cost (₹)
  * Feasibility (High/Medium/Low)
  * Implementation timeline
  * Waste reduction benefit
  * Difficulty level

### 6. **Carbon ROI Analysis**

* **Formula**: CO₂ Reduction ÷ Implementation Cost = Carbon ROI
* **Human-Readable Metric**: kg CO₂e avoided per ₹1,000 invested
* **Cost-Benefit Visualization**: Compare investment vs. climate impact
* **Payback Period**: Estimated time to recover investment

**Example:**

```text
Initiative: 30% Recycled Material Substitution
CO₂ Reduction: 2,100 kg CO₂e/month
Cost: ₹150,000
Carbon ROI: 0.014 kg CO₂e/₹
Payback: ~24 months
Feasibility: High
```

### 7. **What-If Simulator**

* **Interactive Scenario Planning**: Adjust 5 key levers (0–100% each):

  * Recycled material substitution
  * Renewable energy adoption
  * Transport optimization
  * Waste reduction
  * Efficiency improvements

* **Real-Time Calculation**: Scenario emissions update dynamically

* **Clear Comparison**: Current State vs. Scenario State

* **Impact Breakdown**: Category-level emissions changes

**Example:**

```text
CURRENT STATE
Total Emissions: 10,000 kg CO₂e/month

SCENARIO (with 50% intervention mix)
Total Emissions: 7,900 kg CO₂e/month
Reduction: 2,100 kg CO₂e/month (21%)

BY CATEGORY
Electricity: 3,500 → 3,150 kg CO₂e
Materials: 2,500 → 1,500 kg CO₂e
Transportation: 1,500 → 1,300 kg CO₂e
Processes: 1,000 → 950 kg CO₂e
Waste: 800 → 700 kg CO₂e
```

### 8. **Prioritization Engine**

* **Transparent Scoring**: 0–100 score based on:

  * Emission impact (hotspot importance)
  * CO₂ reduction potential
  * Cost efficiency (Carbon ROI)
  * Technical feasibility
  * Implementation complexity
  * Waste reduction co-benefit

* **Score Justification**: Rationale explained for every recommendation

* **Dynamic Ranking**: Scores update when factory data or hotspots change

**Example:**

```text
Priority Score: 92/100

Reasons:
✓ High emission impact (target hotspot)
✓ Strong reduction potential (2,100 kg CO₂e)
✓ Good cost efficiency (high Carbon ROI)
✓ High feasibility
✓ Reasonable implementation cost
✓ Waste reduction benefit
```

### 9. **Action Roadmap**

* **Prioritized Timeline**: Ranked initiatives with clear timelines
* **Status Tracking**: Not Started → Planned → In Progress → Completed
* **Cumulative Impact**: Track total CO₂ reduction progress
* **Implementation Planning**: Milestone dates and dependencies

**Roadmap Display:**

| Rank | Initiative             | Target      | Reduction | Cost  | ROI   | Timeline | Status      |
| ---- | ---------------------- | ----------- | --------- | ----- | ----- | -------- | ----------- |
| 1    | Recycled materials     | Materials   | 2,100 kg  | ₹150K | 0.014 | 0–3 mo   | Planned     |
| 2    | Energy efficiency      | Electricity | 1,400 kg  | ₹90K  | 0.016 | 1–6 mo   | In Progress |
| 3    | Transport optimization | Transport   | 620 kg    | ₹42K  | 0.015 | 0–2 mo   | Not Started |
| 4    | Metal scrap recovery   | Waste       | 480 kg    | ₹28K  | 0.017 | 0–1 mo   | Not Started |

### 10. **Reporting & Analytics**

* **Monthly Emissions Report**: Detailed breakdown and trends
* **Hotspot Analysis**: Deep dive into top emission sources
* **Recommendation Summary**: Prioritized action plan
* **Progress Tracking**: Completed vs. planned initiatives
* **Export Functionality**: Share with stakeholders

---

## 🏭 Sample Demonstration Data

The application includes prototype demonstration data for **Acme Manufacturing** (Ahmedabad Plant):

**Current State: 10,000 kg CO₂e/month**

| Source         | Emissions | %   | Trend  | Severity |
| -------------- | --------- | --- | ------ | -------- |
| Electricity    | 4,200     | 42% | ↑ +11% | High     |
| Raw Materials  | 2,500     | 25% | ↑ +4%  | High     |
| Transportation | 1,500     | 15% | ↓ -2%  | Moderate |
| Processes      | 1,000     | 10% | ↑ +1%  | Moderate |
| Waste          | 800       | 8%  | ↓ -8%  | Low      |

**Recommended Interventions:**

* 30% recycled material substitution → **-2,100 kg CO₂e** (~2 years payback)
* Energy efficiency optimization → **-1,400 kg CO₂e** (~14 months payback)
* Transport route optimization → **-620 kg CO₂e** (~18 months payback)
* Metal scrap monetization → **-480 kg CO₂e** (~9 months payback)

**⚠️ Prototype Notice**: This demonstration data is illustrative only and does not represent real industrial measurements. All values are estimates for demonstration purposes.

---

## 🛠️ Technology Stack

### Frontend

* **React** 18.3.1 — UI framework
* **TypeScript** 5.6.3 — Type-safe development
* **Vite** 6.0.5 — Lightning-fast build tool
* **React Router** 7.18.3 — Client-side routing
* **Recharts** 2.13.3 — Data visualization
* **Lucide React** 0.468.0 — Icon library

### Architecture

* **Component-Driven**: Modular, reusable React components
* **Calculation Engine**: Centralized business logic separate from UI
* **Type-Safe**: Full TypeScript coverage
* **Responsive Design**: Works on desktop and tablet
* **No Backend Required**: Client-side calculations for rapid prototyping

---

## 📁 Project Structure

```text
EcoTrace/
├── src/
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # React entry point
│   ├── data.ts                 # Data models, types, and sample data
│   ├── utils.ts                # Utility functions and calculations
│   └── styles.css              # Global styling and theming
├── index.html                  # HTML entry point
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

### Key Files Explained

* **`App.tsx`** (90 lines, heavily condensed)

  * All React components: Shell, pages, utilities, charts
  * Contains: Overview, FactoryData, Emissions, Hotspots, Recommendations, Simulator, Roadmap, Reports, Settings
  * Chart components: Donut (emissions by source), Sparkline (trend), TrendChart

* **`data.ts`** (36 lines)

  * TypeScript types: `Source`, `Recommendation`, `RoadmapItem`, `RoadmapStatus`
  * Sample data: `sources`, `trend`, `recommendations`, `initialRoadmap`
  * Emission factors and sample values
  * INR formatting utility

* **`utils.ts`** (10 lines)

  * `calculateScenario()`: What-if simulator logic
  * `calculateEmissionIntensity()`: Emission per unit of production
  * Reduction and cost calculations

* **`styles.css`** (358 lines)

  * Root CSS variables (colors, spacing)
  * Component styles: sidebar, topbar, cards, badges
  * Layout grid for dashboard
  * Responsive breakpoints for mobile and tablet
  * Chart and visualization styling

---

## 🚀 Getting Started

### Prerequisites

* **Node.js** 16.0.0 or later
* **npm** 7.0.0 or later (or yarn/pnpm)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ojasarya/EcoTrace.git
   cd EcoTrace
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Start the development server**

   ```bash
   npm run dev
   ```

   The app will open at `http://localhost:5173`

### Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type check
npx tsc --noEmit
```

---

## 📖 Usage Guide

### Quick Start Workflow

1. **Landing Page** (`/`)

   * Overview of EcoTrace
   * Call-to-action: "Get Started"

2. **Dashboard** (`/dashboard`)

   * View your facility's current emissions profile
   * See total emissions and breakdown by source
   * Identify the largest hotspot at a glance
   * Check emission trends

3. **Factory Data** (`/factory-data`)

   * Enter operational data:

     * Electricity consumption (kWh/month)
     * Raw materials used (units/month)
     * Transportation distance (km/month)
     * Process activity levels
     * Waste generation (units/month)
   * Click "Load Demo Data" to see sample values
   * Edit values and click "Calculate Emissions"

4. **Emissions Analysis** (`/emissions`)

   * Detailed breakdown of calculated emissions
   * Category-level analysis
   * Intensity metrics
   * Trend comparison

5. **Hotspots** (`/hotspots`)

   * Ranked list of emission sources
   * Severity indicators
   * Explanation of each hotspot
   * Why is this high? → Data-driven rationale

6. **Recommendations** (`/recommendations`)

   * Circular economy interventions
   * Filtered by category or priority
   * Details: CO₂ reduction, cost, ROI, feasibility
   * Add to roadmap

7. **Simulator** (`/simulator`)

   * Adjust intervention levers (0–100% each)
   * Watch emissions recalculate in real-time
   * Compare current vs. scenario
   * Explore different reduction strategies

8. **Roadmap** (`/roadmap`)

   * Prioritized action plan
   * Timeline and status tracking
   * Cumulative reduction impact
   * Update initiative status

9. **Reports** (`/reports`)

   * Generate monthly reports
   * Export data for stakeholders
   * Track progress over time

10. **Settings** (`/settings`)

    * Workspace configuration
    * Facility profile
    * Analysis preferences

---

## 🔍 How It Works

### 1. Emission Calculation

```text
Emissions = Activity Data × Emission Factor
```

For each category:

* **Electricity**: kWh × 0.73 kg CO₂e/kWh = Electricity Emissions
* **Materials**: units × specific factor = Material Emissions
* **Transportation**: km × factor = Transport Emissions
* **Processes**: activity × factor = Process Emissions
* **Waste**: units × factor = Waste Emissions

**Total Emissions** = Sum of all categories

### 2. Hotspot Analysis

```text
Hotspot Severity = (Category Emissions / Total Emissions) × 100
```

Categories ranked by percentage contribution:

* **High**: > 30%
* **Moderate**: 15–30%
* **Low**: < 15%

Rankings update dynamically when factory data changes.

### 3. Recommendation Prioritization

```text
Priority Score = (Impact Weight × Impact) 
               + (ROI Weight × Carbon ROI) 
               + (Feasibility Weight × Feasibility)
               + (Complexity Weight × Complexity)
               + (Waste Weight × Waste Benefit)
```

Recommendations are:

* **Sorted** by priority score
* **Filtered** by target hotspot relevance
* **Ranked** by urgency and impact

### 4. What-If Simulation

```text
Scenario Emissions = Base Emissions × (1 - Intervention Reduction %)
```

Each lever reduces specific categories:

* **Recycled Materials**: Reduces raw materials by up to 25%
* **Renewable Energy**: Reduces electricity by up to 22%
* **Transport Opt**: Reduces transportation by up to 8%
* **Waste Reduction**: Reduces waste by up to 6%
* **Efficiency**: Reduces processes by up to 19%

All changes visualized in real-time.

---

## 🎨 Design Philosophy

**Clean, Professional, Industrial**

* Eco-friendly color palette (greens, earth tones)
* Clear information hierarchy
* Card-based layouts for clarity
* Dark sidebar for focus
* Responsive design for all devices
* Accessible controls and labels

---

## ⚠️ Important Disclaimers

### Prototype Status

* EcoTrace is a **prototype** created for Hackout 2026
* Not intended for regulatory compliance
* Demonstration data is illustrative only

### Emission Factors

* All factors are **estimates for demonstration**
* Replace with validated industry-specific factors for real use
* Factors clearly labeled as "Prototype Estimates"

### Calculations

* All calculations are based on simplified formulas
* Real industrial emissions require:

  * Validated emissions factors
  * Scope 1, 2, 3 analysis
  * GHG Protocol compliance
  * Third-party verification

### Not Included

* IoT/sensor integration
* Real-time industrial measurements
* Blockchain or certification
* Hardware integration
* Unnecessary authentication

This is a **software-only solution** focused on decision support.

---

## 🎯 Core Differentiators

| Question                   | Generic Calculator | EcoTrace AI      |
| -------------------------- | ------------------ | ---------------- |
| How much carbon do I emit? | ✓                  | ✓                |
| Where is it coming from?   | ✗                  | ✓                |
| Why is it high?            | ✗                  | ✓                |
| What can I do?             | Limited            | ✓ Circular Focus |
| How much will it cost?     | ✗                  | ✓                |
| What's the return?         | ✗                  | ✓ Carbon ROI     |
| What if I change this?     | ✗                  | ✓ Interactive    |
| What should I do first?    | ✗                  | ✓ Prioritized    |

---

## 🔄 Complete User Journey Test

Test the full workflow:

1. ✅ Open app, see landing page
2. ✅ Navigate to dashboard
3. ✅ Go to factory data
4. ✅ Click "Load Demo Data"
5. ✅ See data populated
6. ✅ Edit a value (e.g., electricity)
7. ✅ Click "Calculate"
8. ✅ Navigate to emissions analysis
9. ✅ Verify emissions changed
10. ✅ Go to hotspots
11. ✅ Verify rankings changed
12. ✅ Read explanation
13. ✅ Go to recommendations
14. ✅ Review cost + CO₂
15. ✅ Check Carbon ROI
16. ✅ Open simulator
17. ✅ Move a slider
18. ✅ Verify emissions recalculate
19. ✅ Verify reduction displays
20. ✅ Add recommendation to roadmap
21. ✅ View roadmap
22. ✅ See prioritized actions
23. ✅ No console errors
24. ✅ Responsive on mobile

---

## 🌍 Environmental Impact

Through EcoTrace, manufacturers can:

* **Identify** the largest emission sources in minutes
* **Evaluate** ~25 circular economy interventions
* **Prioritize** actions by CO₂ impact and ROI
* **Plan** implementations with clear timelines
* **Reduce** emissions by up to 4,600+ kg CO₂e/month
* **Achieve** payback on green investments in 9 months to 2 years
* **Track** progress toward reduction targets
* **Report** transparently to stakeholders

---

## 🤝 Contributing

This is a Hackathon prototype. 

### Areas for Enhancement

* Replace prototype factors with validated industry data
* Add Scope 3 (supply chain) emissions
* Integrate with real production ERP systems
* Add multi-facility support
* Implement data persistence (database)
* Add advanced ML for anomaly detection
* Create mobile app version

---

## 📄 License

This project is created for Hackout 2026. All rights reserved.

---

## 📧 Support & Feedback

**Hackout 2026 Submission**

Created by: [TheDots](https://github.com/ojasarya)

**Repository**: [https://github.com/ojasarya/EcoTrace](https://github.com/ojasarya/EcoTrace)

---

## 🎯 Key Takeaway

**EcoTrace transforms industrial emissions from a mystery into actionable intelligence.**

Most facilities know *how much* they emit. **EcoTrace helps them understand why, what to do, and how much it will help.**

This is the difference between a carbon calculator and a decision-making platform.

---

**Find the emissions. Fix the process. Close the carbon loop.** 🌱

```

### One important thing I corrected

I changed the **User Journey flow** from a fenced code block into plain Markdown text with arrows. This avoids the README looking like a giant programming code section.

Everything that actually needs monospaced formatting—**terminal commands, formulas, examples, and project structure**—remains in proper code blocks.

**For GitHub:** copy everything *inside* the large block above into your `README.md`. Do **not** copy the very first and very last triple backticks.
```
 