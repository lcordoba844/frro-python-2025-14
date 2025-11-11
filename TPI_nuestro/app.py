# app.py
import os, sys, subprocess
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from services import get_top
from services import save_score  # si lo necesitás en el futuro

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_SCRIPT = os.path.join(BASE_DIR, "tpi_juego.py")

app = Flask(__name__)
game_proc = None

# --- Control de juego ---
def is_game_running():
    global game_proc
    return (game_proc is not None) and (game_proc.poll() is None)

def start_game():
    global game_proc
    if is_game_running():
        return False, "El juego ya está corriendo."
    py = sys.executable
    creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    try:
        game_proc = subprocess.Popen([py, GAME_SCRIPT], cwd=BASE_DIR, creationflags=creationflags)
        return True, "Juego iniciado."
    except Exception as e:
        return False, f"No se pudo iniciar: {e}"

def stop_game():
    global game_proc
    if not is_game_running():
        return False, "No hay juego corriendo."
    try:
        game_proc.terminate()
        return True, "Juego detenido."
    except Exception as e:
        return False, f"Error al detener: {e}"

# --- Rutas ---
@app.route("/")
def home():
    rows = get_top(20)
    return render_template("leaderboard.html", rows=rows, now=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

@app.route("/api/top")
def api_top():
    limit = int(request.args.get("limit", 20))
    q = (request.args.get("q") or "").strip().lower()
    rows = get_top(limit*3)
    if q:
        rows = [r for r in rows if q in (r[0] or "").lower()]
    rows = rows[:limit]
    return jsonify({"rows": rows, "running": is_game_running()})

@app.route("/api/play", methods=["POST"])
def api_play():
    ok, msg = start_game()
    return jsonify({"ok": ok, "msg": msg, "running": is_game_running()})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    ok, msg = stop_game()
    return jsonify({"ok": ok, "msg": msg, "running": is_game_running()})

if __name__ == "__main__":
    app.run(debug=True)
