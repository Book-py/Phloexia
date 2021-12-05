import json
import hikari
import logging
import typing as t
import lightbulb
from bot.db import Database
import uuid
import aiofiles
import traceback

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
        self.db = Database(self)
        self.bot_version = __version__

        with open("bot/secrets/secrets.json", "r") as f:
            data = json.load(f)

            token = data["token"]
            self.stdout_channel_id = data["stdout_channel_id"]

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
            prefix="t!",
            default_enabled_guilds=[
                806576437011677194,
                750331314204573756,
                701303404630376448,
            ],
        )

    def run(self: _BotT) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.ExceptionEvent, self.on_exception)
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
        await self.db.create_pool()
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS guilds (
                GuildID bigint NOT NULL,
                TestValue text
            )"""
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

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        logging.info(f"Testing v{__version__} is shutting down.")

        # Shutdown / disconnect anything needed here

    async def on_exception(self: _BotT, event: hikari.ExceptionEvent) -> None:
        exception = event.exception

        error_id = str(uuid.uuid4())
        # await event.context.respond(
        # f"Your error ID is `{error_id}` and the error type is `hikari`"
        # )
        raise exception

    async def on_command_error(self: _BotT, event: lightbulb.CommandErrorEvent) -> None:
        exception = event.exception.__cause__ or event.exception

        # if isinstance(exception, lightbulb.NotEnoughArguments):
        #     await event.context.respond(
        #         "You need to pass more arguments for that command to work"
        #     )
        # else:
        error_id = str(uuid.uuid4())
        await event.context.respond(
            f"Your error has been logged!/nPlease report the following to the developers:\nID: `{error_id}`\nError type: `lightbulb`"
        )

        async with aiofiles.open(f"errors/lightbulb/{error_id}.txt", "w") as file:
            partial_traceback: t.List[str] = traceback.format_exception(*event.exc_info)
            full_traceback = "".join(line for line in partial_traceback)
            await file.write(full_traceback)

        raise exception
