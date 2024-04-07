import nextcord
import os
from nextcord.ext import commands

from commissar.bot.cogs.admin_cog import AdminCog
from commissar.bot.cogs.auto_cog import AutoCog
from commissar.bot.cogs.public_cog import PublicCog
from commissar.bot.cogs.reports_cog import ReportsCog
from commissar.bot.cogs.rules_cog import RulesCog
from commissar import SingletonMeta
from commissar import ConfigLoader
from commissar import LOGGER


class CommissarBot(commands.Bot, metaclass=SingletonMeta):
    def __init__(self):
        # fairly important stuff
        intents = nextcord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix='!')
        self.add_cog(AdminCog(self))
        self.add_cog(RulesCog(self))
        self.add_cog(PublicCog(self))
        self.add_cog(ReportsCog(self))
        self.add_cog(AutoCog(self))

    async def setup_hook(self) -> None:
        pass

    async def on_ready(self):
        LOGGER.info(f'Logged in as {self.user} (ID: {self.user.id})')
        LOGGER.info("Connected servers:")
        i = 1
        for g in self.guilds:
            LOGGER.info(f"{i}: {g.name} (Server ID: {g.id})")
            await self.sync_application_commands(guild_id=g.id)
            i += 1


def start() -> None:
    cfg = ConfigLoader().config
    token = os.environ["discord_token"]
    bot = CommissarBot()
    bot.run(token)
