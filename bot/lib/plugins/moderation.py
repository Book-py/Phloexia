import lightbulb

plugin = lightbulb.Plugin("moderation")

@plugin.command
@lightbulb.command("kick", "Kick's a user")
@lightbulb.implements(
    lightbulb.commands.SlashCommand,
    lightbulb.commands.MessageCommand
)
async def kick(ctx: lightbulb.context.Context) -> None:
    ...

@plugin.command
@lightbulb.command("ban", "Ban's a user")
@lightbulb.implements(
    lightbulb.commands.SlashCommand,
    lightbulb.commands.MessageCommand
)
async def ban(ctx: lightbulb.context.Context) -> None:
    ...

@plugin.command
@lightbulb.command("mute", "Mute's a user")
@lightbulb.implements(
    lightbulb.commands.SlashCommand,
    lightbulb.commands.MessageCommand
)
async def mute(ctx: lightbulb.context.Context) -> None:
    ...

@plugin.command
@lightbulb.command("unban", "Unban's a user")
@lightbulb.implements(
    lightbulb.commands.SlashCommand,
    lightbulb.commands.MessageCommand
)
async def unban(ctx: lightbulb.context.Context) -> None:
    ...


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)

