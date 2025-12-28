"""
System Commands
Copyright (c) 2025 Mac GunJon
Production-Grade System & Utility Commands
"""

import time
import discord
from discord.ext import commands
from discord import app_commands

from core.embeds import info, success, error
from core.config import ENVIRONMENT
from data.store import store


class System(commands.Cog):
    """
    System-level commands for bot diagnostics and information.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    # --------------------------------------------------
    # /botinfo
    # --------------------------------------------------
    @app_commands.command(
        name="botinfo",
        description="View bot information",
    )
    async def botinfo(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=info(
                "UptimeGuard",
                (
                    "🛡️ **Production Uptime Monitoring Bot**\n\n"
                    "**Author:** Mac GunJon\n"
                    "**Hosting:** Render\n"
                    "**Language:** Python\n"
                    "**Framework:** discord.py 2.x\n"
                    "**Purpose:** Website uptime monitoring & alerts"
                ),
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /about (PUBLIC FRIENDLY)
    # --------------------------------------------------
    @app_commands.command(
        name="about",
        description="About UptimeGuard",
    )
    async def about(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=info(
                "About UptimeGuard",
                (
                    "UptimeGuard helps you monitor websites and services\n"
                    "with real-time uptime checks, alerts, and metrics.\n\n"
                    "Built for reliability and simplicity."
                ),
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /uptime
    # --------------------------------------------------
    @app_commands.command(
        name="uptime",
        description="View bot uptime",
    )
    async def uptime(self, interaction: discord.Interaction):
        seconds = int(time.time() - self.start_time)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        await interaction.response.send_message(
            embed=info(
                "Bot Uptime",
                f"⏱️ **Running for:** `{hours}h {minutes}m {seconds}s`",
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /ping
    # --------------------------------------------------
    @app_commands.command(
        name="ping",
        description="Check bot latency",
    )
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)

        await interaction.response.send_message(
            embed=info(
                "Pong 🏓",
                f"**Gateway Latency:** `{latency} ms`",
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /health
    # --------------------------------------------------
    @app_commands.command(
        name="health",
        description="Check internal bot health",
    )
    async def health(self, interaction: discord.Interaction):
        status = "🟢 Healthy" if self.bot.is_ready() else "🔴 Not Ready"

        await interaction.response.send_message(
            embed=info(
                "System Health",
                (
                    f"**Status:** {status}\n"
                    f"**Guilds:** `{len(self.bot.guilds)}`\n"
                    f"**Users Cached:** `{len(self.bot.users)}`\n"
                    f"**Environment:** `{ENVIRONMENT}`"
                ),
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /services (QUICK PREVIEW)
    # --------------------------------------------------
    @app_commands.command(
        name="services",
        description="View monitored services overview",
    )
    async def services(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        targets = await store.all()
        if not targets:
            return await interaction.followup.send(
                embed=info(
                    "Services",
                    "No services are currently being monitored.",
                    requester=interaction.user,
                )
            )

        names = ", ".join(t["name"] for t in targets[:10])
        more = "" if len(targets) <= 10 else f"\n…and {len(targets) - 10} more"

        await interaction.followup.send(
            embed=info(
                "Monitored Services",
                (
                    f"**Total:** `{len(targets)}`\n\n"
                    f"**Services:**\n{names}{more}"
                ),
                requester=interaction.user,
            )
        )

    # --------------------------------------------------
    # /invite
    # --------------------------------------------------
    @app_commands.command(
        name="invite",
        description="Get bot invite link",
    )
    async def invite(self, interaction: discord.Interaction):
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True),
        )

        await interaction.response.send_message(
            embed=info(
                "Invite UptimeGuard",
                f"[👉 Click here to invite the bot]({invite_url})",
                requester=interaction.user,
            ),
            ephemeral=True,
        )

    # --------------------------------------------------
    # /reload (OWNER ONLY – OPTIONAL)
    # --------------------------------------------------
    @app_commands.command(
        name="reload",
        description="Reload bot extensions (owner only)",
    )
    async def reload(self, interaction: discord.Interaction):
        if interaction.user.id != self.bot.owner_id:
            return await interaction.response.send_message(
                embed=error("You are not authorized to use this command."),
                ephemeral=True,
            )

        try:
            for ext in list(self.bot.extensions):
                await self.bot.reload_extension(ext)

            await interaction.response.send_message(
                embed=success(
                    "All extensions reloaded successfully.",
                    requester=interaction.user,
                ),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=error(str(e)),
                ephemeral=True,
            )


# --------------------------------------------------
# COG SETUP
# --------------------------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
