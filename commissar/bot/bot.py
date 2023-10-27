import nextcord
from nextcord.ext import commands

from commissar.bot.cogs.admin_cog import AdminCog
from commissar.bot.cogs.auto_cog import AutoCog
from commissar.bot.cogs.public_cog import PublicCog
from commissar.bot.cogs.rules_cog import RulesCog
from commissar.core import SingletonMeta
from commissar.core.config import ConfigLoader
from commissar.core.log import LOGGER


class CommissarBot(commands.Bot, metaclass=SingletonMeta):
    def __init__(self, *args, **kwargs):
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix='$', intents=intents)
        self.add_cog(AdminCog(self))
        self.add_cog(RulesCog(self))
        self.add_cog(PublicCog(self))
        self.add_cog(AutoCog(self))
        self.guild_ids = None

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
        self.guild_ids = [g.id for g in self.guilds]


def start() -> None:
    cfg = ConfigLoader().config
    token = cfg['discord']['token']
    bot = CommissarBot()
    bot.run(token)
