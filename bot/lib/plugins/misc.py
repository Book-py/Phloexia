import lightbulb

plugin = lightbulb.Plugin("misc")


@plugin.command
@lightbulb.command("test0", "Testing command 0")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def test0(ctx: lightbulb.context.Context) -> None:
    await ctx.respond("Testing...", reply=True, mentions_reply=True)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
