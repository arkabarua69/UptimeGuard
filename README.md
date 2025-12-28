# 🛡️ UptimeGuard

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

**UptimeGuard** is a Discord bot for monitoring website and service uptime.  
It tracks availability, latency, and sends downtime & recovery alerts using slash commands.

**Support Server:** https://discord.gg/rU2pu9vvnk

---

## ✅ Features
- Uptime monitoring
- Downtime & recovery alerts
- Latency tracking
- Name-based service management
- Slash commands only
- Render-ready web server

---

## ⚙️ Requirements
- Python 3.10+
- discord.py 2.x

---

## 📦 Installation
```bash
pip install -r requirements.txt
python bot.py
```
# UptimeGuard – Release Notes

## 🚀 Version 1.0.0 – Initial Production Release

### ✅ Core Features
- Website & service uptime monitoring
- Name-based service management
- Slash command interface
- Downtime & recovery alerts
- Latency and uptime metrics
- Failure threshold protection

### ⚙️ Infrastructure
- Async-safe monitoring engine
- Modular architecture
- Render-ready Flask web server
- Secure environment variable handling

### 🔒 Security
- No secrets committed
- GitHub push-protection compatible
- Token rotation friendly

### 📦 Commands
- `/add`, `/remove`, `/pause`, `/resume`
- `/status`, `/details`, `/metrics`, `/latency`
- `/botinfo`, `/uptime`, `/health`

### 🧠 Stability
- Auto-retry with backoff
- Safe background tasks
- Graceful shutdown handling

---

## 🛣️ Planned for Future Releases
- MongoDB persistence
- Per-service alert channels
- Alert cooldowns
- Web dashboard
- SLA reports

---

**Maintainer:** Mac GunJon  
**Status:** Production Ready
