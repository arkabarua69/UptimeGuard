"""
Embed Factory
Copyright (c) 2025 Mac GunJon
Production-Grade Discord Embeds
"""

from datetime import datetime
import discord

# --------------------------------------------------
# BRAND COLORS
# --------------------------------------------------
PRIMARY = 0x5865F2
SUCCESS = 0x57F287
ERROR = 0xED4245
WARNING = 0xFEE75C
INFO = 0x3498DB

# --------------------------------------------------
# BRANDING
# --------------------------------------------------
BOT_NAME = "UptimeGuard"
AUTHOR_TEXT = "UptimeGuard Monitoring System"
FOOTER_TEXT = "© Deploy By • Mac GunJon"
DEFAULT_ICON = "https://cdn.discordapp.com/embed/avatars/0.png"

# --------------------------------------------------
# STATUS BADGES
# --------------------------------------------------
STATUS_BADGES = {
    "UP": "🟢 UP",
    "DOWN": "🔴 DOWN",
    "PAUSED": "⏸️ PAUSED",
    "UNKNOWN": "⚪ UNKNOWN",
}


# --------------------------------------------------
# BASE EMBED BUILDER
# --------------------------------------------------
def build_embed(
    *,
    title: str,
    description: str,
    color: int=PRIMARY,
    requester: discord.User | None=None,
    service_name: str | None=None,
    service_url: str | None=None,
    status: str | None=None,
    thumbnail: str | None=None,
):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )

    embed.set_author(name=AUTHOR_TEXT, icon_url=DEFAULT_ICON)
    embed.set_footer(text=FOOTER_TEXT)

    # -----------------------------
    # SERVICE BLOCK
    # -----------------------------
    if service_name:
        embed.add_field(
            name="Service",
            value=f"**{service_name}**",
            inline=False,
        )

    if service_url:
        embed.add_field(
            name="URL",
            value=f"`{service_url}`",
            inline=False,
        )

    if status:
        badge = STATUS_BADGES.get(status.upper(), status)
        embed.add_field(
            name="Status",
            value=badge,
            inline=True,
        )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if requester:
        embed.add_field(
            name="Requested By",
            value=f"{requester.mention} (`{requester.id}`)",
            inline=False,
        )

    return embed


# --------------------------------------------------
# COMMON EMBED TYPES
# --------------------------------------------------
def success(
    message: str,
    requester: discord.User | None=None,
    **kwargs,
):
    return build_embed(
        title="✅ Operation Successful",
        description=message,
        color=SUCCESS,
        requester=requester,
        **kwargs,
    )


def error(
    message: str,
    requester: discord.User | None=None,
    **kwargs,
):
    return build_embed(
        title="❌ Operation Failed",
        description=message,
        color=ERROR,
        requester=requester,
        **kwargs,
    )


def warning(
    message: str,
    requester: discord.User | None=None,
    **kwargs,
):
    return build_embed(
        title="⚠️ Warning",
        description=message,
        color=WARNING,
        requester=requester,
        **kwargs,
    )


def info(
    title: str,
    message: str,
    requester: discord.User | None=None,
    **kwargs,
):
    return build_embed(
        title=f"ℹ️ {title}",
        description=message,
        color=INFO,
        requester=requester,
        **kwargs,
    )
