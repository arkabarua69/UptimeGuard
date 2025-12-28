"""
Monitor Commands
Copyright (c) 2025 Mac GunJon
Production-Grade Slash Commands
"""

import discord
from discord.ext import commands
from discord import app_commands

from data.store import store
from core.embeds import success, error, info
from services.url_utils import normalize_url


class Monitor(commands.Cog):
    """
    Slash commands for managing monitored services.
    All operations use SERVICE NAME except /add.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------------------------------------------------
    # /add (NAME + URL)
    # --------------------------------------------------
    @app_commands.command(
        name="add",
        description="Add a service to uptime monitoring",
    )
    @app_commands.describe(
        name="Service name (example: Main Website)",
        url="Website URL to monitor",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        name: str,
        url: str,
    ):
        await interaction.response.defer(ephemeral=True)

        normalized = normalize_url(url)
        if not normalized:
            return await interaction.followup.send(
                embed=error("Invalid URL format. Please provide a valid URL."),
            )

        added = await store.add(name=name, url=normalized)
        if not added:
            return await interaction.followup.send(
                embed=error(
                    "This service name or URL is already being monitored."
                ),
            )

        await interaction.followup.send(
            embed=success(
                "Monitoring started successfully.\n\n"
                f"**Service Name:** `{name}`\n"
                f"**URL:** `{normalized}`",
                requester=interaction.user,
            )
        )

    # --------------------------------------------------
    # /remove (NAME ONLY)
    # --------------------------------------------------
    @app_commands.command(
        name="remove",
        description="Remove a monitored service by name",
    )
    async def remove(
        self,
        interaction: discord.Interaction,
        name: str,
    ):
        await interaction.response.defer(ephemeral=True)

        removed = await store.remove_by_name(name)
        if not removed:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        await interaction.followup.send(
            embed=success(
                f"Monitoring removed for service `{name}`.",
                requester=interaction.user,
            )
        )

    # --------------------------------------------------
    # /pause (NAME ONLY)
    # --------------------------------------------------
    @app_commands.command(
        name="pause",
        description="Pause monitoring for a service by name",
    )
    async def pause(
        self,
        interaction: discord.Interaction,
        name: str,
    ):
        await interaction.response.defer(ephemeral=True)

        paused = await store.pause_by_name(name)
        if not paused:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        await interaction.followup.send(
            embed=info(
                "Monitoring Paused",
                f"Monitoring paused for service `{name}`.",
                requester=interaction.user,
            )
        )

    # --------------------------------------------------
    # /resume (NAME ONLY)
    # --------------------------------------------------
    @app_commands.command(
        name="resume",
        description="Resume monitoring for a service by name",
    )
    async def resume(
        self,
        interaction: discord.Interaction,
        name: str,
    ):
        await interaction.response.defer(ephemeral=True)

        resumed = await store.resume_by_name(name)
        if not resumed:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        await interaction.followup.send(
            embed=success(
                f"Monitoring resumed for service `{name}`.",
                requester=interaction.user,
            )
        )


# --------------------------------------------------
# COG SETUP
# --------------------------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Monitor(bot))
