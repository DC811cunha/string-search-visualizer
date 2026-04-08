"""Aplicação Flask para visualização e comparação de algoritmos de busca em strings."""
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from algorithms import STRATEGY_REGISTRY, SearchStrategy

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"txt"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
MAX_DISPLAY_CHARS = 50_000
MAX_STEP_CHARS = 2_000
BENCHMARK_RUNS = 7

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def ensure_upload_folder() -> None:
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def make_unique_filename(filename: str) -> str:
    safe_name = secure_filename(filename)
    if not safe_name:
        raise ValueError("Nome de arquivo inválido")
    stem, dot, suffix = safe_name.rpartition(".")
    stem = stem or suffix
    extension = suffix if dot else "txt"
    unique = uuid.uuid4().hex[:8]
    return f"{stem}_{unique}.{extension}"


def safe_upload_path(filename: str) -> Path:
    safe_name = secure_filename(filename)
    if not safe_name:
        raise ValueError("Nome de arquivo inválido")
    path = (UPLOAD_FOLDER / safe_name).resolve()
    if UPLOAD_FOLDER.resolve() not in path.parents and path != UPLOAD_FOLDER.resolve():
        raise ValueError("Caminho de upload inválido")
    return path


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize_text(value: str) -> str:
    return value.casefold()


def serialize_strategy(strategy: SearchStrategy) -> Dict[str, Any]:
    return {
        "name": strategy.name,
        "complexity": strategy.complexity_dict(),
        "notes": strategy.notes,
    }


def benchmark_search(strategy: SearchStrategy, text: str, pattern: str, runs: int = BENCHMARK_RUNS) -> Dict[str, Any]:
    run_results = [strategy.search(text, pattern) for _ in range(max(1, runs))]
    base = run_results[-1]
    times = [r["time_ns"] for r in run_results]
    avg_ns = int(mean(times))
    best_ns = min(times)
    worst_ns = max(times)

    response = dict(base)
    response["time_ns"] = avg_ns
    response["benchmark_runs"] = len(run_results)
    response["time_ns_best"] = best_ns
    response["time_ns_worst"] = worst_ns
    response["time_ms"] = avg_ns / 1_000_000
    response["time_ms_best"] = best_ns / 1_000_000
    response["time_ms_worst"] = worst_ns / 1_000_000
    response["complexity"] = strategy.complexity_dict()
    response["notes"] = strategy.notes
    response["algorithm"] = strategy.name
    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_large_upload(_: RequestEntityTooLarge):
    return jsonify({"error": "Arquivo excede o limite de 16 MB."}), 413


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/algorithms", methods=["GET"])
def list_algorithms():
    return jsonify({key: serialize_strategy(strategy) for key, strategy in STRATEGY_REGISTRY.items()})


@app.route("/upload", methods=["POST"])
def upload_files():
    ensure_upload_folder()
    if "files" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    files = request.files.getlist("files")
    saved_files: List[str] = []

    for file in files:
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            continue

        unique_name = make_unique_filename(file.filename)
        destination = safe_upload_path(unique_name)
        file.save(destination)
        saved_files.append(destination.name)

    if not saved_files:
        return jsonify({"error": "Envie pelo menos um arquivo .txt válido."}), 400

    return jsonify({"files": saved_files, "message": "Upload concluído com sucesso."})


@app.route("/upload/<filename>", methods=["DELETE"])
def delete_file(filename: str):
    try:
        path = safe_upload_path(filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not path.exists():
        return jsonify({"error": "Arquivo não encontrado."}), 404

    path.unlink()
    return jsonify({"deleted": path.name})


@app.route("/search", methods=["POST"])
def search_pattern():
    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "").strip()
    algorithm_key = data.get("algorithm", "naive")
    filenames = data.get("files", [])

    if not pattern:
        return jsonify({"error": "Informe a string de busca."}), 400
    if not filenames:
        return jsonify({"error": "Selecione pelo menos um arquivo."}), 400

    strategy = STRATEGY_REGISTRY.get(algorithm_key)
    if strategy is None:
        return jsonify({"error": "Algoritmo inválido."}), 400

    normalized_pattern = normalize_text(pattern)
    results: List[Dict[str, Any]] = []

    for filename in filenames:
        try:
            path = safe_upload_path(filename)
        except ValueError:
            continue
        if not path.exists():
            continue

        original_text = load_text_file(path)
        normalized_text = normalize_text(original_text)
        result = benchmark_search(strategy, normalized_text, normalized_pattern)
        result["filename"] = path.name
        result["display_filename"] = path.name.rsplit("_", 1)[0] + ".txt" if "_" in path.stem else path.name
        result["original_text"] = original_text[:MAX_DISPLAY_CHARS]
        result["text_truncated"] = len(original_text) > MAX_DISPLAY_CHARS
        result["full_text_len"] = len(original_text)
        results.append(result)

    return jsonify({"results": results})


@app.route("/step", methods=["POST"])
def step_by_step():
    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "").strip()
    algorithm_key = data.get("algorithm", "naive")
    filename = data.get("file", "")

    if not pattern or not filename:
        return jsonify({"error": "Arquivo e padrão são obrigatórios."}), 400

    strategy = STRATEGY_REGISTRY.get(algorithm_key)
    if strategy is None:
        return jsonify({"error": "Algoritmo inválido."}), 400

    try:
        path = safe_upload_path(filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not path.exists():
        return jsonify({"error": "Arquivo não encontrado."}), 404

    original_text = load_text_file(path)
    normalized_text = normalize_text(original_text)
    normalized_pattern = normalize_text(pattern)
    step_text = normalized_text[:MAX_STEP_CHARS]
    steps = strategy.search_step_by_step(step_text, normalized_pattern)

    for step in steps:
        if "lps" in step:
            step["lps"] = str(step["lps"])
        if "bad_char" in step:
            step["bad_char"] = str(step["bad_char"])

    return jsonify({
        "steps": steps,
        "text": step_text,
        "original_text": original_text[:MAX_DISPLAY_CHARS],
        "pattern": normalized_pattern,
        "algorithm": strategy.name,
        "notes": strategy.notes,
        "complexity": strategy.complexity_dict(),
        "step_truncated": len(normalized_text) > MAX_STEP_CHARS,
        "step_chars_used": len(step_text),
        "full_text_len": len(original_text),
    })


@app.route("/compare", methods=["POST"])
def compare_algorithms():
    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "").strip()
    filename = data.get("file", "")

    if not pattern or not filename:
        return jsonify({"error": "Arquivo e padrão são obrigatórios para comparação."}), 400

    try:
        path = safe_upload_path(filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not path.exists():
        return jsonify({"error": "Arquivo não encontrado."}), 404

    original_text = load_text_file(path)
    normalized_text = normalize_text(original_text)
    normalized_pattern = normalize_text(pattern)

    results = []
    for key, strategy in STRATEGY_REGISTRY.items():
        result = benchmark_search(strategy, normalized_text, normalized_pattern)
        result["key"] = key
        results.append(result)

    results.sort(key=lambda item: item["time_ns"])
    return jsonify({"results": results, "file": path.name})


if __name__ == "__main__":
    ensure_upload_folder()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(debug=debug, port=port)
