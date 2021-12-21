import datetime
import platform
from dataclasses import dataclass
from time import time

import hikari
import lightbulb
import psutil
from bot import ROOT_DIR
from pygount import SourceAnalysis
import io
from PIL import Image

plugin = lightbulb.Plugin("info")


@dataclass
class CodeCounter:
    code: int = 0
    docs: int = 0
    empty: int = 0

    def count(self) -> "CodeCounter":
        for file in ROOT_DIR.rglob("*.py"):
            analysis = SourceAnalysis.from_file(file, "pygount", encoding="utf-8")
            self.code += analysis.code_count
            self.docs += analysis.documentation_count
            self.empty += analysis.empty_count

        return self


counter = CodeCounter()


@plugin.command
@lightbulb.option(
    "target",
    "The target, if supplied, to get the information for",
    hikari.User,
    required=False,
)
@lightbulb.command(
    "userinfo",
    "See all the information for yourself or another user",
    auto_defer=True,
    ephemeral=False,
)
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def userinfo(ctx: lightbulb.context.Context) -> None:
    # target = ctx.options.target if ctx.options.target is not None else ctx.user
    # target = ctx.get_guild().get_member(target)

    target = ctx.get_guild().get_member(
        ctx.options.target if ctx.options.target is not None else ctx.user
    )
    user = await ctx.bot.rest.fetch_user(target.id)

    if not target:
        await ctx.respond("They are not in this server")
        return

    created_at = int(target.created_at.timestamp())
    joined_at = int(target.joined_at.timestamp())
    roles = (sorted((await target.fetch_roles())[1:], key=lambda role: role.position))[
        ::-1
    ]
    boosting = bool(target.premium_since)

    embed = hikari.Embed(
        title=f"User information for `{target.username}#{target.discriminator}` {f'(AKA `{target.display_name}`)' if target.display_name != target.username else ''}",
        description=f"User ID: {target.id}",
        colour=target.get_top_role().colour,
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    ).set_footer(
        text=f"Command invoked by {ctx.member.display_name}",
        icon=ctx.member.avatar_url
        if ctx.member.avatar_url
        else ctx.member.default_avatar_url,
    )

    # embed.set_thumbnail(
    #     target.avatar_url if target.avatar_url else target.default_avatar_url
    # )

    banner_url = (
        f"{str(user.banner_url).split('size=')[0]}size=70096"
        if user.banner_url
        else None
    )
    if user.accent_color or user.banner_url:
        if user.banner_url:
            embed.set_image(user.banner_url)
        elif user.accent_color:
            im = Image.new("RGB", (200, 200), user.accent_color.rgb)
            buffer = io.BytesIO()

            im.save(buffer, "png")
            buffer.seek(0)

            bytes = hikari.Bytes(buffer, "accent colour.png")
            embed.set_image(bytes)

    fields = [
        ("Bot?", target.is_bot, True),
        ("Created account on", f"<t:{created_at}:d> (<t:{created_at}:R>)", True),
        ("Joined server on", f"<t:{joined_at}:d> (<t:{joined_at}:R>)", True),
        ("Is pending?", target.is_pending, True),
        ("Voice muted?", "Yes" if target.is_mute else "No", True),
        ("Voice deafened?", "Yes" if target.is_deaf else "No", True),
        ("Boosting?", "Yes" if boosting else "No", True),
    ]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    if boosting:
        embed.add_filed(
            name="boosting since",
            value=f"<t:{int(target.premium_since.timestamp())}:d> (<t:{int(target.premium_since.timestamp())}:R>)",
            inline=False,
        )

    embed.add_field(
        name="Roles", value=f", ".join(role.mention for role in roles), inline=False
    )

    await ctx.respond(embed=embed)
    # await ctx.respond("Updated code")


@plugin.command
@lightbulb.command("botinfo", "See information my information")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def botinfo(ctx: lightbulb.context.Context) -> None:
    with (proc := psutil.Process()).oneshot():
        uptime = time() - proc.create_time()
        cpu_times = proc.cpu_times()
        total_memory = psutil.virtual_memory().total / (1024 ** 2)
        memory_percent = proc.memory_percent()
        memory_usage = total_memory * (memory_percent / 100)

    embed = hikari.Embed(
        title="Bot information",
        description="Phloexia is a bot developed by <@700336923264155719> and <@709613711475605544>",
        colour=0xFFFF00,
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    fields = [
        ("Bot version", ctx.bot.bot_version, True),
        ("Python version", platform.python_version(), True),
        ("Hikari version", hikari.__version__, True),
        ("Lightbulb version", lightbulb.__version__, True),
        ("Uptime", datetime.timedelta(seconds=uptime), True),
        (
            "Memory usage",
            f"{memory_usage:,.3f} / {total_memory:,.0f} MiB ({memory_percent:.0f}%)",
            True,
        ),
        ("Lines", f"{counter.code:,} lines", True),
        ("Comments", f"{counter.docs:,} lines", True),
        ("Blank", f"{counter.empty:,} lines", True),
        ("Database calls", f"{ctx.bot.db.calls:,} calls", True),
    ]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.respond(embed=embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)
    counter.count()


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
