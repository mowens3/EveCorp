import asyncio

from nextcord.ext import commands, tasks

from commissar_core.data import auth_attempt, user_data, server_settings
from commissar_core.esi.esi import ESI
from commissar_core.log import LOGGER


class AutoCog(commands.Cog):
    DEFAULT_INTERVAL = 60

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checks.start()

    def cog_unload(self):
        self.checks.cancel()

    @tasks.loop(seconds=DEFAULT_INTERVAL)
    async def checks(self):
        try:
            await self.delete_expired_auth_attempts()
            await self.check_characters()
        except Exception as e:
            LOGGER.error(e, exc_info=True)

    @checks.before_loop
    async def before_start(self):
        LOGGER.info("Waiting until ready...")
        await self.bot.wait_until_ready()

    @staticmethod
    async def delete_expired_auth_attempts():
        expired = auth_attempt.find_expired()
        for a in expired:
            LOGGER.info("{}".format(a))
        deleted = auth_attempt.remove_expired()
        LOGGER.info("deleted: {}".format(deleted))

    @staticmethod
    async def check_characters():
        servers = server_settings.find_all()
        for s in servers:
            LOGGER.info(s)
            users = user_data.find_all(s.discord_server_id)
            for u in users:
                LOGGER.info(u)
                characters_ids = [c.id for c in u.characters]
                LOGGER.info(characters_ids)
                results = await ESI().async_get_characters_corp(characters_ids)
                for r in results:
                    LOGGER.info(r[0], r[1])

