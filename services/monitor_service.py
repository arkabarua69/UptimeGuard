"""
Monitoring Service
Copyright (c) 2025 Mac GunJon
Production-Grade Uptime Monitoring Engine
"""

import asyncio
import time
from typing import List

import aiohttp
import discord

from core.config import CHECK_INTERVAL, REQUEST_TIMEOUT
from core.logger import setup_logger
from data.store import store
from services.alert_service import handle_alerts

logger = setup_logger()

# --------------------------------------------------
# ENGINE CONFIG
# --------------------------------------------------
MAX_CONCURRENT_CHECKS = 10
MAX_RETRIES = 2
RETRY_BACKOFF = 2  # exponential base (seconds)


# --------------------------------------------------
# SINGLE TARGET CHECK
# --------------------------------------------------
async def check_target(
    *,
    bot: discord.Client,
    session: aiohttp.ClientSession,
    target: dict,
    semaphore: asyncio.Semaphore,
):
    url = target["url"]

    # absolute safety: paused services do nothing
    if target.get("paused"):
        logger.debug(f"Skipped paused service: {target['name']}")
        return

    async with semaphore:
        attempt = 0

        while attempt <= MAX_RETRIES:
            start_time = time.monotonic()

            try:
                async with session.get(
                    url,
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    elapsed = round(time.monotonic() - start_time, 3)

                    await store.update_status(
                        url=url,
                        status=response.status,
                        failed=False,
                        response_time=elapsed,
                    )

                    logger.info(
                        f"UP | {target['name']} | {response.status} | {elapsed}s"
                    )

                    # alert handling (RECOVERY)
                    await handle_alerts(bot, url=url)
                    return

            except asyncio.TimeoutError:
                logger.warning(f"Timeout | {target['name']}")

            except aiohttp.ClientError as e:
                logger.warning(f"HTTP error | {target['name']} | {e}")

            except Exception as e:
                logger.exception(
                    f"Unexpected error | {target['name']}", exc_info=e
                )

            attempt += 1

            if attempt <= MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF ** attempt)

        # --------------------------------------------------
        # ALL RETRIES FAILED → MARK DOWN
        # --------------------------------------------------
        await store.update_status(
            url=url,
            status="DOWN",
            failed=True,
        )

        logger.error(f"DOWN | {target['name']} | retries exhausted")

        # alert handling (DOWN)
        await handle_alerts(bot, url=url)


# --------------------------------------------------
# ONE MONITOR CYCLE
# --------------------------------------------------
async def monitor_cycle(
    *,
    bot: discord.Client,
    session: aiohttp.ClientSession,
):
    targets = await store.all()

    if not targets:
        logger.debug("No monitored services found")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)

    tasks: List[asyncio.Task] = [
        asyncio.create_task(
            check_target(
                bot=bot,
                session=session,
                target=target,
                semaphore=semaphore,
            )
        )
        for target in targets
    ]

    await asyncio.gather(*tasks, return_exceptions=True)


# --------------------------------------------------
# MAIN LOOP (IMMORTAL)
# --------------------------------------------------
async def monitor_loop(bot: discord.Client):
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        logger.info("Uptime monitoring loop started")

        while True:
            try:
                await monitor_cycle(bot=bot, session=session)
            except Exception as e:
                logger.critical("Monitor cycle crashed", exc_info=e)

            await asyncio.sleep(CHECK_INTERVAL)


# --------------------------------------------------
# BOT INTEGRATION
# --------------------------------------------------
def start_monitor_loop(bot: discord.Client):
    """
    Starts the monitoring loop as a background task.
    Safe for Render & long-running deployments.
    """
    task = bot.loop.create_task(monitor_loop(bot))
    task.add_done_callback(_monitor_crash_handler)

    logger.info("Monitor loop task scheduled")


def _monitor_crash_handler(task: asyncio.Task):
    if task.cancelled():
        logger.warning("Monitor loop task cancelled")
        return

    if task.exception():
        logger.critical(
            "Monitor loop task crashed unexpectedly",
            exc_info=task.exception(),
        )
