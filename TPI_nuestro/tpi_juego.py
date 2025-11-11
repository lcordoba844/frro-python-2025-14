# tpi_juego.py
import cv2
import time
import random
import sqlite3
import collections
from datetime import datetime
from tpi_letras import LetterEngine  # <- tu módulo

# =================== Config ===================
WORDS = [
    "LUNA", "LEON", "CERA", "CAMION", "RANA", "MESA", "CIELO",
    "FLOR", "CARA", "ARCO", "MELON", "LIMON", "UVA", "MANI", "KIWI",
    "MARRON", "AVENA", "VELA", "FARO", "RIO", "LINEA", "NIVEL", "MAR",
    "VELERO", "CARAMELO", "ANILLO", "MONO", "LORO", "CUADERNO",
    "LIBRO", "ARBOL", "CAMARA", "RAMO", "COCO", "RUIDO", "CEREAL",
    "FIDEO", "AMARILLO", "VERDE", "AVION"
]

K = 20            # frames consecutivos para validar letra
COOLDOWN = 10    # frames de cooldown
TIME_LIMIT = 75  # segundos por partida

FONT = cv2.FONT_HERSHEY_SIMPLEX

# Leaderboard (opcional)
USE_DB = True
DB_PATH = "scores.db"
TOP_LIMIT = 20

# =================== Utils UI ===================
def center_text(img, text, y, scale=1.2, color=(255,255,255), thick=2):
    H, W, _ = img.shape
    (tw, th), _ = cv2.getTextSize(text, FONT, scale, thick)
    x = (W - tw)//2
    cv2.putText(img, text, (x, y), FONT, scale, color, thick, cv2.LINE_AA)

def draw_button(img, rect, text, active=True):
    x1, y1, x2, y2 = rect
    base = (70,180,90) if active else (120,120,120)
    cv2.rectangle(img, (x1,y1), (x2,y2), base, -1)
    cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,255), 2)
    (tw, th), _ = cv2.getTextSize(text, FONT, 1.0, 2)
    tx = x1 + (x2-x1-tw)//2
    ty = y1 + (y2-y1+th)//2
    cv2.putText(img, text, (tx,ty), FONT, 1.0, (255,255,255), 2, cv2.LINE_AA)

def draw_text_input(img, rect, text, placeholder="Tu nombre...", focused=True):
    x1, y1, x2, y2 = rect
    cv2.rectangle(img, (x1,y1), (x2,y2), (30,30,30), -1)
    cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,255), 2 if focused else 1)
    shown = text if text else placeholder
    color = (255,255,255) if text else (180,180,180)
    pad = 12
    cv2.putText(img, shown, (x1+pad, y1+int((y2-y1)*0.65)), FONT, 0.9, color, 2, cv2.LINE_AA)

# =================== HUD Helpers ===================
def draw_hud(img, target_word, pos, score, time_left, combo, last_label):
    H, W, _ = img.shape
    # Panel superior
    word_disp = "".join([f"[{c}]" if i == pos else c for i, c in enumerate(target_word)])
    cv2.rectangle(img, (0,0), (W, 80), (25,25,25), -1)
    cv2.putText(img, f"Palabra: {word_disp}", (20,50), FONT, 1.1, (255,255,255), 2, cv2.LINE_AA)
    # Tip atajo
    hint = "S: Saltear (-5s)"
    (tw, th), _ = cv2.getTextSize(hint, FONT, 0.8, 2)
    cv2.putText(img, hint, (W - tw - 20, 50), FONT, 0.8, (255,255,255), 2, cv2.LINE_AA)

    # Panel inferior
    cv2.rectangle(img, (0,H-80), (W, H), (25,25,25), -1)
    cv2.putText(img, f"Puntos: {score}", (20,H-25), FONT, 0.9, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(img, f"Tiempo: {max(0,int(time_left))}s", (220,H-25), FONT, 0.9, (255,255,255), 2, cv2.LINE_AA)
    cv2.putText(img, f"Combo: x{combo}", (400,H-25), FONT, 0.9, (180,255,180), 2, cv2.LINE_AA)
    if last_label:
        cv2.putText(img, f"Detectado: {last_label}", (560,H-25), FONT, 0.9, (200,200,255), 2, cv2.LINE_AA)

    # Barra de progreso
    bar_x, bar_y = 20, 90
    bar_w, bar_h = W-40, 16
    done_ratio = pos / max(1, len(target_word))
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (180,180,180), 2)
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+int(bar_w*done_ratio), bar_y+bar_h), (80,200,80), -1)

def draw_skip_button(img):
    H, W, _ = img.shape
    btn_w, btn_h = 260, 50
    x2, y1 = W - 20, 18
    x1, y2 = x2 - btn_w, y1 + btn_h
    cv2.rectangle(img, (x1,y1), (x2,y2), (70,70,200), -1)
    cv2.rectangle(img, (x1,y1), (x2,y2), (255,255,255), 2)
    text = "S: Saltear (-5s)"
    (tw, th), _ = cv2.getTextSize(text, FONT, 0.7, 2)
    tx = x1 + (btn_w - tw)//2
    ty = y1 + (btn_h + th)//2 - 2
    cv2.putText(img, text, (tx,ty), FONT, 0.7, (255,255,255), 2, cv2.LINE_AA)
    return (x1, y1, x2, y2)

# =================== Start / End Menus ===================
_last_click = None
def _on_mouse(event, x, y, flags, param):
    global _last_click
    if event == cv2.EVENT_LBUTTONDOWN:
        _last_click = (x, y)

def draw_start_menu(img, player_name, input_focus=True):
    H, W, _ = img.shape
    # título
    center_text(img, "Senas & Palabras", int(H*0.22), 2.0, (0,255,255), 5)
    center_text(img, "Escribe tu nombre y presiona Comenzar", int(H*0.32), 0.9)

    # input + botón
    box_w, box_h = int(W*0.45), 70
    box_x1 = (W - box_w)//2
    box_y1 = int(H*0.40)
    box_rect = (box_x1, box_y1, box_x1+box_w, box_y1+box_h)
    draw_text_input(img, box_rect, player_name, focused=input_focus)

    btn_w, btn_h = int(W*0.25), 70
    btn_x1 = (W - btn_w)//2
    btn_y1 = int(H*0.55)
    btn_rect = (btn_x1, btn_y1, btn_x1+btn_w, btn_y1+btn_h)
    can_start = len(player_name.strip()) > 0
    draw_button(img, btn_rect, "Comenzar", active=can_start)

    center_text(img, "ENTER: Comenzar  |  ESC: Salir", int(H*0.75), 0.8, (200,200,200), 2)
    return box_rect, btn_rect, can_start

def draw_end_menu(img, score, player_name, top_rows=None):
    H, W, _ = img.shape
    overlay = img.copy()
    cv2.rectangle(overlay, (0,0), (W, H), (0,0,0), -1)
    img[:] = cv2.addWeighted(img, 0.35, overlay, 0.65, 0)

    center_text(img, f"¡Felicidades, {player_name}!", int(H*0.22), 1.6, (0,255,0), 4)
    center_text(img, f"Tu puntaje fue: {score}", int(H*0.30), 1.3, (255,255,255), 3)

    # Botones
    btn_w, btn_h = int(W*0.28), 70
    gap = 40
    x1 = int((W - (btn_w*2 + gap)) / 2)
    y1 = int(H*0.55)
    replay_rect = (x1, y1, x1+btn_w, y1+btn_h)
    quit_rect   = (x1+btn_w+gap, y1, x1+btn_w*2+gap, y1+btn_h)
    draw_button(img, replay_rect, "Volver a Jugar", True)
    draw_button(img, quit_rect, "Salir", True)

    # Top 20 (si hay DB)
    if top_rows:
        center_text(img, "TOP 20", int(H*0.36), 1.1, (255,255,0), 2)
        base_y = int(H*0.40)
        lh = 28
        left_x = int(W*0.20)
        right_x = int(W*0.60)
        for i, (name, sc, ts) in enumerate(top_rows[:TOP_LIMIT]):
            line = f"{i+1:2d}. {name[:18]:<18}  {sc:>5}"
            cv2.putText(img, line, (left_x, base_y + i*lh), FONT, 0.8, (255,255,255), 2, cv2.LINE_AA)

    center_text(img, "R: Volver a Jugar  |  Q/ESC: Salir", int(H*0.85), 0.8, (200,200,200), 2)
    return replay_rect, quit_rect

def point_in_rect(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2

# =================== Scoring ===================
def speed_bonus(elapsed_letter):
    if elapsed_letter <= 0.4: return 120
    if elapsed_letter <= 0.8: return 80
    if elapsed_letter <= 1.2: return 40
    if elapsed_letter <= 1.8: return 20
    return 0

# =================== Words shuffle ===================
def _new_words_queue():
    words = WORDS[:]
    random.shuffle(words)
    return words

# =================== DB (versión con SQLAlchemy) ===================
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# === Configuración del ORM ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scores.db")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# === Definición del modelo ===
class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# Crear tabla si no existe
Base.metadata.create_all(engine)

# === Función para guardar un puntaje ===
def save_score(name, score):
    """Guarda un puntaje en la base de datos."""
    session = SessionLocal()
    try:
        new_score = Score(name=name.strip()[:30], score=int(score))
        session.add(new_score)
        session.commit()
    except Exception as e:
        print(f"⚠️ Error al guardar puntaje: {e}")
        session.rollback()
    finally:
        session.close()

# === Función para inicializar la base ===
def init_db():
    """Crea las tablas si no existen (compatibilidad)."""
    Base.metadata.create_all(engine)

# === Función para obtener el top 20 ===
def get_top20(limit=20):
    """Devuelve los puntajes más altos (nombre, puntaje, fecha)."""
    session = SessionLocal()
    try:
        rows = (
            session.query(Score.name, Score.score, Score.created_at)
            .order_by(Score.score.desc(), Score.created_at.asc())
            .limit(limit)
            .all()
        )
        return [(r[0], r[1], r[2].strftime("%d/%m/%Y %H:%M:%S")) for r in rows]
    finally:
        session.close()


# =================== Game State ===================
def reset_game_state(player_name):
    words_queue = _new_words_queue()
    return {
        "player_name": player_name,
        "words": words_queue,
        "score": 0,
        "combo": 1.0,
        "word_index": 0,
        "target_word": words_queue[0],
        "pos": 0,
        "cooldown": 0,
        "last_labels": collections.deque(maxlen=K),
        "start_time": time.time(),
        "last_letter_time": time.time(),
        "penalty": 0
    }

def _advance_word(gs, give_word_bonus=True):
    if give_word_bonus:
        gs["score"] += 250
        gs["combo"] = min(gs["combo"] + 0.3, 3.0)
    gs["word_index"] += 1
    if gs["word_index"] >= len(gs["words"]):
        gs["words"] = _new_words_queue()
        gs["word_index"] = 0
    gs["target_word"] = gs["words"][gs["word_index"]]
    gs["pos"] = 0
    gs["cooldown"] = COOLDOWN + 10
    gs["last_letter_time"] = time.time()

def apply_skip(gs):
    gs["penalty"] += 5
    gs["pos"] += 1
    gs["last_labels"].clear()
    gs["combo"] = 1.0
    gs["cooldown"] = COOLDOWN
    if gs["pos"] >= len(gs["target_word"]):
        _advance_word(gs, give_word_bonus=False)

# =================== Main Loop ===================
def main():
    global _last_click
    random.seed()

    # Ventana grande / fullscreen
    cv2.namedWindow("Senas & Palabras", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Senas & Palabras", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("Senas & Palabras", _on_mouse)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    engine = LetterEngine()

    # Estados: START | PLAY | END
    state = "START"
    player_name = ""
    input_focus = True  # para el cuadro de nombre
    gs = None
    prev_t = cv2.getTickCount()

    top_rows_cache = get_top20() if USE_DB else []

    while True:
        ok, frame = cap.read()
        if not ok:
            # si no hay frame, dibujamos un lienzo negro para seguir con UI
            frame = (255 * (0 * 0)).__class__()
            frame = 255 * 0

        label, annotated = engine.process_frame(frame)

        # FPS (opcional)
        t = cv2.getTickCount()
        fps = cv2.getTickFrequency() / max(1, (t - prev_t))
        prev_t = t
        cv2.putText(annotated, f"FPS: {fps:.1f}", (20, 40), FONT, 0.9, (255,255,255), 2, cv2.LINE_AA)

        if state == "START":
            box_rect, btn_rect, can_start = draw_start_menu(annotated, player_name, input_focus)

            # Clicks
            if _last_click is not None:
                x, y = _last_click
                _last_click = None
                if point_in_rect(x, y, box_rect):
                    input_focus = True
                elif point_in_rect(x, y, btn_rect) and can_start:
                    gs = reset_game_state(player_name)
                    state = "PLAY"

            # Teclado (START)
            raw = cv2.waitKeyEx(30)   # mejor que waitKey para códigos extendidos
            if raw != -1:
                key = raw & 0xFFFFFFFF  # preserva el código, sin convertir -1 a 255

                if key == 27:  # ESC
                    break

                elif key in (13, 10):  # ENTER / RETURN
                    if can_start:
                        gs = reset_game_state(player_name)
                        state = "PLAY"

                elif input_focus:
                    # Backspace en distintas plataformas
                    if key in (8, 127):   # 8=Win, 127=Unix
                        player_name = player_name[:-1]

                    else:
                        # Caracter imprimible básico
                        try:
                            ch = chr(key)
                        except (ValueError, OverflowError):
                            ch = ""

                        # Filtramos a visibles estándar + espacio
                        if ch and 32 <= ord(ch) <= 126 and len(player_name) < 30:
                            player_name += ch


        elif state == "PLAY":
            time_left = TIME_LIMIT - (time.time() - gs["start_time"]) - gs["penalty"]
            if time_left <= 0:
                # guardar score y pasar a END
                if USE_DB:
                    save_score(gs["player_name"], int(gs["score"]))
                    top_rows_cache = get_top20()
                state = "END"
            else:
                if gs["cooldown"] > 0:
                    gs["cooldown"] -= 1
                else:
                    need = gs["target_word"][gs["pos"]]
                    if label:
                        gs["last_labels"].append(label)

                    if label and sum(1 for x in gs["last_labels"] if x == need) >= (K//2 + 1):
                        elapsed = time.time() - gs["last_letter_time"]
                        gs["last_letter_time"] = time.time()

                        base = 100
                        bonus = speed_bonus(elapsed)
                        score_gain = int((base + bonus) * gs["combo"])
                        gs["score"] += score_gain
                        gs["combo"] = min(gs["combo"] + 0.1, 3.0)

                        gs["pos"] += 1
                        gs["cooldown"] = COOLDOWN
                        gs["last_labels"].clear()

                        # Feedback
                        cv2.putText(annotated, f"{need}", (60,160), FONT, 3.2, (0,255,0), 7, cv2.LINE_AA)
                        cv2.putText(annotated, f"+{score_gain}", (60,240), FONT, 1.6, (0,255,0), 5, cv2.LINE_AA)

                        if gs["pos"] == len(gs["target_word"]):
                            _advance_word(gs, give_word_bonus=True)
                    elif label and label != need:
                        gs["combo"] = max(1.0, gs["combo"] - 0.3)

                # Dibujo HUD primero
                draw_hud(annotated, gs["target_word"], gs["pos"], int(gs["score"]), time_left, round(gs["combo"],1), label)
                # Botón Saltear encima
                skip_rect = draw_skip_button(annotated)

                # Click saltear
                if _last_click is not None:
                    x, y = _last_click
                    _last_click = None
                    if point_in_rect(x, y, skip_rect):
                        apply_skip(gs)
                        time_left = TIME_LIMIT - (time.time() - gs["start_time"]) - gs["penalty"]
                        if time_left <= 0:
                            if USE_DB:
                                save_score(gs["player_name"], int(gs["score"]))
                                top_rows_cache = get_top20()
                            state = "END"

                # Teclas globales
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key in (ord('q'), ord('Q')):
                    break
                if key in (ord('s'), ord('S')):
                    apply_skip(gs)

        elif state == "END":
            replay_rect, quit_rect = draw_end_menu(annotated, int(gs["score"]), gs["player_name"], top_rows_cache if USE_DB else None)

            if _last_click is not None:
                x, y = _last_click
                _last_click = None
                if point_in_rect(x, y, replay_rect):
                    # volver a START para escribir otro nombre o reusar el mismo
                    state = "START"
                elif point_in_rect(x, y, quit_rect):
                    break

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key in (ord('q'), ord('Q')):
                break
            if key in (ord('r'), ord('R')):
                state = "START"

        # Mostrar frame
        cv2.imshow("Senas & Palabras", annotated)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
