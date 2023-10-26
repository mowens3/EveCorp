import nextcord
from nextcord import Permissions, SlashOption, Locale
from nextcord.ext import commands

from bot.exception import BotException
from bot.helpers import ZKILLBOARD_CORPORATION_URL_PATTERN, EMOJI_POSITIVE, EMOJI_NEGATIVE, \
    ZKILLBOARD_CHARACTER_URL_PATTERN
from bot.localizations import get_localized, GUILD_ONLY_LOC, CORP_NOT_FOUND_LOC, ROLE_ID_SET_LOC, \
    SOMETHING_WENT_WRONG_LOC, CURRENT_SETTINGS_LOC, ROLE_NOT_FOUND_LOC, SETTINGS_NOT_FOUND_LOC, MEMBER_INFO_LOC, \
    CHARACTER_NOT_FOUND_LOC, USER_NOT_REGISTERED_LOC, QUERY_STRING_TOO_SHORT_LOC, CHARACTER_INFO_LOC, \
    QUERY_CHARACTERS_NOT_FOUND_LOC, REPORT_INFO_LOC, CORP_ID_SET_LOC
from bot.response import bot_response, bot_response_multi
from core.data import server_settings
from core.data import character, user_data
from core.esi.esi import ESI
from core.log import LOGGER


class AdminCog(commands.Cog):
    MIN_QUERY_LENGTH = 4

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot
        self.guild_ids = [g.id for g in self._bot.guilds]

    @commands.guild_only()
    @nextcord.slash_command(
        name="set_corporation_id",
        description="Set linked EVE Online corporation ID",
        description_localizations={
            Locale.ru: "Указать ID связанной корпорации в EVE Online для Discord сервера"
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def set_corporation_id(
            self,
            interaction: nextcord.Interaction,
            corporation_id: int = SlashOption(
                description='EVE Online corporation ID',
                description_localizations={
                    Locale.ru: "ID корпорации в EVE Online"
                }
            )
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            ss = server_settings.find(interaction.guild.id)
            if ss is None:
                server_settings.create(interaction.guild.id, interaction.guild.name)
            # check corporation with ESI
            data = ESI().get_corporation(corporation_id)
            if data is None:
                raise BotException(get_localized(CORP_NOT_FOUND_LOC, loc).format(corporation_id))
            name = data['name']
            ticker = data['ticker']
            server_settings.update_corporation(interaction.guild.id, corporation_id, name, ticker)
            await bot_response(interaction, get_localized(CORP_ID_SET_LOC, loc).format(name, ticker))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="set_discord_role",
        description="Set linked Discord role",
        description_localizations={
            Locale.ru: "Указать связанную роль на сервере для Discord сервера",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def set_discord_role(
            self,
            interaction: nextcord.Interaction,
            role: nextcord.Role = SlashOption(
                description='Discord server role',
                description_localizations={
                    Locale.ru: "Роль на сервере Discord"
                }
            )
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            ss = server_settings.find(interaction.guild.id)
            if ss is None:
                server_settings.create(interaction.guild.id, interaction.guild.name)
            server_settings.update_role(interaction.guild.id, role.id, role.name)
            await bot_response(interaction, get_localized(ROLE_ID_SET_LOC, loc).format(role.mention))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="get_settings",
        description="Prints current settings",
        description_localizations={
            Locale.ru: "Выводит текущие настройки для сервера",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def get_settings(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            s = server_settings.find(interaction.guild.id)
            if s is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            role = interaction.guild.get_role(s.discord_role_id)
            if role is None:
                raise BotException(get_localized(ROLE_NOT_FOUND_LOC, loc))
            _link = ZKILLBOARD_CORPORATION_URL_PATTERN.format(s.corporation_id)
            await bot_response(interaction, get_localized(CURRENT_SETTINGS_LOC, loc).format(
                    interaction.guild.name, role.mention, s.corporation_name, s.corporation_ticker, _link))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="info",
        description="Show member info",
        description_localizations={
            Locale.ru: "Показать информацию о пользователе",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def info(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member = SlashOption(
                description='Discord server member',
                description_localizations={
                    Locale.ru: "Пользователь на сервере"
                }
            )
    ):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            u = user_data.find(interaction.guild.id, member.id)
            if u is None:
                raise BotException(get_localized(USER_NOT_REGISTERED_LOC, loc).format(member.name))
            roles = []
            for r in member.roles:
                # except default permissions
                if r.name != '@everyone':
                    roles.append(r.mention)
            messages.append(get_localized(MEMBER_INFO_LOC, loc).format(member.mention, ", ".join(roles)))
            for c in u.characters:
                # check character with ESI
                data = ESI().get_character(c.id)
                if data is None:
                    raise BotException(get_localized(CHARACTER_NOT_FOUND_LOC, loc).format(c.id))
                character_corp_id = data['corporation_id']
                mark = EMOJI_POSITIVE if character_corp_id == settings.corporation_id else EMOJI_NEGATIVE
                _link = ZKILLBOARD_CHARACTER_URL_PATTERN.format(c.id)
                messages.append("- [{}]({}) {}".format(c.name, _link, mark))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="who",
        description="Perform search for registered characters using part of character name",
        description_localizations={
            Locale.ru: "Выполнить поиск зарегистрированных персонажей, используя часть имени персонажа",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def who(
            self,
            interaction: nextcord.Interaction,
            character_name: str = SlashOption(
                description='Part of EVE Online character name',
                description_localizations={
                    Locale.ru: "Часть имени персонажа EVE Online"
                }
            )
    ):
        loc = interaction.locale
        messages = []
        try:
            if len(character_name) < self.MIN_QUERY_LENGTH:
                raise BotException(get_localized(QUERY_STRING_TOO_SHORT_LOC, loc).format(self.MIN_QUERY_LENGTH))
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            chars = character.find_by_name(interaction.guild.id, character_name)
            if chars is None:
                raise BotException(get_localized(CHARACTER_NOT_FOUND_LOC, loc).format(character_name))
            messages.append(get_localized(CHARACTER_INFO_LOC, loc))
            count = 0
            for c in chars:
                member = interaction.guild.get_member(c.user_data.discord_user_id)
                _link = ZKILLBOARD_CHARACTER_URL_PATTERN.format(c.id)
                messages.append("- [{}]({}) {}".format(c.name, _link, member.mention))
                count += 1
            if count == 0:
                raise BotException(get_localized(QUERY_CHARACTERS_NOT_FOUND_LOC, loc))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="stats",
        description="Show stats",
        description_localizations={
            Locale.ru: "Показать статистику",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def stats(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        # no bots
        total_users_count = sum(1 if not m.bot else 0 for m in interaction.guild.members)
        registered_users_count = 0
        characters_count = 0
        characters_in_corp = 0
        characters_not_in_corp = 0
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            users = user_data.find_all(interaction.guild.id)
            for u in users:
                for c in u.characters:
                    data = ESI().get_character(c.id)
                    if data is None:
                        raise BotException(get_localized(CHARACTER_NOT_FOUND_LOC, loc).format(c.id))
                    character_corp_id = data['corporation_id']
                    if character_corp_id == settings.corporation_id:
                        characters_in_corp += 1
                    else:
                        characters_not_in_corp += 1
                    characters_count += 1
                registered_users_count += 1
            await bot_response(interaction, get_localized(REPORT_INFO_LOC, loc).format(
                total_users_count, registered_users_count, characters_count, characters_in_corp, characters_not_in_corp
            ))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="report",
        description="Show short report",
        description_localizations={
            Locale.ru: "Показать краткий отчет",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def report(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            users = user_data.find_all(interaction.guild.id)
            for u in users:
                member = interaction.guild.get_member(u.discord_user_id)
                roles = []
                for r in member.roles:
                    # except default permissions
                    if r.name != '@everyone':
                        roles.append(r.mention)
                messages.append("{} ({})".format(member.mention, ", ".join(roles)))
                for c in u.characters:
                    data = ESI().get_character(c.id)
                    if data is None:
                        raise BotException(get_localized(CHARACTER_NOT_FOUND_LOC, loc).format(c.id))
                    character_corp_id = data['corporation_id']
                    mark = EMOJI_POSITIVE if character_corp_id == settings.corporation_id else EMOJI_NEGATIVE
                    messages.append("- {} {}".format(c.name, mark))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))
