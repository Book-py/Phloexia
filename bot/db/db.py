import asyncpg
from apscheduler.triggers.cron import CronTrigger
import typing as t

from asyncpg import pool


class Database:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.pool: asyncpg.Pool = None
        # bot.scheduler.add_job(self.commit, CronTrigger(second=0))
        self.calls = 0

    async def create_pool(self) -> None:
        self.pool = await asyncpg.create_pool(
            "postgresql://postgres:password123@localhost:8080/postgres"
        )

    async def execute(self, command: str, *values: t.Any) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(command, *values)
                self.calls += 1

    async def field(self, command: str, *values: t.Any | None) -> t.Any:
        async with self.pool.acquire() as conn:
            if (fetch := await conn.fetchval(command, *values)) is not None:
                return fetch

    async def row(self, command: str, *values: t.Any | None) -> t.Any:
        async with self.pool.acquire() as conn:
            if (fetch := await conn.fetchrow(command, *values)) is not None:
                return fetch

        return None

    async def fetch_rows(self, command: str, *values: t.Any | None) -> None:
        async with self.pool.acquire() as conn:
            if (fetch := await conn.fetch(command, *values)) is not None:
                return fetch
