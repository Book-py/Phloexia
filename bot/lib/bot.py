import datetime
import json
import logging
import traceback
import typing as t
import uuid

import aiofiles
import hikari
import lightbulb
import motor

_BotT = t.TypeVar("_BotT", bound="Bot")

with open("bot/secrets/secrets.json", "r") as f:
    data = json.load(f)
    __version__ = data["__version__"]


class Bot(lightbulb.BotApp):
    __slots__ = lightbulb.BotApp.__slots__ + (
        "stdout_channel_id",
        "stdout_channel",
        "db",
        "bot_version",
    )

    def __init__(self: _BotT) -> _BotT:
        self.bot_version = __version__

        with open("bot/secrets/secrets.json", "r") as f:
            data = json.load(f)

            token = data["token"]
            self.db = motor.MotorClient(data["mongo_db_uri"])
            self.stdout_channel_id = data["stdout_channel_id"]

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
            prefix="t!",
            default_enabled_guilds=[
                806576437011677194,
                750331314204573756,
                701303404630376448,
                914433510343856158,
            ],
        )

        self.d.interactive_embeds = {}

    def run(self: _BotT) -> None:
        # Hikari events
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(
            hikari.GuildAvailableEvent, self.on_guild_available
        )
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.ExceptionEvent, self.on_exception)

        # Lightbulb events
        self.event_manager.subscribe(lightbulb.CommandErrorEvent, self.on_command_error)

        super().run(
            activity=hikari.Activity(
                name=f"Version {__version__}",
                type=hikari.ActivityType.WATCHING,
            )
        )

    async def on_starting(self: _BotT, event: hikari.StartingEvent) -> None:
        self.load_extensions_from(
            "bot/lib/plugins",
            must_exist=True,
        )

    async def on_started(self: _BotT, event: hikari.StartedEvent) -> None:
        self.stdout_channel = await self.rest.fetch_channel(self.stdout_channel_id)
        await self.stdout_channel.send(
            embed=hikari.Embed(
                title="Now online",
                description=f"Testing bot v{__version__} now online!",
            )
        )

        logging.info("Bot ready")

    async def on_guild_available(
        self: _BotT, event: hikari.GuildAvailableEvent
    ) -> None:
        self.d.interactive_embeds[event.guild_id] = {}

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        logging.info(f"Testing v{__version__} is shutting down.")

    async def on_exception(self: _BotT, event: hikari.ExceptionEvent) -> None:
        exception = event.exception

        error_id = str(uuid.uuid4())
        await self.rest.create_message(
            self.stdout_channel_id,
            f"A hikari error occurred and I have logged it with the id {error_id}",
        )
        raise exception

    async def on_command_error(self: _BotT, event: lightbulb.CommandErrorEvent) -> None:
        exception = event.exception.__cause__ or event.exception

        if isinstance(exception, lightbulb.CommandNotFound):
            pass
        elif isinstance(exception, lightbulb.NotEnoughArguments):
            await event.context.respond(
                "You need to pass more arguments for that command to work"
            )
        elif isinstance(
            exception,
            (
                lightbulb.ExtensionNotFound,
                lightbulb.ExtensionMissingLoad,
                lightbulb.ExtensionMissingUnload,
                lightbulb.ExtensionNotLoaded,
                lightbulb.ExtensionAlreadyLoaded,
            ),
        ):
            await event.context.respond(event.exception)
        else:
            error_id = str(uuid.uuid4())

            embed = hikari.Embed(
                title="An error has occurred",
                description="While processing that command and unknown error occurred. It has been logged, please report the error ID to the developers to get it sorted.",
                colour=0xFF0000,
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            )

            embed.add_field("Error type", "hikari-lightbulb", inline=True).add_field(
                "Error ID:", f"`{error_id}`", inline=True
            ).add_field("Basic error", f"```py\n{str(exception)}```", inline=False)

            await event.context.respond(embed=embed)

            async with aiofiles.open(f"errors/lightbulb/{error_id}.txt", "w") as file:
                partial_traceback: t.List[str] = traceback.format_exception(
                    *event.exc_info
                )
                full_traceback = "".join(line for line in partial_traceback)
                await file.write(full_traceback)
