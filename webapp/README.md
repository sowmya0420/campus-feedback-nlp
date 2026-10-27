# Campus Facility Feedback Analysis System - Web Application

This web application is the presentation dashboard for NLP project on campus facility feedback. It features a compact, fully offline dark-mode dashboard with a persistent left sidebar. All pages load strictly from the final dataset outputs in `data/outputs/` and allow interactive exploration without page reloads.

---

## How to Run

Run this single command in PowerShell from the project root directory:

```powershell
.\venv\Scripts\python.exe webapp/app.py
```

Then open your browser and navigate to:

```text
http://127.0.0.1:5000
```

> **Note on Ollama**: Ensure Ollama is running (`ollama serve` or Ollama app in background) if you want real-time AI summaries on the Live Demo page. If Ollama is not running, the site automatically falls back to an auto-generated factual summary based strictly on the detected aspects.

---

## Dashboard Pages (7 Left Sidebar Links)

1. **Home (`/`)**: Executive overview with project title, 1-line plain description, 4 campus-wide KPI cards (800 comments, 8 facilities, 2.54 average rating, 49 quarantined comments), and a direct "Try it live" action button.
2. **Live Demo (`/demo` or `/submit`)**: Real-time evaluation of custom student feedback using the project's trained models in memory. Features:
   - "All facilities" default option with clause routing, carry-over, and hostel disambiguation.
   - Result table grouped to one row per aspect with sentiment badges, half-up rounded star ratings, and honest routing disclaimer.
   - Toxic-BERT abusive content check (0.50 threshold) evaluated once per comment.
   - Local Ollama AI summary generation with clean fallback.
3. **Facility Explorer (`/explorer`)**: Simple facility picker dropdown, overall rating, feedback count, top complaint area, recurring issues count, small Chart.js aspect rating chart, and scrollable aspect list.
4. **Aspect-wise Ratings (`/ratings`)**: Inner tabs switching between interactive benchmark chart (with 2.54 campus average reference line) and a sortable data table with instant text filtering.
5. **Recurring Issues (`/issues`)**: Inner tabs switching between ranked severity chart (horizontal bars) and expandable verified student comments filtered by a dynamic negative share threshold slider.
6. **Facility Briefs (`/briefs` or `/summaries`)**: Hand-corrected executive facility summaries directly from `summaries.csv`, with sortable facility tabs, rating badges, copy button, and side-by-side Compare Mode.
7. **Abusive Content (`/abusive` or `/flagged`)**: Moderation overview explaining the Toxic-BERT data integrity policy, distribution across facilities, and quarantined feedback table with safe truncated previews and expansion toggle.

---

## Design System & Offline Integrity

- **Dark Theme Palette**: Background `#0e1013`, sidebar `#13161b`, cards `#181b21`, raised `#1f232b`, borders `#2b303a`, text `#e8eaed`, muted text `#9aa3b0`, accent `#fb923c`, ratings green `#4ade80`, amber `#fbbf24`, red `#f87171`.
- **Fully Offline**: All static assets (Inter fonts, SVGs, Chart.js v4.4.7) are stored locally in `webapp/static/`. Zero external CDNs or online requests.
- **Read-Only Data Access**: Files in `data/outputs/` are strictly read-only.
