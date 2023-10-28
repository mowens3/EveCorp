import nextcord
from nextcord import Permissions
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import user_data_repo
from commissar import LOGGER


class ReportsCog(commands.Cog):
    MIN_QUERY_LENGTH = 4

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot

    @nextcord.slash_command(
        name="reports",
        dm_permission=False,
        default_member_permissions=Permissions(administrator=True)
    )
    async def reports(self, interaction: nextcord.Interaction):
        pass

    @reports.subcommand(
        name="stats",
        description="Show users and characters registration stats",
        description_localizations={
            Locale.ru: "Показать статистику регистрации пользователей и персонажей",
        }
    )
    async def stats(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        # no bots
        total_users_count = sum(1 if not m.bot else 0 for m in interaction.guild.members)
        registered_users_count = 0
        characters_count = 0
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            users = user_data_repo.find_by_server_id(interaction.guild.id)
            for u in users:
                characters_count += len(u.characters)
                registered_users_count += 1
            unregistered_users_count = total_users_count - registered_users_count
            await bot_response(interaction, get_localized(REPORT_INFO, loc).format(
                total_users_count, registered_users_count, unregistered_users_count, characters_count
            ))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @reports.subcommand(
        name="unregistered",
        description="Show unregistered users",
        description_localizations={
            Locale.ru: "Показать незарегистрированных пользователей",
        }
    )
    async def unregistered(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            users = user_data_repo.find_by_server_id(interaction.guild.id)
            registered_user_ids = [u.discord_user_id for u in users]
            messages.append(get_localized(UNREGISTERED_USERS_HEADER, loc))
            unregistered = [m for m in interaction.guild.members if not m.bot and m.id not in registered_user_ids]
            for m in unregistered:
                messages.append("- {}".format(m.mention))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @reports.subcommand(
        name="registered",
        description="Show registered users",
        description_localizations={
            Locale.ru: "Показать зарегистрированных пользователей",
        }
    )
    async def registered(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            users = user_data_repo.find_by_server_id(interaction.guild.id)
            if len(users) == 0:
                raise BotException(get_localized(NO_REGISTERED_USERS, loc))
            messages.append(get_localized(REGISTERED_USERS_HEADER, loc))
            for u in users:
                member = interaction.guild.get_member(u.discord_user_id)
                roles = []
                for r in member.roles:
                    # except default permissions
                    if r.name != '@everyone':
                        roles.append(r.mention)
                messages.append("- {} ({})".format(member.mention, ", ".join(roles)))
                for c in u.characters:
                    messages.append("  - {} `ID: {}`".format(c.character_name, c.character_id))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))
