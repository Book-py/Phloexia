import lightbulb
import hikari
import datetime
import asyncio

plugin = lightbulb.Plugin("fun")


embed_say_buttons = [
    {
        "name": "Message",
        "description": "The normal message to send along with the embed",
        "emoji": "🗣️",
        "custom_id": "message",
    },
    {
        "name": "Title",
        "description": "Set the title of the embed",
        "emoji": "🔈",
        "custom_id": "title",
    },
]


@plugin.command
@lightbulb.command("embed-say", "Interactively make an embed")
@lightbulb.implements(lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand)
async def embed_say(ctx: lightbulb.context.Context) -> None:
    ctx.bot.d.interactive_embeds = {}

    embed = hikari.Embed(
        title="Interactive embed creation",
        description="Click on the different buttons below to change something about the embed",
        colour=hikari.Colour(0x0000F0),
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    action_row = ctx.bot.rest.build_action_row()

    for button_info in embed_say_buttons:
        action_row.add_button(
            hikari.ButtonStyle.PRIMARY, button_info["custom_id"]
        ).set_label(button_info["name"]).set_emoji(
            button_info["emoji"]
        ).add_to_container()

    original_msg = await ctx.respond(embed=embed, component=action_row)

    while True:
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, timeout=60)
        except asyncio.TimeoutError:
            await original_msg.edit("You timed out!", components=[])
            break
        else:
            print(event.interaction.custom_id)

            if event.interaction.user.id == ctx.author.id:
                # if event.interaction.custom_id == "test button":
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    "Test button clicked",
                    flags=hikari.messages.MessageFlag.EPHEMERAL,
                )
                #     await ctx._maybe_defer()
                for button_info in embed_say_buttons:
                    if button_info["custom_id"] == event.interaction.custom_id:
                        pass
            else:
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    f"You can't use this embed creation session, only <@{ctx.author.id}> can!",
                    flags=64,
                )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
