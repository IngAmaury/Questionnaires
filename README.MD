# 🚗📝 Driver Study Questionnaires GUI

A friendly PyQt6 application to collect questionnaires during driving-simulator experiments.
It guides the participant through an initial battery and then repeated inter-stage blocks, saving every answer to a CSV file (UTF-8).

## 📍Overview

This app shows large fonts and radio buttons to speed up data entry.
It follows this sequence:
- Initial(once):
    1. Beck Anxiety Inventory (BAI)
    2. Perceived Stress Scale (PSS-14, with the inverted items handled automatically)
    3. Positive and Negative Affect Schedule (PANAS) (short Spanish version, 20 items)
- Inter-stage blocks (e.g., between protocol phases, repeat as many times as needed):
    1. Self-Assessment Manikin (SAM-Emotion) for Valence, Arousal, Dominance (1–9).
        - One horizontal image per dimension shown above the options.
        - If your arousal image is reversed (high arousal on the left), the app maps scores so that 1 = calm and 9 = highly aroused.
    2. Stress Appraisal Measure (SAM–Stress) subset: items 2, 5, 8, 14, 20, 16, 22, 19, 24, 26 (0–4).
Every response is appended immediately to "respuestas_cuestionarios.csv" (one row per item).

## 🛠️ Features
### 🔹 Main Features
- Big UI: large fonts, clear radio buttons, images for SAM.
- Sectioned flow: initial battery, then repeatable blocks with transition messages.
- Robust saving: answers are written row-by-row to a CSV with UTF-8 BOM (Excel-friendly).
- PSS scoring: inverted items (4, 5, 6, 7, 9, 10, 13) are auto-reversed.
- SAM images: fixed size, centered; radio buttons can be overlaid on the images to save space.
- Participant & stage metadata: each row includes timestamp, participant ID, block number, and stage label.

### 🔹 CSV Schema
- Columns: timestamp, participant_id, block_id, stage_label, instrument, item_code, item_text, response, score
- Example instruments: BAI, PSS, PSS_TOTAL, PANAS, SAM_Manikin, SAM_Stress.

### 🔹 Add a new questionnarie (quick guide)
Add the follow in the code inside "cuestionarios.py":
1. Create an item list: NEWQ_ITEMS = ["Question 1", "Question 2", ...].
2. Create options as (label, score) tuples, for example:
```python
NEWQ_OPTIONS = [("Never",0), ("Rarely",1), ("Often",2), ("Always",3)]
```
3. Instantiate a QuestionGroup (or subclass if special scoring is needed):
```python
self.newq = QuestionGroup(
    "My New Questionnaire",
    NEWQ_ITEMS, NEWQ_OPTIONS,
    self.pid, self.block, self.stage,
    item_prefix="NEWQ_",
    instructions="Answer according to your current feeling."
)
```
4. Insert it in the flow where you want (before/after other pages).
5. Special scoring? Override save_to_csv() in a subclass (like PSSWidget does).
[!TIP]
> Tip: keep items and options in separate constants for easier maintenance and translations.

## 💻 Requirements
* Python 3.9–3.12
* PyQt6 (UI)
* Pillow (optional, only if you later add image processing; not required now) 

## 🎌 Getting Started

📁 **Folder structure**

```bash
project/
├─ cuestionarios_gui.py
├─ respuestas_cuestionarios.csv        # auto-created on first run
└─ Sources/                            # SAM images used in the UI
   ├─ valence_scale.jpg
   ├─ arousal_scale.png
   └─ dominance_scale.png
```
> [!NOTE]
> Use your own images; the app scales them to a uniform size. If an image is missing, a warning text appears instead.

🏃‍♂️‍➡️ **Run**

Use your favorite IDE to run the Python file "cuestionarios.py", or run it in the terminal from the folder where you downloaded the repository, like this:
```python
python cuestionarios.py
```
At start up:
1. Enter Participant ID (free text).
2. Enter Stage label (e.g., “Baseline”, “Stage 1”, “Route 2”).
3. Choose Block # (1..n).
4. Click Initial evaluation or Inter-stage block.

## 🕹️ Usage
- Initial evaluation runs BAI → PSS → PANAS.
    - You must answer all items in a page to continue.
    - PSS scores are stored already corrected (inverted items handled internally).
    - A final “Thank you” screen returns you to the start page.
- Inter-stage block runs SAM (Valence, Arousal, Dominance) + SAM–Stress subset.
    - SAM scale is 1–9. If your arousal image is reversed (high arousal drawn on the left), the app maps options so that scores remain consistent (1 = calm, 9 = activated).
    - The radio buttons may be drawn on top of the image to save vertical space.
- CSV output is written after each “Next” click. Encoding is UTF-8 with BOM so Excel shows accents correctly.
    - If you open the CSV manually in Excel and still see strange characters, import via Data → From Text/CSV → UTF-8.

- Shortcuts for customization:
    - Font size: change BIG_FONT, TITLE_FONT, BTN_FONT.
    - SAM image size: edit self.SCALE_W, self.SCALE_H in SAMManikinWidget.
    - Instructions text & alignment: pass instructions=... and instr_align=... to QuestionGroup, or add a QLabel under the page title (as done for SAM).
    - Messages between blocks: edit the text in the transition pages.

## 🔎 Test results interpretations

The system saves each response and adds summary rows per instrument in the CSV with the following columns:

```bash
timestamp, participant_id, block_id, stage_label, instrument, item_code, item_text, response, score
```

In the answers per item, *response* is the chosen label and *score* is the numerical value.
In the summary rows (or score sum), *response* usually contains the interpretation (in English) and *score* the total (or the normalized value in SAM-stress, see below).

---

### BAI — Beck Anxiety Inventory
- Scale per item: 0–3
- Total: sum of 21 ítems → range 0–63.
- Interpretation:
    - 0–7 → Minimal anxiety
    - 8–15 → Mild anxiety
    - 16–25 → Moderate anxiety
    - 26–63 → Severe anxiety
- CSV (summary):
    - instrument=BAI_SUMMARY, item_code=total, item_text=Total (0–63), response=<interpretación>, score=<suma>

--- 

### PSS — Perceived Stress Scale (14 items)
- Scale per ítem: 0–4
- Reversed items : 4, 5, 6, 7, 9, 10, 13 (scored as 4-0).
- Total: sum of 14 items (with reversal already applied) → range 0–56.
- Interpretation:
    - 0–18 → Low stress
    - 19–37 → Moderate stress
    - 38–56 → High stress
- CSV (summary):
    - instrument=PSS_TOTAL, item_code=sum, item_text=Suma de 14 ítems, response=<interpretación>, score=<suma>

---

### PANAS — Positive and Negative Affect Schedule (short form)

- Per-item scale: 1–5
- Subscales (10 items each):
    - Positive Affect (PA) — in the app these items are labeled (Spanish): Motivado/a, Emocionado/a, Firme, Entusiasmado/a, Estar orgulloso/a, Alerta, Inspirado/a, Decidido/a, Estar atento/a, Activo/a.
    - Negative Affect (NA) — in the app these items are labeled (Spanish): Molesto/a, De malas, Culpable, Temeroso/a, Agresivo/a, Irritable, Avergonzado/a, Nervioso/a, Inquieto/a, Inseguro/a.
- Totals and ranges:
    - PA_sum = sum of PA items (range 10–50)
        - 10–25 → Low · 26–35 → Moderate · 36–50 → High
    - NA_sum = sum of NA items (range 10–50)
        - 10–25 → Low · 26–35 → Moderate · 36–50 → High
    - PA_minus_NA = PA_sum − NA_sum (range −40…+40)
        - < 0 → Negative · = 0 → Balanced · > 0 → Positive
- Overall label (1–2 words, English):
    - PA High + NA Low → Optimal
    - PA Low + NA High → Distress
    - PA High + NA High → Ambivalent
    - PA Low + NA Low → Blunted affect
    (If none of the four patterns matches cleanly, the balance is used: Positive, Balanced, or Negative.)
- CSV (summary rows):
    - instrument=PANAS_SUMMARY, item_code=PA_sum, item_text=Positive Affect (sum 10 items), response="", score=<PA_sum>
    - instrument=PANAS_SUMMARY, item_code=NA_sum, item_text=Negative Affect (sum 10 items), response="", score=<NA_sum>
    - instrument=PANAS_SUMMARY, item_code=PA_minus_NA, item_text=Balance (PA - NA), response="", score=<PA-NA>
    - instrument=PANAS_SUMMARY, item_code=PA_cat|NA_cat|Balance_cat, response=<Low/Moderate/High or Balance>, score=""
    - instrument=PANAS_SUMMARY, item_code=Overall, item_text=Overall affective state, response=<Optimal/Distress/Ambivalent/Blunted affect/...>, score=""

---

### SAM-Manikin — Valence / Arousal / Dominance

- Per-dimension scale: 1–9 (the midpoint is 5).
- Quadrant (Valence–Arousal) and emotion:
    - V=5 & A=5 → Q0, Neutral
    - V>5 & A>5 → Q1, Elated
    - V<5 & A>5 → Q2, Anxious/tense
    - V<5 & A<5 → Q3, Tired/sadness
    - V>5 & A<5 → Q4, Calm
    - V>5 & A=5 → Q1/Q4, Happy
    - V=5 & A>5 → Q1/Q2, Aroused
    - V<5 & A=5 → Q2/Q3, Unhappy
    - V=5 & A<5 → Q3/Q4, Quiet

- CSV (summary rows):
    - instrument=SAM_Manikin_SUMMARY, item_code=quadrant, item_text=Quadrant by Valence–Arousal, response=<Q...>, score=""
    - instrument=SAM_Manikin_SUMMARY, item_code=interpretation, item_text=Emotion, response=<emotion>, score=""

---

### SAM-Stress — Subscales and normalization

- Items used: 2, 5, 8, 14, 20, 16, 22, 19, 24, 26.
- Per-item scale: 0–4.
- Raw sums and categories:
    - Stress = 2 + 16 + 24 + 26 → range 0–16
        - 0–5 → Low stress · 6–10 → Moderate stress · 11–15 → High stress
    - Threat = 2 + 5 → range 0–8
        - 0–2 → Low threat · 3–5 → Moderate threat · 6–8 → High threat
    - Challenge = 8 + 19 → range 0–8
        - 0–2 → Low challenge · 3–5 → Moderate challenge · 6–8 → High challenge
    - Controllable-by-self = 14 + 22 → range 0–8
        - 0–2 → Low controllable-by-self · 3–5 → Moderate controllable-by-self · 6–8 → High controllable-by-self
-    Normalization (applied in CSV): each summary score is stored normalized to [0, 1] by dividing by the subscale’s maximum. The category is computed before normalization and written in response.
    - stress_level: score = (Q2+Q16+Q24+Q26) / 16
    - threat_sum: score = (Q2+Q5) / 8
    - challenge_sum: score = (Q8+Q19) / 8
    - ctrl_self_sum: score = (Q14+Q22) / 8
- CSV (summary rows):
    - instrument=SAM_Stress_SUMMARY, item_code=stress_level, item_text=Stress Score, response=<Low/Moderate/High stress>, score=<sum/16>
    - instrument=SAM_Stress_SUMMARY, item_code=threat_sum, item_text=Threat Score, response=<Low/Moderate/High threat>, score=<sum/8>
    - instrument=SAM_Stress_SUMMARY, item_code=challenge_sum, item_text=Challenge Score, response=<Low/Moderate/High challenge>, score=<sum/8>
    - instrument=SAM_Stress_SUMMARY, item_code=ctrl_self_sum, item_text=Ctrl-self score,response=<Low/Moderate/High controllable-by-self>, score=<sum/8>

---

## 📕 Language
- The UI and questionnaires are currently in Spanish.
- You can translate items or add new language versions by duplicating the item lists.

## 📜 License
This project’s **source code** is licensed under the **MIT License**.  
Copyright © 2025 Amaury Santiago Horta.
See the [LICENSE](LICENSE) file for details.

> **Note:** The work’s title and branding — “Formulario de Estrés y Emociones Reportado (FEER)” and “FEER” — are claimed as trademarks (™) and are **not** covered by the MIT License.

## 🔖 Work Title & Naming Notice

The work is published under the title **“Formulario de Estrés y Emociones Reportado (FEER)”**.
“**FEER**” and “**Formulario de Estrés y Emociones Reportado**” are claimed as trademarks (™) by
Amaury Santiago Horta.

- The **source code** is licensed under MIT (see [LICENSE](LICENSE)).
- The **name/branding** (“FEER”, logo, and visual identity) are **not** licensed under MIT.
  Any use of the name or logo requires prior written permission, and must not imply endorsement.
- Forks or derivatives **must not** present themselves as “FEER” or use the FEER logo or branding
  without permission. Use a distinct name/branding for redistributed versions.

© 2025 Amaury Santiago Horta. All rights reserved on the FEER name and branding.
*If the mark is later registered, replace “™” with “®”.*
