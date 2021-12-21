import lightbulb
import logging

plugin = lightbulb.Plugin("owner")


@plugin.command
@lightbulb.command("plugin", "Manage the lightbulb plugins")
@lightbulb.implements(
    lightbulb.commands.PrefixCommandGroup, lightbulb.commands.SlashCommandGroup
)
async def manage_plugins(ctx: lightbulb.context.Context) -> None:
    pass


@manage_plugins.child
@lightbulb.option(
    "plugin",
    "The name of the plugin to reload (the bot.lib.plugins will automatically be added for you)",
)
@lightbulb.command("reload", "Reload the specified plugin")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def reload(ctx: lightbulb.context.Context) -> None:
    # if ctx.options.plugin == "owner":
    #     await ctx.respond("You can't reload this plugin")
    #     return

    ctx.bot.reload_extensions(f"bot.lib.plugins.{ctx.options.plugin}")
    await ctx.respond("Reloaded the plugin!")


@manage_plugins.child
@lightbulb.option(
    "plugin",
    "The name of the plugin to load (the bot.lib.plugins will automatically be added for you)",
)
@lightbulb.command("load", "Load the specified plugin")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def load(ctx: lightbulb.context.Context) -> None:
    if ctx.options.plugin == "owner":
        await ctx.respond("You can't reload this plugin")
        return

    ctx.bot.load_extensions(f"bot.lib.plugins.{ctx.options.plugin}")
    await ctx.respond("Loaded the plugin!")


@manage_plugins.child
@lightbulb.option(
    "plugin",
    "The name of the plugin to unload (the bot.lib.plugins will automatically be added for you)",
)
@lightbulb.command("unload", "Unload the specified plugin")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def reload(ctx: lightbulb.context.Context) -> None:
    if ctx.options.plugin == "owner":
        await ctx.respond("You can't reload this plugin")
        return

    ctx.bot.unload_extensions(f"bot.lib.plugins.{ctx.options.plugin}")
    await ctx.respond("Unloaded the plugin!")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
