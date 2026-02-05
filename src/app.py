from __future__ import annotations

from dataclasses import fields
import os
from typing import Any

from flask import Flask, jsonify, request

from thermal_model import ThermalInputs, results_as_dict, solve_thermal_model


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def health() -> Any:
        return jsonify({"status": "ok", "endpoints": ["GET /thermal", "POST /thermal"]})

    @app.get("/thermal")
    def thermal_default() -> Any:
        inputs = ThermalInputs()
        results = solve_thermal_model(inputs)
        return jsonify({"inputs": inputs.__dict__, "results": results_as_dict(results)})

    @app.post("/thermal")
    def thermal_custom() -> Any:
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "JSON body must be an object"}), 400

        allowed = {f.name for f in fields(ThermalInputs)}
        unknown = sorted(set(payload.keys()) - allowed)
        if unknown:
            return jsonify({"error": "Unknown fields", "unknown": unknown, "allowed": sorted(allowed)}), 400

        try:
            inputs = ThermalInputs(**payload)
        except TypeError as e:
            return jsonify({"error": str(e)}), 400

        results = solve_thermal_model(inputs)
        return jsonify({"inputs": inputs.__dict__, "results": results_as_dict(results)})

    return app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug, use_reloader=False)
