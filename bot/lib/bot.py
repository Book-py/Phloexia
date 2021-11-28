import json
import hikari
import logging
import typing as t
import lightbulb

_BotT = t.TypeVar("_BotT", bound="Bot")
with open("bot/secrets/secrets.json", "r") as f:
    data = json.load(f)
    __version__ = data["__version__"]


class Bot(lightbulb.BotApp):
    __slots__ = lightbulb.BotApp.__slots__ + ("stdout_channel_id", "stdout_channel")

    def __init__(self: _BotT) -> _BotT:
        with open("bot/secrets/secrets.json", "r") as f:
            data = json.load(f)

            token = data["token"]
            self.stdout_channel_id = data["stdout_channel_id"]

        super().__init__(
            token=token,
            intents=hikari.Intents.ALL,
            prefix="t!",
            default_enabled_guilds=806576437011677194,
        )

    def run(self: _BotT) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)

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

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        logging.info(f"Testing v{__version__} is shutting down.")

        # Shutdown / disconnect anything needed here
