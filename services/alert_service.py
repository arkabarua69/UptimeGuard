"""
Alert Service
Copyright (c) 2025 Mac GunJon
Production-Grade Alert Engine
"""

import discord

from core.logger import setup_logger
from core.config import ALERT_FAILURE_THRESHOLD, ALERT_CHANNEL_ID
from core.embeds import error, success
from data.store import store

logger = setup_logger()


async def handle_alerts(bot: discord.Client, *, url: str):
    """
    Handle DOWN and RECOVERY alerts for a monitored service.
    Internal lookup is done by URL, user-facing alerts use SERVICE NAME.
    """

    # Alerts disabled
    if not ALERT_CHANNEL_ID:
        return

    # Resolve target by URL (internal key)
    target = None
    targets = await store.all()
    for t in targets:
        if t["url"] == url:
            target = t
            break

    if not target:
        return

    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if not channel:
        logger.warning("Alert channel not found or bot lacks access")
        return

    service_name = target["name"]
    service_url = target["url"]

    # --------------------------------------------------
    # DOWN ALERT
    # --------------------------------------------------
    if (
        target["fails"] >= ALERT_FAILURE_THRESHOLD
        and not target["alerted_down"]
    ):
        await channel.send(
            embed=error(
                (
                    "🚨 **Service DOWN**\n\n"
                    f"**Service:** `{service_name}`\n"
                    f"**Failures:** `{target['fails']}` consecutive checks"
                ),
                service_name=service_name,
                service_url=service_url,
                status="DOWN",
            )
        )

        target["alerted_down"] = True
        logger.warning(f"DOWN alert sent | {service_name}")

    # --------------------------------------------------
    # RECOVERY ALERT
    # --------------------------------------------------
    if target["fails"] == 0 and target["alerted_down"]:
        await channel.send(
            embed=success(
                (
                    "✅ **Service RECOVERED**\n\n"
                    f"**Service:** `{service_name}` is back online."
                ),
                service_name=service_name,
                service_url=service_url,
                status="UP",
            )
        )

        target["alerted_down"] = False
        logger.info(f"RECOVERY alert sent | {service_name}")
