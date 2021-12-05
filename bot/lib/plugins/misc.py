import lightbulb
import logging

plugin = lightbulb.Plugin("misc")


@plugin.command
@lightbulb.command("test0", "Testing command 0")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def test0(ctx: lightbulb.context.Context) -> None:
    await ctx.respond("Testing...", reply=True, mentions_reply=True)


@plugin.command
@lightbulb.option("value", "The value to insert into the database")
@lightbulb.command("test1", "Testing command 1")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def test1(ctx: lightbulb.context.Context) -> None:
    await ctx.bot.db.execute(
        "INSERT INTO guilds(GuildID, TestValue) VALUES ($1, $2)",
        ctx.guild_id,
        ctx.options.value,
    )
    await ctx.respond("Done???")


@plugin.command
@lightbulb.command(
    "test2",
    "Testing command 2",
    ephemeral=False,
)
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def test2(ctx: lightbulb.context.Context) -> None:
    try:
        guilds, testvalues = await ctx.bot.db.fetch_rows(
            "SELECT * FROM guilds WHERE GuildID = $1", ctx.guild_id
        )
        await ctx.respond(f"The value for {guilds} is {testvalues}")
    except:
        await ctx.respond("No value set!")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
