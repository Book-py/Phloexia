import lightbulb
import logging

plugin = lightbulb.Plugin("misc")


@plugin.command
@lightbulb.command("test", "Testing command")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def ping(ctx: lightbulb.context.Context) -> None:
    await ctx.respond("Testing...", reply=True, mentions_reply=True)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)
    logging.info(f"--- Loaded the plugin named {plugin.name} ---")


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
