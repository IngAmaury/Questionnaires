# Driver Study Questionnaires GUI

A friendly PyQt6 application to collect questionnaires during driving-simulator experiments.
It guides the participant through an initial battery and then repeated inter-stage blocks, saving every answer to a CSV file (UTF-8).

## Overview

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

## Features
### Main Features
- Big UI: large fonts, clear radio buttons, images for SAM.
- Sectioned flow: initial battery, then repeatable blocks with transition messages.
- Robust saving: answers are written row-by-row to a CSV with UTF-8 BOM (Excel-friendly).
- PSS scoring: inverted items (4, 5, 6, 7, 9, 10, 13) are auto-reversed.
- SAM images: fixed size, centered; radio buttons can be overlaid on the images to save space.
- Participant & stage metadata: each row includes timestamp, participant ID, block number, and stage label.

### CSV Schema
- Columns: timestamp, participant_id, block_id, stage_label, instrument, item_code, item_text, response, score
- Example instruments: BAI, PSS, PSS_TOTAL, PANAS, SAM_Manikin, SAM_Stress.

### Add a new questionnarie (quick guide)
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

## Requirements
* Python 3.9–3.12
* PyQt6 (UI)
* Pillow (optional, only if you later add image processing; not required now) 

## Getting Started

**Folder structure**

```bash
project/
├─ cuestionarios_gui.py
├─ respuestas_cuestionarios.csv        # auto-created on first run
└─ Sources/                            # SAM images used in the UI
   ├─ valence_scale.jpg
   ├─ arousal_scale.png
   └─ dominance_scale.png
```
[!NOTE]
> Use your own images; the app scales them to a uniform size.
> If an image is missing, a warning text appears instead.

**Run**
Use your favorite IDE to run the Python file "cuestionarios.py", or run it in the terminal from the folder where you downloaded the repository, like this:
```python
python cuestionarios.py
```
At start up:
1. Enter Participant ID (free text).
2. Enter Stage label (e.g., “Baseline”, “Stage 1”, “Route 2”).
3. Choose Block # (1..n).
4. Click Initial evaluation or Inter-stage block.

## Usage
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

## Language
- The UI and questionnaires are currently in Spanish.
- You can translate items or add new language versions by duplicating the item lists.

## License
This project is licensed under the **MIT License**.  
Copyright © 2025 Amaury Santiago Horta.
See the [LICENSE](LICENSE) file for details.