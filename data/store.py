"""
In-Memory Store (MongoDB Ready)
Copyright (c) 2025 Mac GunJon
Production-Grade Data Layer
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from core.logger import setup_logger

logger = setup_logger()


class MonitorStore:
    """
    Async-safe in-memory store.
    URL is the internal key.
    All user operations are performed via SERVICE NAME.
    """

    def __init__(self):
        self._targets: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    # --------------------------------------------------
    # INTERNAL RESOLVER
    # --------------------------------------------------
    def _find_by_name(self, name: str) -> Optional[dict]:
        for target in self._targets.values():
            if target["name"].lower() == name.lower():
                return target
        return None

    # --------------------------------------------------
    # CREATE (NAME + URL)
    # --------------------------------------------------
    async def add(self, *, name: str, url: str) -> bool:
        async with self._lock:
            # duplicate URL
            if url in self._targets:
                logger.warning(f"Duplicate URL attempt: {url}")
                return False

            # duplicate NAME
            if self._find_by_name(name):
                logger.warning(f"Duplicate service name attempt: {name}")
                return False

            self._targets[url] = {
                # identity
                "name": name,
                "url": url,

                # control
                "paused": False,

                # status
                "last_status": None,
                "last_checked": None,

                # failure tracking
                "fails": 0,
                "alerted_down": False,

                # metrics
                "checks": 0,
                "success": 0,
                "response_times": [],

                # audit
                "created_at": datetime.utcnow(),
            }

            logger.info(f"Monitoring started | {name} -> {url}")
            return True

    # --------------------------------------------------
    # DELETE (NAME)
    # --------------------------------------------------
    async def remove_by_name(self, name: str) -> bool:
        async with self._lock:
            target = self._find_by_name(name)
            if not target:
                return False

            del self._targets[target["url"]]
            logger.info(f"Monitoring removed | {name}")
            return True

    # --------------------------------------------------
    # READ
    # --------------------------------------------------
    async def get_by_name(self, name: str) -> Optional[dict]:
        async with self._lock:
            return self._find_by_name(name)

    async def all(self) -> List[dict]:
        async with self._lock:
            return list(self._targets.values())

    # --------------------------------------------------
    # CONTROL (NAME)
    # --------------------------------------------------
    async def pause_by_name(self, name: str) -> bool:
        async with self._lock:
            target = self._find_by_name(name)
            if not target:
                return False

            target["paused"] = True
            logger.info(f"Monitoring paused | {name}")
            return True

    async def resume_by_name(self, name: str) -> bool:
        async with self._lock:
            target = self._find_by_name(name)
            if not target:
                return False

            target["paused"] = False
            logger.info(f"Monitoring resumed | {name}")
            return True

    # --------------------------------------------------
    # STATUS + METRICS UPDATE (URL INTERNAL)
    # --------------------------------------------------
    async def update_status(
        self,
        *,
        url: str,
        status,
        failed: bool,
        response_time: float | None=None,
    ):
        async with self._lock:
            target = self._targets.get(url)
            if not target:
                return

            now = datetime.utcnow()

            # status
            target["last_status"] = status
            target["last_checked"] = now

            # metrics
            target["checks"] += 1

            if failed:
                target["fails"] += 1
            else:
                target["fails"] = 0
                target["success"] += 1
                target["alerted_down"] = False

            if response_time is not None:
                target["response_times"].append(response_time)
                target["response_times"] = target["response_times"][-20:]

    # --------------------------------------------------
    # DERIVED METRICS (NAME)
    # --------------------------------------------------
    async def uptime_percentage(self, name: str) -> float:
        async with self._lock:
            target = self._find_by_name(name)
            if not target or target["checks"] == 0:
                return 0.0
            return (target["success"] / target["checks"]) * 100

    async def average_latency(self, name: str) -> float:
        async with self._lock:
            target = self._find_by_name(name)
            if not target or not target["response_times"]:
                return 0.0
            return sum(target["response_times"]) / len(target["response_times"])

    # --------------------------------------------------
    # FUTURE DB HOOKS
    # --------------------------------------------------
    async def load_from_db(self):
        pass

    async def save_to_db(self):
        pass


# --------------------------------------------------
# SINGLETON INSTANCE
# --------------------------------------------------
store = MonitorStore()
