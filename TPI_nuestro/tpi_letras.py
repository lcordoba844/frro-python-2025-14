# tpi_letras.py
# Módulo exportable para usar desde tpi_juego.py
# Uso: from tpi_letras import LetterEngine

import cv2
import math
import collections
import mediapipe as mp
import time

# -------------------- Utils geométricas --------------------
def euclid(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5

def angle(a, b, c):
    # ángulo en B formado por A-B-C (en grados)
    ba = (a[0]-b[0], a[1]-b[1])
    bc = (c[0]-b[0], c[1]-b[1])
    dot = ba[0]*bc[0] + ba[1]*bc[1]
    n1 = (ba[0]**2 + ba[1]**2) ** 0.5
    n2 = (bc[0]**2 + bc[1]**2) ** 0.5
    if n1 == 0 or n2 == 0: return 0.0
    cosv = max(-1.0, min(1.0, dot/(n1*n2)))
    return math.degrees(math.acos(cosv))

def bbox_from_landmarks(image_shape, hand_landmarks):
    H, W, _ = image_shape
    xs, ys = [], []
    for lm in hand_landmarks.landmark:
        xs.append(int(lm.x * W))
        ys.append(int(lm.y * H))
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return (x_min, y_min, x_max, y_max)

def lm_px(hand_landmarks, idx, W, H):
    return (int(hand_landmarks.landmark[idx].x * W),
            int(hand_landmarks.landmark[idx].y * H))

def is_extended_y(tip, pip):
    # y menor = más arriba (coordenadas de imagen)
    return tip[1] < pip[1]

# ---- TUNEABLE THRESHOLDS ----
TH_CLOSE = 0.10
TH_NEAR  = 0.13   # + levemente más permisivo
TH_MED   = 0.18   # + levemente más permisivo
TH_WIDE  = 0.22
TH_GAP_TIGHT = 0.06
TH_GAP_JOIN  = 0.10
TH_GAP_SPLIT = 0.14

def horiz_ratio(a, b):
    dx = abs(a[0]-b[0]); dy = abs(a[1]-b[1])
    return dy / (dx + 1e-6)

def roughly_horizontal(a, b, max_ratio=0.60):
    # 0.60 para tolerar inclinación leve
    return horiz_ratio(a, b) < max_ratio

def roughly_vertical(a, b, min_ratio=0.90):
    return horiz_ratio(a, b) > min_ratio

def between(v, a, b):  # v dentro del rango [min(a,b), max(a,b)]
    return min(a, b) <= v <= max(a, b)

# -------------------- ROI Z helpers --------------------
def point_in_roi(point, roi):
    x, y = point
    x1, y1, x2, y2 = roi
    return x1 <= x <= x2 and y1 <= y <= y2

def analyze_z_pattern(points, roi_width, roi_height, z_roi_bounds):
    """
    Analiza si los puntos forman un patrón de Z.
    Retorna True si es una Z válida.
    """
    if len(points) < 14:
        return False

    # largo total del trazo (px)
    total_len = 0.0
    for i in range(1, len(points)):
        total_len += euclid(points[i-1], points[i])
    if total_len < 0.9 * (roi_width + roi_height*0.5):
        # trazo demasiado corto para una Z visible
        return False

    # Normalizar puntos al ROI (0-1)
    x1, y1, x2, y2 = z_roi_bounds
    normalized = [((px - x1) / roi_width, (py - y1) / roi_height) for (px,py) in points]

    # Dividir en 3 segmentos
    third = len(normalized) // 3
    seg1 = normalized[:third]
    seg2 = normalized[third:2*third]
    seg3 = normalized[2*third:]

    if not seg1 or not seg2 or not seg3:
        return False

    # Segmento 1: debe ir hacia la derecha (horizontal)
    dx1 = seg1[-1][0] - seg1[0][0]
    dy1 = abs(seg1[-1][1] - seg1[0][1])
    seg1_horizontal_right = dx1 > 0.28 and dy1 < 0.18

    # Segmento 2: debe ir diagonal abajo-izquierda
    dx2 = seg2[-1][0] - seg2[0][0]
    dy2 = seg2[-1][1] - seg2[0][1]
    seg2_diagonal = dx2 < -0.22 and dy2 > 0.28  # más marcada

    # Segmento 3: debe ir hacia la derecha (horizontal)
    dx3 = seg3[-1][0] - seg3[0][0]
    dy3 = abs(seg3[-1][1] - seg3[0][1])
    seg3_horizontal_right = dx3 > 0.28 and dy3 < 0.18

    return seg1_horizontal_right and seg2_diagonal and seg3_horizontal_right

def draw_z_roi(image, roi, points, status):
    """
    Dibuja el ROI para la Z y el trazo actual.
    status: None (trazando), "success" (Z detectada), "fail" (no es Z)
    """
    x1, y1, x2, y2 = roi

    # Color del ROI según el estado
    if status == "success":
        roi_color = (0, 255, 0)  # Verde
        text = "Z DETECTADA!"
        text_color = (0, 255, 0)
    elif status == "fail":
        roi_color = (0, 0, 255)  # Rojo
        text = "Intenta de nuevo"
        text_color = (0, 0, 255)
    else:
        roi_color = (255, 200, 0)  # Cyan
        text = "Traza una Z aqui"
        text_color = (255, 200, 0)

    # Dibujar ROI
    cv2.rectangle(image, (x1, y1), (x2, y2), roi_color, 3)

    # Texto instructivo
    cv2.putText(image, text, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2, cv2.LINE_AA)

    # Dibujar el trazo
    if len(points) > 1:
        for i in range(len(points) - 1):
            cv2.line(image, points[i], points[i+1], roi_color, 3)

        # Punto actual (más grande)
        cv2.circle(image, points[-1], 6, roi_color, -1)

# -------------------- Dibujo misceláneo --------------------
def draw_bbox(image, box, color=(0,255,0)):
    x1,y1,x2,y2 = box
    cv2.rectangle(image, (x1,y1), (x2,y2), color, 2)

def put_big_text(img, txt, org=(40,120)):
    cv2.putText(img, txt, org, cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0,0,255), 6, cv2.LINE_AA)

# -------------------- Stabilizer --------------------
class Debouncer:
    def __init__(self, window=7):
        self.recent = collections.deque(maxlen=window)

    def push(self, new_label: str) -> str:
        self.recent.append(new_label)
        if not self.recent:
            return ""
        candidates = [x for x in self.recent if x]
        if not candidates:
            return ""
        return max(set(candidates), key=candidates.count)

# -------------------- Clasificador estático --------------------
def classify_letter(lm, W, H, scale_h, wrist_y_for_down):
    """
    Devuelve una letra (ASL) o "" si no hay match.
    Nota: La detección dinámica de 'J' y el trazo de 'Z' se manejan fuera de esta función.
    """
    wrist   = lm_px(lm, 0,  W, H)
    thumb2  = lm_px(lm, 2,  W, H)
    thumb4  = lm_px(lm, 4,  W, H)
    idx5    = lm_px(lm, 5,  W, H)
    idx6    = lm_px(lm, 6,  W, H)
    idx8    = lm_px(lm, 8,  W, H)
    mid10   = lm_px(lm, 10, W, H)
    mid12   = lm_px(lm, 12, W, H)
    rng14   = lm_px(lm, 14, W, H)
    rng16   = lm_px(lm, 16, W, H)
    pky18   = lm_px(lm, 18, W, H)
    pky20   = lm_px(lm, 20, W, H)

    def ndist(a,b):
        return euclid(a,b) / max(1.0, scale_h)

    # Estado extendido
    idx_ext = is_extended_y(idx8, idx6)
    mid_ext = is_extended_y(mid12, mid10)
    rng_ext = is_extended_y(rng16, rng14)
    pky_ext = is_extended_y(pky20, pky18)

    idx_mid_gap = ndist(idx8, mid12)
    mid_rng_gap = ndist(mid12, rng16)

    # “Pulgar extendido real” (para diferenciar I/Y)
    thumb_dist_wrist = ndist(thumb4, wrist)
    thumb_dist_idx   = ndist(thumb4, idx5)
    thb_ext = (thumb_dist_wrist > 0.70) and (thumb_dist_idx > 0.25)

    # A
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext
        and abs(thumb4[1] - idx6[1]) / max(1.0, scale_h) < 0.08):
        return "A"

    # B (ajustada)
    if idx_ext and mid_ext and rng_ext and pky_ext:
        thumb_near_palm = ndist(thumb4, idx6) < TH_NEAR
        fingers_flat = (horiz_ratio(idx8, idx6) < 0.8 and
                        horiz_ratio(mid12, mid10) < 0.8 and
                        horiz_ratio(rng16, rng14) < 0.8 and
                        horiz_ratio(pky20, pky18) < 0.8)
        compact_band = (idx_mid_gap + mid_rng_gap) < 0.24
        if thumb_near_palm and fingers_flat and compact_band:
            return "B"

    # C
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext):
        if TH_CLOSE <= ndist(thumb4, idx8) <= 0.25 and \
           TH_NEAR  <= ndist(thumb4, pky20) <= 0.40 and \
           ndist(idx8, mid12) < 0.20 and ndist(mid12, rng16) < 0.20 and ndist(rng16, pky20) < 0.20:
            return "C"

    # D
    if idx_ext and (not mid_ext) and (not rng_ext) and (not pky_ext) and \
       (ndist(thumb4, mid12) < 0.11 or ndist(thumb4, rng16) < 0.11):
        return "D"

    # E
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext) and \
       (thumb4[1] > idx8[1] and thumb4[1] > mid12[1] and thumb4[1] > rng16[1] and thumb4[1] > pky20[1]):
        return "E"

    # F
    if ndist(idx8, thumb4) < 0.10 and mid_ext and rng_ext and pky_ext and (not idx_ext):
        return "F"

    # G — índice horizontal extendido; pulgar alineado; resto flexionados (y arriba de la muñeca)
    if idx_ext and (not mid_ext) and (not rng_ext) and (not pky_ext):
        index_horizontal = roughly_horizontal(idx8, idx6, 0.55)
        same_y_thumb = abs(idx8[1] - thumb4[1]) / max(1.0, scale_h) < 0.06
        close_thumb_idx = ndist(thumb4, idx8) < TH_MED
        above_wrist = (idx8[1] + 0.02*scale_h) < wrist_y_for_down
        if index_horizontal and same_y_thumb and close_thumb_idx and above_wrist:
            return "G"

    # H — índice y medio horizontales, a la misma altura aprox; resto flexionados
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext):
        same_level = abs(idx8[1]-mid12[1]) / max(1.0, scale_h) < 0.06
        both_h = roughly_horizontal(idx8, idx6, 0.60) and roughly_horizontal(mid12, mid10, 0.60)
        sep_min = abs(idx8[0]-mid12[0]) / max(1.0, scale_h) >= 0.09
        sep_max = abs(idx8[0]-mid12[0]) / max(1.0, scale_h) <= 0.22
        if same_level and both_h and sep_min and sep_max:
            return "H"

    # Y (shaka): pulgar y meñique extendidos; índice/medio/anular flexionados
    if (not idx_ext) and (not mid_ext) and (not rng_ext) and pky_ext and thb_ext:
        return "Y"

    # I: meñique extendido; resto flexionados; pulgar NO extendido
    if pky_ext and (not idx_ext) and (not mid_ext) and (not rng_ext):
        if not thb_ext:
            return "I"

    # K
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext) and idx_mid_gap >= 0.12 and thb_ext \
       and (euclid(thumb4, mid10)/max(1.0, scale_h) < 0.13 or euclid(thumb4, idx5)/max(1.0, scale_h) < 0.13):
        return "K"

    # L
    ang_L = angle(thumb4, idx5, idx8)
    if idx_ext and thb_ext and (not mid_ext) and (not rng_ext) and (not pky_ext) and 70 <= ang_L <= 110:
        return "L"

    # M
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext) \
       and (idx8[1] < thumb4[1] and mid12[1] < thumb4[1] and rng16[1] < thumb4[1]):
        return "M"

    # N
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext) \
       and (idx8[1] < thumb4[1] and mid12[1] < thumb4[1] and rng16[1] > thumb4[1]):
        return "N"

    # O (más selectiva)
    tips = [thumb4, idx8, mid12, rng16, pky20]
    cx = int(sum(t[0] for t in tips)/5); cy = int(sum(t[1] for t in tips)/5)
    def ndc(t): return euclid((cx,cy), t)/max(1.0, scale_h)
    r  = sum(ndc(t) for t in tips) / 5.0
    var = sum(abs(ndc(t) - r) for t in tips) / 5.0
    thumb_idx_dist = euclid(thumb4, idx8)/max(1.0, scale_h)
    if 0.11 < r < 0.22 and var < 0.085 and thumb4[1] > idx6[1] and 0.10 < thumb_idx_dist < 0.22:
        return "O"

    # P (vertical hacia abajo)
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext):
        split = (abs(idx8[0]-mid12[0]) / max(1.0, scale_h)) >= TH_GAP_SPLIT
        thumb_between = thb_ext and (euclid(thumb4, mid10)/max(1.0, scale_h) < TH_NEAR or euclid(thumb4, idx5)/max(1.0, scale_h) < TH_NEAR)
        pointing_down = (idx8[1] > wrist[1] + 0.03*scale_h) and roughly_vertical(idx8, idx6, 0.85)
        if split and thumb_between and pointing_down:
            return "P"

    # Q (G hacia abajo, no horizontal)
    if idx_ext and (not mid_ext) and (not rng_ext) and (not pky_ext):
        same_y_thumb = abs(idx8[1]-thumb4[1]) / max(1.0, scale_h) < 0.06
        close_thumb_idx = euclid(thumb4, idx8)/max(1.0, scale_h) < TH_MED
        below_wrist = (idx8[1] > wrist[1] + 0.03*scale_h)
        not_horizontal = not roughly_horizontal(idx8, idx6, 0.55)
        if same_y_thumb and close_thumb_idx and below_wrist and not_horizontal:
            return "Q"

    # R
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext):
        gap = abs(idx8[0]-mid12[0]) / max(1.0, scale_h)
        higher_idx = (idx8[1] + 0.02*scale_h) < mid12[1]
        if gap < TH_GAP_TIGHT and higher_idx:
            return "R"

    # S (pulgar por fuera)
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext):
        thumb_over_knuckle = euclid(thumb4, idx6)/max(1.0, scale_h) < TH_NEAR and thumb4[1] < idx8[1] + 0.08*scale_h
        thumb_not_between  = euclid(thumb4, idx8)/max(1.0, scale_h) >= TH_CLOSE + 0.02
        if thumb_over_knuckle and thumb_not_between:
            return "S"

    # T (pulgar entre índice y medio)
    if (not idx_ext and not mid_ext and not rng_ext and not pky_ext):
        between_xy = between(thumb4[0], idx8[0], mid12[0]) and between(thumb4[1], idx8[1], mid12[1])
        very_close = (euclid(thumb4, idx8)/max(1.0, scale_h) < TH_CLOSE + 0.01) and (euclid(thumb4, mid12)/max(1.0, scale_h) < TH_NEAR)
        if between_xy and very_close:
            return "T"

    # U
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext) and idx_mid_gap < 0.08 \
       and euclid(thumb4, rng16)/max(1.0, scale_h) < 0.12:
        return "U"

    # V
    if idx_ext and mid_ext and (not rng_ext) and (not pky_ext) and idx_mid_gap >= 0.12:
        return "V"

    # W
    if idx_ext and mid_ext and rng_ext and (not pky_ext) and (idx_mid_gap + mid_rng_gap) >= 0.22:
        return "W"

    # X (índice en gancho; pulgar fuera; índice NO extendido)
    if (not mid_ext) and (not rng_ext) and (not pky_ext) and thb_ext:
        hook = euclid(idx8, idx6)/max(1.0, scale_h) < 0.11 and euclid(idx8, idx5)/max(1.0, scale_h) < 0.18
        curled = hook and (idx8[1] > idx6[1] - 0.01*scale_h)
        if curled and (not is_extended_y(idx8, idx6)):
            return "X"

    return ""

# -------------------- Motor en clase --------------------
class LetterEngine:
    """Encapsula cámara, MediaPipe Hands y la lógica de clasificación.
       Método principal: process_frame(frame_bgr) -> (label, annotated_frame)
    """
    def __init__(self, cam_w=1280, cam_h=720, window=7):
        # MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )

        # Estado
        self.deb = Debouncer(window=window)
        self.last_pinky = collections.deque(maxlen=5)

        # ROI Z
        self.z_roi_points = []
        self.z_roi_active = False
        self.z_last_detection_time = 0
        self.z_detection_status = None
        self.z_roi_bounds = None

        self.cam_w = cam_w
        self.cam_h = cam_h

    def _ensure_roi(self, W, H):
        if self.z_roi_bounds is None:
            roi_width = int(W * 0.25)  # 25% del ancho
            roi_height = int(H * 0.35)  # 35% del alto
            margin = 20
            self.z_roi_bounds = (W - roi_width - margin, margin,
                                 W - margin, roi_height + margin)

    def process_frame(self, frame_bgr):
        """Procesa 1 frame BGR y retorna (label_estable, frame_anotado)."""
        image = cv2.flip(frame_bgr, 1)  # espejo
        H, W, _ = image.shape
        self._ensure_roi(W, H)

        current_time = time.time()
        if self.z_detection_status and (current_time - self.z_last_detection_time) > 2.0:
            self.z_detection_status = None
            self.z_roi_points.clear()
            self.z_roi_active = False

        # MediaPipe
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        label = ""

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # bbox + escala
                x1,y1,x2,y2 = bbox_from_landmarks(image.shape, hand_lms)
                scale_h = max(1, y2 - y1)

                # dibujo landmarks (comentá si querés más FPS)
                self.mp_drawing.draw_landmarks(
                    image, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style()
                )

                # puntos útiles
                idx8  = lm_px(hand_lms, 8,  W, H)
                idx6  = lm_px(hand_lms, 6,  W, H)
                mid12 = lm_px(hand_lms, 12, W, H)
                rng16 = lm_px(hand_lms, 16, W, H)
                pky20 = lm_px(hand_lms, 20, W, H)
                mid10 = lm_px(hand_lms, 10, W, H)
                rng14 = lm_px(hand_lms, 14, W, H)
                pky18 = lm_px(hand_lms, 18, W, H)

                # estado dedos
                idx_ext = is_extended_y(idx8, idx6)
                mid_ext = is_extended_y(mid12, mid10)
                rng_ext = is_extended_y(rng16, rng14)
                pky_ext = is_extended_y(pky20, pky18)

                # ======== ROI Z: tracking del trazo con el índice =========
                z_gesture = idx_ext and (not mid_ext) and (not rng_ext) and (not pky_ext)
                if z_gesture and point_in_roi(idx8, self.z_roi_bounds):
                    if not self.z_roi_active:
                        self.z_roi_active = True
                        self.z_roi_points.clear()
                        self.z_detection_status = None
                    if not self.z_roi_points or euclid(idx8, self.z_roi_points[-1]) > 5:
                        self.z_roi_points.append(idx8)
                elif self.z_roi_active and not point_in_roi(idx8, self.z_roi_bounds):
                    # terminó el trazo: evaluar
                    self.z_roi_active = False
                    x1r, y1r, x2r, y2r = self.z_roi_bounds
                    roi_w = x2r - x1r
                    roi_h = y2r - y1r
                    if analyze_z_pattern(self.z_roi_points, roi_w, roi_h, self.z_roi_bounds):
                        label = "Z"
                        self.z_detection_status = "success"
                        self.z_last_detection_time = current_time
                    else:
                        self.z_detection_status = "fail"
                        self.z_last_detection_time = current_time

                # ======== Clasificación estática (A–Y excepto J) =========
                wrist = lm_px(hand_lms, 0, W, H)
                raw = classify_letter(hand_lms, W, H, scale_h, wrist[1])

                # ======== J dinámica (meñique extendido con caída y cambio de dirección) ========
                if raw == "":
                    if pky_ext and (not idx_ext) and (not mid_ext) and (not rng_ext):
                        self.last_pinky.append(pky20)
                        if len(self.last_pinky) >= 5:
                            dy = self.last_pinky[-1][1] - self.last_pinky[0][1]  # + abajo
                            dx_start = self.last_pinky[len(self.last_pinky)//2][0] - self.last_pinky[0][0]
                            dx_end   = self.last_pinky[-1][0] - self.last_pinky[len(self.last_pinky)//2][0]
                            change_dir = (dx_start == 0) or (dx_start * dx_end < 0)  # reversa en X
                            if dy / max(1.0, scale_h) > 0.12 and change_dir:
                                raw = "J"
                else:
                    # si hubo letra “fija”, reseteo trayectoria J
                    self.last_pinky.clear()

                # ======== Debounce / etiqueta estable (salvo si ya marcó Z) ========
                if not label:
                    label = self.deb.push(raw)
        else:
            # no mano
            self.last_pinky.clear()
            if self.z_roi_active:
                self.z_roi_active = False

        # Dibujo ROI de Z y trazo
        draw_z_roi(image, self.z_roi_bounds, self.z_roi_points, self.z_detection_status)

        return label, image