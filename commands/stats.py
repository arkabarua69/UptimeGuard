"""
Stats Commands
Copyright (c) 2025 Mac GunJon
Production-Grade Monitoring Statistics
"""

import discord
from discord.ext import commands
from discord import app_commands

from data.store import store
from core.embeds import info, error, success


class Stats(commands.Cog):
    """
    Read-only monitoring statistics & metrics commands.
    All commands operate using SERVICE NAME.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------------------------------------------------
    # /status (ALL SERVICES)
    # --------------------------------------------------
    @app_commands.command(
        name="status",
        description="View status of all monitored services",
    )
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        targets = await store.all()
        if not targets:
            return await interaction.followup.send(
                embed=info(
                    "Uptime Status",
                    "No services are currently being monitored.",
                    requester=interaction.user,
                )
            )

        lines = []
        for t in targets:
            status = t["last_status"]
            paused = t["paused"]

            if paused:
                badge = "⏸️ PAUSED"
            elif isinstance(status, int) and status < 400:
                badge = "🟢 UP"
            elif status:
                badge = "🔴 DOWN"
            else:
                badge = "⚪ UNKNOWN"

            lines.append(f"**{t['name']}** → {badge}")

        await interaction.followup.send(
            embed=info(
                "Uptime Status",
                "\n".join(lines),
                requester=interaction.user,
            )
        )

    # --------------------------------------------------
    # /details (SINGLE SERVICE)
    # --------------------------------------------------
    @app_commands.command(
        name="details",
        description="View detailed status of a service",
    )
    async def details(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)

        target = await store.get_by_name(name)
        if not target:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        status = target["last_status"]
        if target["paused"]:
            state = "PAUSED"
        elif isinstance(status, int) and status < 400:
            state = "UP"
        elif status:
            state = "DOWN"
        else:
            state = "UNKNOWN"

        await interaction.followup.send(
            embed=info(
                "Service Details",
                (
                    f"**Service:** `{target['name']}`\n"
                    f"**URL:** `{target['url']}`\n"
                    f"**Last Status:** `{status}`\n"
                    f"**Fails:** `{target['fails']}`\n"
                    f"**Last Checked:** `{target['last_checked']}`"
                ),
                requester=interaction.user,
                service_name=target["name"],
                service_url=target["url"],
                status=state,
            )
        )

    # --------------------------------------------------
    # /metrics
    # --------------------------------------------------
    @app_commands.command(
        name="metrics",
        description="View uptime metrics for a service",
    )
    async def metrics(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)

        target = await store.get_by_name(name)
        if not target:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        uptime = await store.uptime_percentage(name)
        avg_latency = await store.average_latency(name)

        await interaction.followup.send(
            embed=info(
                "Service Metrics",
                (
                    f"**Uptime:** `{uptime:.2f}%`\n"
                    f"**Average Latency:** `{avg_latency:.3f}s`\n"
                    f"**Total Checks:** `{target['checks']}`\n"
                    f"**Successful Checks:** `{target['success']}`"
                ),
                requester=interaction.user,
                service_name=target["name"],
                service_url=target["url"],
            )
        )

    # --------------------------------------------------
    # /latency
    # --------------------------------------------------
    @app_commands.command(
        name="latency",
        description="View recent response times for a service",
    )
    async def latency(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)

        target = await store.get_by_name(name)
        if not target or not target["response_times"]:
            return await interaction.followup.send(
                embed=error("No latency data available for this service."),
            )

        times = ", ".join(f"{t:.2f}s" for t in target["response_times"])

        await interaction.followup.send(
            embed=info(
                "Latency History",
                f"**Recent Response Times:**\n{times}",
                requester=interaction.user,
                service_name=target["name"],
                service_url=target["url"],
            )
        )

    # --------------------------------------------------
    # /clearstats
    # --------------------------------------------------
    @app_commands.command(
        name="clearstats",
        description="Reset metrics for a service",
    )
    async def clearstats(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)

        target = await store.get_by_name(name)
        if not target:
            return await interaction.followup.send(
                embed=error(f"No service found with name `{name}`."),
            )

        # reset metrics safely
        target["checks"] = 0
        target["success"] = 0
        target["fails"] = 0
        target["response_times"].clear()

        await interaction.followup.send(
            embed=success(
                "Metrics have been reset successfully.",
                requester=interaction.user,
                service_name=target["name"],
                service_url=target["url"],
            )
        )

    # --------------------------------------------------
    # /count
    # --------------------------------------------------
    @app_commands.command(
        name="count",
        description="View total monitored services",
    )
    async def count(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        total = len(await store.all())

        await interaction.followup.send(
            embed=info(
                "Monitoring Count",
                f"Currently monitoring **{total}** service(s).",
                requester=interaction.user,
            )
        )


# --------------------------------------------------
# COG SETUP
# --------------------------------------------------
async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
