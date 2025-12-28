"""
UptimeGuard Bot
Copyright (c) 2025 Mac GunJon
Production-Grade Entry Point
"""

import asyncio
import signal
import sys
import threading
import discord
from discord.ext import commands

from core.config import BOT_TOKEN
from core.logger import setup_logger
from services.monitor_service import start_monitor_loop
from web.keep_alive import run_server 

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logger = setup_logger()

# --------------------------------------------------
# INTENTS
# --------------------------------------------------
intents = discord.Intents.default()

# --------------------------------------------------
# BOT INSTANCE
# --------------------------------------------------
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
)

# --------------------------------------------------
# SAFE EXTENSION LOADER
# --------------------------------------------------
EXTENSIONS = (
    "commands.monitor",
    "commands.stats",
    "commands.system",
)


async def load_extensions_safe():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            logger.info(f"Loaded extension: {ext}")
        except Exception as e:
            logger.exception(f"Failed to load extension {ext}", exc_info=e)


# --------------------------------------------------
# READY EVENT
# --------------------------------------------------
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logger.info(f"Bot ready | User={bot.user} | ID={bot.user.id}")
    except Exception as e:
        logger.exception("Slash command sync failed", exc_info=e)

    try:
        start_monitor_loop(bot)
        logger.info("Monitor service started")
    except Exception as e:
        logger.exception("Failed to start monitor service", exc_info=e)


# --------------------------------------------------
# GLOBAL ERROR HANDLING
# --------------------------------------------------
@bot.event
async def on_error(event, *args, **kwargs):
    logger.exception(f"Unhandled event error: {event}")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    logger.error(f"Slash command error: {error}")

    if interaction.response.is_done():
        return

    await interaction.response.send_message(
        "⚠️ An internal error occurred. Please try again later.",
        ephemeral=True,
    )


# --------------------------------------------------
# GRACEFUL SHUTDOWN (RENDER SAFE)
# --------------------------------------------------
def shutdown_handler():
    logger.warning("Shutdown signal received. Closing bot safely...")
    asyncio.create_task(bot.close())


def register_signal_handlers():
    try:
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown_handler)
    except NotImplementedError:
        # Windows fallback
        pass


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
async def main():
    if not BOT_TOKEN:
        logger.critical("DISCORD_TOKEN is missing. Bot cannot start.")
        sys.exit(1)

    # --------------------------------------------------
    # START WEB SERVER (RENDER REQUIREMENT)
    # --------------------------------------------------
    threading.Thread(
        target=run_server,
        name="WebServer",
        daemon=True,
    ).start()
    logger.info("Web server started (Render)")

    register_signal_handlers()

    try:
        async with bot:
            await load_extensions_safe()
            await bot.start(BOT_TOKEN)
    except discord.LoginFailure:
        logger.critical("Invalid Discord token. Login failed.")
        sys.exit(1)
    except Exception as e:
        logger.critical("Fatal startup error", exc_info=e)
        sys.exit(1)


# --------------------------------------------------
# ENTRYPOINT
# --------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot interrupted manually")
