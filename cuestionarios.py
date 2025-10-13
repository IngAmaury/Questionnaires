import sys, csv, os
from datetime import datetime
from typing import List, Dict, Tuple
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QRadioButton, QButtonGroup, QScrollArea, QStackedWidget, QLineEdit,
    QMessageBox, QGroupBox, QComboBox, QSizePolicy, QStackedLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

# =========================
# CONFIGURACIÓN GENERAL
# =========================
APP_TITLE = "Cuestionarios (BAI, PSS, PANAS, SAM-manikin, SAM-estrés)"
CSV_FILE  = "respuestas_cuestionarios.csv"  # se crea/apendea en la carpeta del script
BIG_FONT  = QFont("Segoe UI", 16)
TITLE_FONT = QFont("Segoe UI", 20, QFont.Weight.Bold)
BTN_FONT   = QFont("Segoe UI", 16)

# =========================
# DEFINICIÓN DE CUESTIONARIOS
# =========================

# --- BAI (Inventario de Ansiedad de Beck, 21 ítems, 0..3)
BAI_INSTRUCTIONS = ("INSTRUCCIONES:\n"
                    "Lea cada síntoma y marque cuánto le ha afectado actualmente. Considere como referencia las dificultades que ha tenido este último mes.")
BAI_ITEMS = [
    "Hormigueo o entumecimiento",
    "Sensación de calor",
    "Con temblor en las piernas",
    "Incapacidad de relajarse",
    "Miedo a que suceda lo peor",
    "Mareo o aturdimiento",
    "Latidos del corazón fuertes y acelerados",
    "Sensación de inestabilidad e inseguridad física",
    "Atemorizado o asustado",
    "Nerviosismo",
    "Sensación de bloqueo o ahogo",
    "Temblores en las manos",
    "Inquieto, inseguro o estremecimiento",
    "Miedo a perder el control",
    "Dificultad para respirar",
    "Miedo a morirse",
    "Sobresaltos",
    "Con problemas digestivos o abdominales",
    "Palidez",
    "Rubor facial",
    "Con sudores, fríos o calientes (no debidos a la temperatura)",
]
BAI_OPTIONS = [("Nada",0), ("Leve",1), ("Moderado",2), ("Bastante",3)]

# --- PSS (Escala de Estrés Percibido 14 ítems, 0..4)
# Ítems invertidos: 4, 5, 6, 7, 9, 10, 13 (indexados 1..14).
PSS_REVERSE = {4,5,6,7,9,10,13}
PSS_ITEMS = [
    "En el último mes, ¿con qué frecuencia te has sentido afectado por algo que ocurrió inesperadamente?",
    "En el último mes, ¿con qué frecuencia te has sentido incapaz de controlar las cosas importantes en tu vida?",
    "En el último mes, ¿con qué frecuencia te has sentido nervioso o estresado?",
    "En el último mes, ¿con qué frecuencia has manejado con éxito los pequeños problemas irritantes de la vida?",
    "En el último mes, ¿con qué frecuencia has sentido que has afrontado efectivamente los cambios importantes que han estado ocurriendo en tu vida?",
    "En el último mes, ¿con qué frecuencia has estado seguro sobre tu capacidad para manejar tus problemas personales?",
    "En el último mes, ¿con qué frecuencia has sentido que las cosas van bien?",
    "En el último mes, ¿con qué frecuencia has sentido que no podías afrontar todas las cosas que tenías que hacer?",
    "En el último mes, ¿con qué frecuencia has podido controlar las dificultades de tu vida?",
    "En el último mes, ¿con qué frecuencia has sentido que tenías todo bajo control?",
    "En el último mes, ¿con qué frecuencia has estado enfadado porque las cosas que te han ocurrido estaban fuera de tu control?",
    "En el último mes, ¿con qué frecuencia has pensado sobre las cosas que te faltan por hacer?",
    "En el último mes, ¿con qué frecuencia has podido controlar la forma de pasar el tiempo?",
    "En el último mes, ¿con qué frecuencia has sentido que las dificultades se acumulan tanto que no puedes superarlas?",
]
PSS_OPTIONS = [("Nunca",0),("Casi nunca",1),("De vez en cuando",2),("A menudo",3),("Muy a menudo",4)]

# --- PANAS (20 adjetivos, 1..5)
PANAS_INSTRUCTIONS = ("INSTRUCCIONES:\n"
                      "Esta escala consiste en una serie de palabras  que describen diferentes sentimientos y emociones. Lea cada palabra y marque la respuesta apropieada para usted.\n"
                      "Indique cómo se siente generalmente.")
PANAS_ITEMS = [
    # Positivos (PA)
    "interesado/a","entusiasmado/a","fuerte","inspirado/a","alerta",
    "activo/a","atento/a","decidido/a","orgulloso/a","emocionado/a",
    # Negativos (NA)
    "irritable","nervioso/a","culpable","temeroso/a","ansioso/a",
    "inquieto/a","avergonzado/a","triste","hostil","asustado/a",
]
PANAS_OPTIONS = [("1 Muy poco o nada",1),("2 Algo",2),("3 Moderadamente",3),("4 Bastante",4),("5 Extremadamente",5)]

# --- SAM-manikin (valencia, activación, dominio) 1..5
SAM_MANIKIN_ITEMS = [
    ("Valencia (muy desagradable → muy agradable)", 1, 9),
    ("Activación (muy activado → muy calmado)",     1, 9),
    ("Dominio (sin control → con mucho control)",    1, 9),
]

# --- SAM-estrés (Stress Appraisal Measure, subset: 2,5,8,14,20,16,22,19,24,26) escala 0..4
SAM_STRESS_Instructions = ("INSTRUCCIONES:\n"
                           "Este cuestionario se refiere a tus pensamientos sobre la situación identificada previamente. No hay respuestas correctas o incorrrectas.\n"
                           "Por favor, responde según como te sentiste con la situación.")
SAM_STRESS_ALL = {
    1:"¿Es esta una situación totalmente desesperada?",
    2:"¿Esta situación te crea tensión?",
    3:"¿El resultado de esta situación es incontrolable por alguien más?",
    4:"¿Hay alguien o alguna agencia a la que puedas recurrir para pedir ayuda si la necesitas?",
    5:"¿La situación te hizo sentir ansioso?",
    6:"¿Esta situación tiene consecuencias importantes para ti?",
    7:"¿Esta situación va a tener un impacto positivo en ti?",
    8:"¿Qué tan ansioso estabas por abordar el evento?",
    9:"¿Cuánto te afectará el resultado de esta situación?",
    10:"¿Hasta qué punto puedes convertirte en una persona más fuerte debido a este problema?",
    11:"¿El resultado de esta situación será negativo?",
    12:"¿Tienes la capacidad de hacerlo bien en esta situación?",
    13:"¿Esta situación tiene implicaciones serias para ti?",
    14:"¿Tuviste lo necesario para hacerlo bien en esa situación?",
    15:"¿Hubo ayuda disponible para mí para lidiar con este problema?",
    16:"¿La situación superó o agotó mis recursos de afrontamiento?",
    17:"¿Hubo suficientes recursos disponibles para ayudarme a lidiar con esta situación?",
    18:"¿Estaba fuera del poder de alguien hacer algo sobre esta situación?",
    19:"¿Qué tan emocionado estuviste pensando en el resultado de esta situación?",
    20:"¿Qué tan amenazante fue la situación?",
    21:"¿El problema fue irresoluble por alguien?",
    22:"¿Pude superar el problema?",
    23:"¿Hubo alguien que pudiera ayudarme a manejar este problema?",
    24:"¿En qué medida percibí esta situación como estresante?",
    25:"¿Tuve las habilidades necesarias para lograr un resultado exitoso en esta situación?",
    26:"¿En qué medida este evento requirió esfuerzos de afrontamiento de mi parte?",
    27:"¿Esta situación tuvo consecuencias a largo plazo para mí?",
    28:"¿Esto iba a tener un impacto negativo en mí?",
}
SAM_STRESS_SUBSET_ORDER = [2,8,14,20,16,5,22,19,24,26]
SAM_STRESS_OPTIONS = [("0 Nada",0),("1 Poco",1),("2 Algo",2),("3 Mucho",3),("4 Demasiado",4)]

# =========================
# UTILIDADES CSV
# =========================
def ensure_csv_header(path: str):
    exists = os.path.isfile(path)
    if not exists:
        with open(path, "a", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp","participant_id","block_id","stage_label",
                "instrument","item_code","item_text","response","score"
            ])

def append_row(row: List):
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(row)

# =========================
# WIDGETS GENERALES
# =========================
class QuestionGroup(QWidget):
    """Grupo de varias preguntas con opciones tipo radio grande."""
    def __init__(self, instrument: str, items: List[str],
                 options: List[Tuple[str,int]], participant_id: str,
                 block_id: int, stage_label: str, item_prefix: str = "",
                 instructions: str | None = None,
                 instr_align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignJustify):
        super().__init__()
        self.instrument = instrument
        self.items = items
        self.options = options
        self.participant_id = participant_id
        self.block_id = block_id
        self.stage_label = stage_label
        self.item_prefix = item_prefix
        self.groups: List[QButtonGroup] = []

        layout = QVBoxLayout()
        title = QLabel(instrument)
        title.setFont(TITLE_FONT)
        layout.addWidget(title)

        # -- INSTRUCCIONES --
        if instructions:
            instr = QLabel(instructions)
            instr.setWordWrap(True)
            instr.setAlignment(instr_align)  # Justificado / Derecha / Centro
            instr.setFont(QFont('Segoe UI', 14))
            instr.setStyleSheet("color:#333;")
            instr.setContentsMargins(8, 0, 8, 12)
            layout.addWidget(instr)

        # Scroll para listas largas
        container = QWidget()
        v = QVBoxLayout(container)
        v.setSpacing(16)

        for idx, txt in enumerate(items, start=1):
            box = QGroupBox(f"{idx}. {txt}")
            box_font = QFont(BIG_FONT)
            box.setFont(box_font)
            hb = QHBoxLayout()
            bg = QButtonGroup(self)
            bg.setExclusive(True)
            for opt_txt, val in options:
                rb = QRadioButton(opt_txt)
                rb.setFont(BIG_FONT)
                rb.setProperty("score", val)
                bg.addButton(rb)
                hb.addWidget(rb)
            box.setLayout(hb)
            v.addWidget(box)
            self.groups.append(bg)

        v.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        layout.addWidget(scroll)

        btns = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.next_btn = QPushButton("Siguiente")
        self.prev_btn.setFont(BTN_FONT)
        self.next_btn.setFont(BTN_FONT)
        btns.addStretch(1)
        btns.addWidget(self.prev_btn)
        btns.addWidget(self.next_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def all_answered(self) -> bool:
        return all(g.checkedButton() is not None for g in self.groups)

    def save_to_csv(self):
        ts = datetime.now().isoformat(timespec="seconds")
        for idx, g in enumerate(self.groups, start=1):
            b = g.checkedButton()
            score = b.property("score")
            code = f"{self.item_prefix}{idx}"
            txt  = self.items[idx-1]
            append_row([ts, self.participant_id, self.block_id, self.stage_label,
                        self.instrument, code, txt, b.text(), score])

# PSS con inversión de ítems
class PSSWidget(QuestionGroup):
    def __init__(self, instrument: str, items, options, participant_id: str, block_id: int, stage_label: str):
        instr_text = (
            "INSTRUCCIONES:\n"
            "Las preguntas en esta escala hacen referencia a tus sentimientos y pensamientos durante el último mes. En cada caso, por favor indica la expresión que mejor represente como te has sentido o cómo has enfrentado cada situación.\n"
            ""
        )
        super().__init__(instrument, items, options, participant_id, block_id, stage_label, item_prefix='PSS_', instructions=instr_text)

    def save_to_csv(self):
        ts = datetime.now().isoformat(timespec="seconds")
        total = 0
        for idx, g in enumerate(self.groups, start=1):
            b = g.checkedButton()
            val = b.property("score")  # 0..4
            # invertir donde corresponda
            score = 4 - val if idx in PSS_REVERSE else val
            total += score
            code = f"PSS_{idx}"
            txt  = self.items[idx-1]
            append_row([ts, self.participant_id, self.block_id, self.stage_label,
                        "PSS", code, txt, b.text(), score])
        # guardar total como fila resumen
        append_row([ts, self.participant_id, self.block_id, self.stage_label,
                    "PSS_TOTAL", "sum", "Suma de 14 ítems (con inversión)", "", total])

# SAM-manikin simple (3 preguntas, 1..9) con imagen horizontal de tamaño uniforme
class SAMManikinWidget(QWidget):
    def __init__(self, participant_id: str, block_id: int, stage_label: str):
        super().__init__()
        self.participant_id = participant_id
        self.block_id = block_id
        self.stage_label = stage_label
        self.groups: List[QButtonGroup] = []

        # --- tamaño uniforme para TODAS las imágenes ---
        self.SCALE_W, self.SCALE_H = 600, 160

        layout = QVBoxLayout()
        title = QLabel("Maniquí de autoevaluación (Valencia, Activación, Dominio)")
        title.setFont(TITLE_FONT)
        layout.addWidget(title)

        instr = QLabel(
            "INSTRUCCIONES:\n"
            "Observa la tira de maniquíes y elige un número del 1 al 9 que mejor describa cómo te sientes.\n"
            "Si tiene dudas pregunte al entrevistador."
        )
        instr.setWordWrap(True)
        instr.setAlignment(Qt.AlignmentFlag.AlignJustify)
        instr.setFont(QFont('Segoe UI', 14))
        instr.setStyleSheet("color:#333;")
        instr.setContentsMargins(8, 0, 8, 12)
        layout.addWidget(instr)

        dims = [
            ("Valencia (muy desagradable → muy agradable)", "valence_scale.png", False),
            ("Activación (muy activado → muy calmado)",     "arousal_scale.png", True),
            ("Dominio (sin control → con mucho control)",    "dominance_scale.png", False),
        ]

        for label_text, img_file, invert in dims:
            group_box = QGroupBox(label_text)
            group_box.setFont(BIG_FONT)
            vbox = QVBoxLayout()

            # --- Imagen (capa inferior) ---
            img_path = os.path.join("Sources", img_file)
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setFixedSize(self.SCALE_W, self.SCALE_H)
            img_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            if os.path.isfile(img_path):
                pm = QPixmap(img_path).scaled(
                    self.SCALE_W, self.SCALE_H,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label.setPixmap(pm)
            else:
                img_label.setText(f"[Falta imagen: {img_file}]")
                img_label.setStyleSheet("color:#aa0000;")

            # --- Radios (capa superior) ---
            radios_bar = QWidget()
            rb_h = QHBoxLayout(radios_bar)
            rb_h.setSpacing(12)
            rb_h.setContentsMargins(0, 0, 0, 0)  # margen inferior dentro de la capa
            rb_h.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            bg = QButtonGroup(self)
            bg.setExclusive(True)
            for k in range(1, 10):  # 1..9
                rb = QRadioButton(str(k))
                rb.setFont(BIG_FONT)
                rb.setProperty("score", 10 - k if invert else k)
                bg.addButton(rb)
                rb_h.addWidget(rb)

            # --- SUPERPOSICIÓN: imagen + radios ---
            canvas = QWidget()
            canvas.setFixedSize(self.SCALE_W, self.SCALE_H)
            stack = QStackedLayout(canvas)
            stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.addWidget(img_label)

            overlay = QWidget()
            ov = QVBoxLayout(overlay)
            ov.setContentsMargins(0, 0, 0, 0)
            ov.addStretch(1)
            ov.addWidget(radios_bar, alignment=Qt.AlignmentFlag.AlignHCenter)
            stack.addWidget(overlay)
            stack.setCurrentWidget(overlay)

            group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            vbox.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            group_box.setLayout(vbox)
            layout.addWidget(group_box)

            self.groups.append(bg)

        # Navegación
        btns = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.next_btn = QPushButton("Siguiente")
        self.prev_btn.setFont(BTN_FONT)
        self.next_btn.setFont(BTN_FONT)
        btns.addStretch(1)
        btns.addWidget(self.prev_btn)
        btns.addWidget(self.next_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

    def all_answered(self) -> bool:
        return all(g.checkedButton() is not None for g in self.groups)

    def save_to_csv(self):
        ts = datetime.now().isoformat(timespec="seconds")
        names = ["Valencia","Activación","Dominio"]
        for i, g in enumerate(self.groups):
            b = g.checkedButton()
            score = b.property("score")
            append_row([ts, self.participant_id, self.block_id, self.stage_label,
                        "SAM_Manikin", names[i], names[i], str(score), score])

# SAM-estrés (subset)
class SAMStressSubsetWidget(QuestionGroup):
    def __init__(self, participant_id: str, block_id: int, stage_label: str):
        items = [f"{k}. {SAM_STRESS_ALL[k]}" for k in SAM_STRESS_SUBSET_ORDER]
        super().__init__("Medida de evaluación del estrés (SAM) – Subconjunto", items,
                         SAM_STRESS_OPTIONS, participant_id, block_id, stage_label, item_prefix="SAMQ_",
                         instructions=SAM_STRESS_Instructions)
        # Sobrescribe el rotulado para conservar el código original
        for i, gb in enumerate(self.findChildren(QGroupBox), start=0):
            k = SAM_STRESS_SUBSET_ORDER[i]
            gb.setTitle(f"{SAM_STRESS_ALL[k]}")

    def save_to_csv(self):
        ts = datetime.now().isoformat(timespec="seconds")
        for i, g in enumerate(self.groups):
            k = SAM_STRESS_SUBSET_ORDER[i]
            b = g.checkedButton()
            score = b.property("score")
            append_row([ts, self.participant_id, self.block_id, self.stage_label,
                        "SAM_Stress", f"Q{k}", SAM_STRESS_ALL[k], b.text(), score])

# =========================
# PÁGINAS DE FLUJO
# =========================
class StartPage(QWidget):
    """Pantalla inicial para ID de participante y elegir flujo."""
    def __init__(self, proceed_initial, proceed_block):
        super().__init__()
        v = QVBoxLayout()
        title = QLabel(APP_TITLE)
        title.setFont(TITLE_FONT)
        v.addWidget(title)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("ID del participante")
        self.id_edit.setFont(BIG_FONT)

        self.stage_edit = QLineEdit()
        self.stage_edit.setPlaceholderText("Etiqueta de etapa (p. ej., Baseline, Ruta 1, etc.)")
        self.stage_edit.setFont(BIG_FONT)

        self.block_combo = QComboBox()
        self.block_combo.setFont(BIG_FONT)
        self.block_combo.addItems([str(i) for i in range(1, 21)])
        block_row = QHBoxLayout()
        block_row.addWidget(QLabel("Bloque #:"))
        block_row.addWidget(self.block_combo)
        block_row.addStretch(1)
        for w in (block_row.itemAt(0).widget(),):
            w.setFont(BIG_FONT)

        btn_initial = QPushButton("Evaluación inicial (BAI + PSS + PANAS)")
        btn_block   = QPushButton("Iniciar Bloque Inter-etapas (SAM-manikin + SAM-estrés)")
        for b in (btn_initial, btn_block):
            b.setFont(BTN_FONT)

        v.addWidget(self.id_edit)
        v.addWidget(self.stage_edit)
        v.addLayout(block_row)
        v.addSpacing(20)
        v.addWidget(btn_initial)
        v.addWidget(btn_block)
        v.addStretch(1)
        self.setLayout(v)

        btn_initial.clicked.connect(lambda: proceed_initial(self._payload()))
        btn_block.clicked.connect(lambda: proceed_block(self._payload()))

    def _payload(self):
        pid = self.id_edit.text().strip()
        stage = self.stage_edit.text().strip() or "SinEtiqueta"
        block = int(self.block_combo.currentText())
        if not pid:
            QMessageBox.warning(self, "Dato faltante", "Introduce el ID del participante.")
            return None
        return {"participant_id": pid, "stage_label": stage, "block_id": block}

class TransitionPage(QWidget):
    def __init__(self, message: str, on_next):
        super().__init__()
        v = QVBoxLayout()
        lab = QLabel(message)
        lab.setWordWrap(True)
        lab.setFont(TITLE_FONT)
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addStretch(1)
        v.addWidget(lab)
        v.addStretch(1)
        btn = QPushButton("Continuar")
        btn.setFont(BTN_FONT)
        btn.clicked.connect(on_next)
        v.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(v)

# =========================
# APLICACIÓN PRINCIPAL
# =========================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 800)
        self.setWindowIcon(QIcon("Sources/logo.ico"))

        # Fuente grande por defecto
        self.setFont(BIG_FONT)

        ensure_csv_header(CSV_FILE)

        self.stack = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Página de inicio
        self.start = StartPage(self.start_initial_flow, self.start_block_flow)
        self.stack.addWidget(self.start)

    # ---------- Flujos ----------
    def start_initial_flow(self, payload):
        if not payload: return
        self.pid = payload["participant_id"]
        self.stage = payload["stage_label"]
        self.block = payload["block_id"]  # puede ser 1 o el que decidas
        # BAI
        self.bai = QuestionGroup("Inventario de Ansiedad de Beck (BAI)",
                                 BAI_ITEMS, BAI_OPTIONS, self.pid, self.block, self.stage, "BAI_",
                                 BAI_INSTRUCTIONS)
        self.bai.prev_btn.clicked.connect(self.go_start)
        self.bai.next_btn.clicked.connect(self._bai_next)
        self.stack.addWidget(self.bai); self.stack.setCurrentWidget(self.bai)

    def _bai_next(self):
        if not self.bai.all_answered():
            QMessageBox.information(self, "Faltan respuestas", "Responde todas las preguntas.")
            return
        self.bai.save_to_csv()
        # PSS
        self.pss = PSSWidget("Escala de Estrés Percibido (PSS)", PSS_ITEMS, PSS_OPTIONS, self.pid, self.block, self.stage)
        self.pss.prev_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.bai))
        self.pss.next_btn.clicked.connect(self._pss_next)
        self.stack.addWidget(self.pss); self.stack.setCurrentWidget(self.pss)

    def _pss_next(self):
        if not self.pss.all_answered():
            QMessageBox.information(self, "Faltan respuestas", "Responde todas las preguntas.")
            return
        self.pss.save_to_csv()
        # PANAS
        self.panas = QuestionGroup("Escala de Afectividad Positiva y Negativa (PANAS) (versión corta en castellano)",
                                   PANAS_ITEMS, PANAS_OPTIONS, self.pid, self.block, self.stage, "PANAS_", PANAS_INSTRUCTIONS)
        self.panas.prev_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.pss))
        self.panas.next_btn.clicked.connect(self._panas_next)
        self.stack.addWidget(self.panas); self.stack.setCurrentWidget(self.panas)

    def _panas_next(self):
        if not self.panas.all_answered():
            QMessageBox.information(self, "Faltan respuestas", "Responde todas las preguntas.")
            return
        self.panas.save_to_csv()
        done = TransitionPage(
            "¡Gracias! Terminaste la evaluación inicial.\n\n"
            "Pulsa continuar para volver a la pantalla inicial.",
            self.go_start
        )
        self.stack.addWidget(done); self.stack.setCurrentWidget(done)

    def start_block_flow(self, payload):
        if not payload: return
        self.pid = payload["participant_id"]
        self.stage = payload["stage_label"]
        self.block = payload["block_id"]

        intro = TransitionPage(
            f"Bloque {self.block}\n\n"
            "Responda la Escala de Autoevaluación con Maniquí (SAM: Valencia, Activación, Dominio).",
            self._block_sam_manikin
        )
        self.stack.addWidget(intro); self.stack.setCurrentWidget(intro)

    def _block_sam_manikin(self):
        self.sam = SAMManikinWidget(self.pid, self.block, self.stage)
        self.sam.prev_btn.clicked.connect(self.go_start)
        self.sam.next_btn.clicked.connect(self._sam_next)
        self.stack.addWidget(self.sam); self.stack.setCurrentWidget(self.sam)

    def _sam_next(self):
        if not self.sam.all_answered():
            QMessageBox.information(self, "Faltan respuestas", "Responde las tres dimensiones.")
            return
        self.sam.save_to_csv()
        trans = TransitionPage(
            "Ahora responde el Cuestionario de Evaluación de Estrés (SAM).",
            self._block_sam_stress
        )
        self.stack.addWidget(trans); self.stack.setCurrentWidget(trans)

    def _block_sam_stress(self):
        self.samstress = SAMStressSubsetWidget(self.pid, self.block, self.stage)
        self.samstress.prev_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.sam))
        self.samstress.next_btn.clicked.connect(self._block_done)
        self.stack.addWidget(self.samstress); self.stack.setCurrentWidget(self.samstress)

    def _block_done(self):
        if not self.samstress.all_answered():
            QMessageBox.information(self, "Faltan respuestas", "Responde todos los ítems.")
            return
        self.samstress.save_to_csv()
        done = TransitionPage(
            f"Bloque {self.block} completado.\n\n"
            "Espere indicaciones y pulse continuar\n"
            "cuando sea momento se pasará al siguiente bloque.",
            self.go_start
        )
        self.stack.addWidget(done); self.stack.setCurrentWidget(done)

    # ---------- Navegación ----------
    def go_start(self):
        self.stack.setCurrentWidget(self.start)

# =========================
# MAIN
# =========================
def main():
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(APP_TITLE)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
