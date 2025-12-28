"""
UptimeGuard Web Server
Used for Render health checks & uptime
"""

from flask import Flask, jsonify
import os
import logging

app = Flask(__name__)

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UptimeGuard-Web")


# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "status": "ok",
            "service": "UptimeGuard",
            "message": "Bot is running",
        }
    ), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"health": "good"}), 200


# --------------------------------------------------
# SERVER RUNNER (RENDER SAFE)
# --------------------------------------------------
def run_server():
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting web server on 0.0.0.0:{port}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,  # MUST be False in production
        use_reloader=False  # Prevent duplicate threads
    )
