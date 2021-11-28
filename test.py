import datetime
import logging
import traceback
import typing as t
from pathlib import Path

import hikari
import asyncpg

_BotT = t.TypeVar("_BotT", bound="Bot")

STDOUT_CHANNEL_ID = 806585593017532476
__version__ = "0.0.1a"


class Bot(hikari.GatewayBot):
    __slots__ = hikari.GatewayBot.__slots__ + (
        "client",
        "stdout_channel",
        "_token",
        "pool",
    )

    def __init__(self: _BotT) -> None:
        token = "ODIwMzM1MzAzMzg2NTk1Mzgx.YEzqyQ.2-n9iMnzEPGP12BF_BwHBR-ElhM"

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
        )

    def run(self: _BotT) -> None:

        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.MessageCreateEvent, self.on_message_created)

        super().run(
            activity=hikari.Activity(
                name=f"TESTING...",
                type=hikari.ActivityType.WATCHING,
            )
        )

    async def on_starting(self: _BotT, event: hikari.StartingEvent) -> None:
        self.pool = await asyncpg.create_pool(
            "postgresql://postgres:password123@localhost:8080/postgres"
        )
        logging.info("Connected to the database")

    async def on_started(self: _BotT, event: hikari.StartedEvent) -> None:
        self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        await self.stdout_channel.send(
            embed=hikari.Embed(
                title="Now online",
                description=f"Testing bot v{__version__} now online!",
            )
        )

        logging.info("Bot ready")

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS foo(
                    GuildID bigint
                );
                """
            )

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        # This is gonna be fixed.
        await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")

    async def on_message_created(self: _BotT, event: hikari.MessageCreateEvent) -> None:
        if event.content and event.content.startswith("!insert"):
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO foo(GuildID) VALUES($1)", event.message.guild_id
                )
                logging.info(
                    f"Entered {event.message.guild_id} into the guildID in the foo table"
                )

        if event.content and event.content.startswith("!check"):
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "SELECT * FROM foo WHERE GuildID = $1", event.message.guild_id
                )

                if (row := await conn.fetchone()) is not None:
                    print(row)


bot = Bot()
bot.run()
