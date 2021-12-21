import lightbulb
import hikari
import datetime
import asyncio
from lightbulb.ext import neon

plugin = lightbulb.Plugin("fun")


class ButtonsMenu(neon.ComponentMenu):
    @neon.button("Message", "message", hikari.ButtonStyle.PRIMARY, emoji="🗣️")
    async def message(self) -> None:
        await self.edit_msg(
            "Send the message you want to be sent along with the embed", components=[]
        )

        try:
            msg_event = await self.context.bot.wait_for(
                hikari.GuildMessageCreateEvent, 2
            )
        except asyncio.TimeoutError:
            msg = await self.context.bot.rest.create_message(
                self.context.channel_id,
                content="You timedout!",
                # flags=hikari.MessageFlag.EPHEMERAL,
            )

            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
        else:
            self.context.bot.d.interactive_embeds[self.context.guild_id][
                "message"
            ] = msg_event.message.content

            msg = await self.context.bot.rest.create_message(
                self.context.channel_id,
                content="Successfully updated the message",
                # flags=hikari.MessageFlag.EPHEMERAL,
            )

            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass

        finally:
            await self.edit_msg(embeds=self.msg.embeds, components=self.build())

    @neon.button("test", "test", hikari.ButtonStyle.PRIMARY)
    async def test_button(self) -> None:
        ...


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
    ctx.bot.d.interactive_embeds[ctx.guild_id] = {}

    embed = hikari.Embed(
        title="Interactive embed creation",
        description="Click on the different buttons below to change something about the embed",
        colour=hikari.Colour(0x0000F0),
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    # action_row = ctx.bot.rest.build_action_row()

    # for button_info in embed_say_buttons:
    #     action_row.add_button(
    #         hikari.ButtonStyle.PRIMARY, button_info["custom_id"]
    #     ).set_label(button_info["name"]).set_emoji(
    #         button_info["emoji"]
    #     ).add_to_container()

    my_menu = ButtonsMenu(ctx)
    original_msg = await ctx.respond(embed=embed, components=my_menu.build())
    await my_menu.run(original_msg)

    # while True:
    #     try:
    #         event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, timeout=60)
    #     except asyncio.TimeoutError:
    #         await original_msg.edit("You timed out!", components=[])
    #         break
    #     else:
    #         print(event.interaction.custom_id)

    #         if event.interaction.user.id == ctx.author.id:
    #             # if event.interaction.custom_id == "test button":
    #             await event.interaction.create_initial_response(
    #                 hikari.ResponseType.MESSAGE_CREATE,
    #                 "Test button clicked",
    #                 flags=hikari.messages.MessageFlag.EPHEMERAL,
    #             )
    #             #     await ctx._maybe_defer()
    #             for button_info in embed_say_buttons:
    #                 if button_info["custom_id"] == event.interaction.custom_id:
    #                     pass
    #         else:
    #             await event.interaction.create_initial_response(
    #                 hikari.ResponseType.MESSAGE_CREATE,
    #                 f"You can't use this embed creation session, only <@{ctx.author.id}> can!",
    #                 flags=64,
    #             )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
