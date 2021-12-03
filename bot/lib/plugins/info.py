import lightbulb
import hikari
import logging
import datetime

plugin = lightbulb.Plugin("info")


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

    embed.set_thumbnail(
        target.avatar_url if target.avatar_url else target.default_avatar_url
    )

    banner_url = (
        f"{str(user.banner_url).split('size=')[0]}size=70096"
        if user.banner_url
        else None
    )
    embed.set_image(user.banner_url if user.banner_url else user.accent_colour)
    print(banner_url)

    fields = [
        ("Bot?", target.is_bot, True),
        ("Created account on", f"<t:{created_at}:d> (<t:{created_at}:R>)", True),
        ("Joined server on", f"<t:{joined_at}:d> (<t:{joined_at}:R>)", True),
        ("Is pending?", target.is_pending, True),
        ("Voice muted?", "Yes" if target.is_mute else "No", True),
        ("Voice deafened?", "Yes" if target.is_deaf else "No", True),
        (
            "Roles",
            f", ".join(role.mention for role in roles),
            False,
        ),
    ]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.respond(embed=embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
