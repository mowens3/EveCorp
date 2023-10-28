import nextcord
from nextcord import Permissions, Locale
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.localizations import get_localized, HELP_ADMIN, SOMETHING_WENT_WRONG
from commissar.bot.response import bot_response
from commissar.core.log import LOGGER


class HelpCog(commands.Cog, name="Help"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="help",
        description="Shows help",
        description_localizations={
            Locale.ru: "Отображает помощь",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def help(self, interaction: nextcord.Interaction):
        pass

    @help.subcommand(
        name="user",
        description="Shows User Guide",
        description_localizations={
            Locale.ru: "Отображает Руководство пользователя",
        }
    )
    async def help_user(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            await bot_response(interaction, get_localized(HELP_ADMIN, loc))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @help.subcommand(
        name="admin",
        description="Shows Admin Guide",
        description_localizations={
            Locale.ru: "Отображает Руководство администратора",
        },
    )
    async def help_admin(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            await bot_response(interaction, get_localized(HELP_ADMIN, loc))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

