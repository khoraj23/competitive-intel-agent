# Adoption UX Flow: Competitive Intelligence Agent

Designed for a non-technical merchandising manager. Ready for Figma translation.

---

## User Persona

**Name**: Sarah, Senior Merchandising Manager
**Context**: Runs competitive reviews quarterly. Currently does this manually — opens competitor sites in tabs, takes notes in a Google Doc, spends half a day on it. Wants to go from 4 hours to 15 minutes.

---

## Flow

### Screen 1: Entry Point

**Trigger**: User opens their internal tools dashboard (or Claude Code CLI).

```
┌─────────────────────────────────────────────┐
│                                             │
│  🔍 What would you like to do?              │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ /competitive-intel                    │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Recent:                                    │
│  • Q4 Analysis: West Elm vs CB2  (Dec 15)   │
│  • Q3 Analysis: West Elm vs RH   (Sep 12)   │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Slash command as primary input (power users)
- Recent runs shown below for quick re-runs
- Could also be triggered from a button in a dashboard wrapper

---

### Screen 2: Configuration

**After typing `/competitive-intel`, the agent prompts for inputs.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  Competitive Intelligence Agent             │
│  ─────────────────────────────              │
│                                             │
│  Competitor A                               │
│  ┌───────────────────────────────────────┐  │
│  │ westelm.com                           │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Competitor B                               │
│  ┌───────────────────────────────────────┐  │
│  │ cb2.com                               │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Focus Areas                                │
│  ☑ Homepage Messaging & Visual Hierarchy    │
│  ☑ Promo Placement & Offers                 │
│  ☑ Product Discovery                        │
│  ☑ AI-Powered Features                      │
│                                             │
│  Pages to Analyze                           │
│  ☑ Homepage                                 │
│  ☑ Category / Listing Page                  │
│  ☐ Product Detail Page                      │
│  ☐ Search Results                           │
│                                             │
│         [ Cancel ]     [ Run Analysis → ]   │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Pre-filled defaults for common analysis (all 4 focus areas, homepage + category)
- Checkboxes let user customize scope without needing to learn syntax
- "Pages to Analyze" controls scraping depth (more pages = longer runtime)
- URL inputs could have autocomplete from previous runs

---

### Screen 3: Progress

**Agent is running. User sees real-time progress.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  Analyzing West Elm vs CB2                  │
│  ─────────────────────────────              │
│                                             │
│  ✅ Capturing westelm.com homepage          │
│  ✅ Capturing cb2.com homepage              │
│  ✅ Capturing westelm.com/sofas             │
│  ✅ Capturing cb2.com/furniture/sofas       │
│  ⏳ Extracting structured data...           │
│  ○ Synthesizing comparison                  │
│  ○ Cross-validating claims                  │
│  ○ Generating report                        │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ ████████████████░░░░░░  65%           │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Estimated: ~2 min remaining                │
│                                             │
│              [ Cancel Run ]                 │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Steps map directly to pipeline stages from the workflow spec
- Parallel captures shown completing together
- Progress bar gives time estimate based on scope selected
- Cancel available at any point
- If a capture fails, show inline: `⚠️ westelm.com blocked — requesting screenshot fallback` with a prompt for user to provide screenshot

---

### Screen 4: Human-in-the-Loop (Conditional)

**Shown only if automated capture fails and screenshot is needed.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  ⚠️  Manual capture needed                 │
│  ─────────────────────────────              │
│                                             │
│  cb2.com blocked our automated capture.     │
│  Please provide a screenshot:               │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │                                       │  │
│  │     📎 Drag screenshot here           │  │
│  │        or click to upload             │  │
│  │                                       │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  How to capture:                            │
│  1. Open cb2.com in Chrome                  │
│  2. Cmd+Shift+P → "full size screenshot"    │
│  3. Drop the file above                     │
│                                             │
│         [ Skip this site ]  [ Continue → ]  │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Clear instructions so non-technical users can provide the fallback data
- "Skip this site" lets them proceed with partial analysis rather than blocking
- This screen is the key trust-builder — it shows the agent knows its limits

---

### Screen 5: Draft Review

**Analysis complete. User reviews before distribution.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  ✅ Analysis Complete                       │
│  ─────────────────────────────              │
│                                             │
│  ┌───────────────────────────────────────┐  │
│  │ Executive Summary                     │  │
│  │                                       │  │
│  │ • West Elm leads with lifestyle       │  │
│  │   mood; CB2 leads with editorial      │  │
│  │   authority                           │  │
│  │ • Neither brand deploys visible AI    │  │
│  │   features — first-mover lane open    │  │
│  │ • West Elm's cross-brand ecosystem    │  │
│  │   is a structural advantage CB2       │  │
│  │   can't replicate                     │  │
│  │                                       │  │
│  │ ✅ Cross-validation: 2/2 claims       │  │
│  │    verified                           │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Full Report Preview ▾                      │
│  ┌───────────────────────────────────────┐  │
│  │ [Scrollable markdown preview of       │  │
│  │  competitive-analysis.md]             │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  [ ✏️ Edit ]  [ 🔄 Re-run ]  [ ✅ Approve ]│
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Executive summary shown first — most users won't read the full report inline
- Cross-validation status prominently displayed (trust signal)
- "Edit" opens the markdown in an editor for manual tweaks
- "Re-run" sends the agent back through the pipeline (useful if user wants to adjust focus areas)
- "Approve" triggers distribution (next screen)

---

### Screen 6: Distribution

**After approval, user chooses where to send the report.**

```
┌─────────────────────────────────────────────┐
│                                             │
│  Distribute Report                          │
│  ─────────────────────────────              │
│                                             │
│  Save to:                                   │
│  ☑ Google Drive → /Competitive Intel/Q1     │
│  ☑ Local file   → work/pm-exercise/        │
│                                             │
│  Notify:                                    │
│  ☑ Slack → #merchandising-team              │
│  ☐ Email → team distribution list           │
│                                             │
│  Include:                                   │
│  ☑ Full analysis report                     │
│  ☐ Prompt log (for reproducibility)         │
│  ☐ Raw screenshots                          │
│                                             │
│         [ Back ]        [ Send → ]          │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Pre-configured destinations from previous runs
- Slack notification includes the exec summary inline (not just a link)
- Prompt log and raw data optional — most stakeholders only want the report
- "Back" returns to edit/review without losing distribution config

---

### Screen 7: Confirmation

```
┌─────────────────────────────────────────────┐
│                                             │
│  ✅ Report distributed                      │
│                                             │
│  • Saved to Google Drive                    │
│  • Posted to #merchandising-team            │
│                                             │
│  Schedule next run?                         │
│  [ Monthly ]  [ Quarterly ]  [ Not now ]    │
│                                             │
└─────────────────────────────────────────────┘
```

**UX notes**:
- Scheduling prompt seeds the recurring use case
- Reduces friction for the user to make this a habit vs. a one-off

---

## End-to-End Journey Summary

| Step | User Action | System Response | Time |
|---|---|---|---|
| 1. Trigger | Types `/competitive-intel` | Shows configuration screen | 0s |
| 2. Configure | Enters URLs, selects focus areas | Validates inputs | ~30s |
| 3. Wait | Watches progress | Parallel scrapes → extraction → synthesis | ~3-5 min |
| 4. Fallback | Uploads screenshot (if needed) | Resumes pipeline | ~1 min |
| 5. Review | Reads exec summary, previews report | Shows draft with validation status | ~2 min |
| 6. Approve | Clicks Approve | Proceeds to distribution | 0s |
| 7. Distribute | Selects destinations, clicks Send | Saves + notifies | ~10s |
| **Total** | | | **~5-8 min** |

**vs. manual process: ~4 hours** — a 30-50x reduction.

---

## Figma Implementation Notes

- **Color palette**: Neutral grays + one accent color for progress/success states
- **Typography**: Monospace for the CLI-native version; system sans-serif for dashboard wrapper
- **Key components to build**: Input form, progress stepper, markdown preview card, distribution checklist, confirmation toast
- **Responsive**: Desktop-first (this is a work tool), but progress screen should work on mobile for checking status on the go
- **Accessibility**: All interactive elements keyboard-navigable; progress updates announced to screen readers
