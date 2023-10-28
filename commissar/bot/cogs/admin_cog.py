import nextcord
import tenacity
from nextcord import Permissions, SlashOption
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.helpers import *
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import character_repo, Character, UserData
from commissar.core.data import user_data_repo
from commissar.core.esi.esi import ESI
from commissar import LOGGER


class AdminCog(commands.Cog):
    MIN_QUERY_LENGTH = 4

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot

    @nextcord.slash_command(
        name="members",
        dm_permission=False,
        default_member_permissions=Permissions(administrator=True)
    )
    async def members(self, interaction: nextcord.Interaction):
        pass

    @members.subcommand(
        name="register",
        description="Register server member",
        description_localizations={
            Locale.ru: "Зарегистрировать пользователя",
        }
    )
    async def members_register(
            self,
            interaction: nextcord.Interaction,
            member: nextcord.Member = SlashOption(
                description='Discord server member',
                description_localizations={
                    Locale.ru: "Пользователь на сервере"
                }
            ),
            character_id: int = SlashOption(
                description='EVE Online Character ID',
                description_localizations={
                    Locale.ru: "ID персонажа в EVE Online"
                }
            )
    ):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            # check character with ESI
            data = ESI().get_character(character_id)
            if data is None:
                raise BotException(get_localized(CHARACTER_NOT_FOUND, loc).format(character_id))
            u = user_data_repo.find(interaction.guild.id, member.id)
            if u is None:
                u = UserData(
                    discord_server_id=interaction.guild.id,
                    discord_user_id=member.id,
                    discord_user_name=member.name
                )
                user_data_repo.save(u)
            else:
                character_ids = [c.id for c in u.characters]
                if character_id in character_ids:
                    raise BotException(get_localized(CHARACTER_ALREADY_REGISTERED, loc).format(character_id))
            character_name = data['name']
            corporation_id = data['corporation_id']
            alliance_id = data['alliance_id'] if 'alliance_id' in data else None
            c = Character(
                discord_server_id=interaction.guild.id,
                user_data_id=u.id,
                character_id=character_id,
                character_name=data['name'],
                corporation_id=corporation_id,
                alliance_id=alliance_id
            )
            character_repo.save(c)
            messages.append(get_localized(CHARACTER_REGISTERED, loc).format(character_name, member.mention))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except (BaseException, tenacity.RetryError) as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @members.subcommand(
        name="info",
        description="Show member info",
        description_localizations={
            Locale.ru: "Показать информацию о пользователе",
        }
    )
    async def members_info(
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
                raise BotException(get_localized(GUILD_ONLY, loc))
            u = user_data_repo.find(interaction.guild.id, member.id)
            if u is None:
                raise BotException(get_localized(USER_NOT_REGISTERED, loc).format(member.mention))
            # except default permissions
            roles = [r.mention for r in interaction.user.roles if r.name != '@everyone']
            messages.append(get_localized(MEMBER_INFO, loc).format(member.mention, ", ".join(roles)))
            for c in u.characters:
                _link = ZKILLBOARD_CHARACTER_URL_PATTERN.format(c.character_id)
                messages.append("- [{}]({}) `ID: {}`".format(c.character_name, _link, c.character_id))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @members.subcommand(
        name="who",
        description="Perform search for registered characters using part of character name",
        description_localizations={
            Locale.ru: "Выполнить поиск зарегистрированных персонажей, используя часть имени персонажа",
        }
    )
    async def members_who(
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
                raise BotException(get_localized(QUERY_STRING_TOO_SHORT, loc).format(self.MIN_QUERY_LENGTH))
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            chars = character_repo.find_by_name(interaction.guild.id, character_name)
            if chars is None:
                raise BotException(get_localized(CHARACTER_NOT_FOUND, loc).format(character_name))
            messages.append(get_localized(CHARACTER_INFO_HEADER, loc))
            count = 0
            for c in chars:
                member = interaction.guild.get_member(c.user_data.discord_user_id)
                _link = ZKILLBOARD_CHARACTER_URL_PATTERN.format(c.character_id)
                messages.append("- [{}]({}) {}".format(c.character_name, _link, member.mention))
                count += 1
            if count == 0:
                raise BotException(get_localized(QUERY_CHARACTERS_NOT_FOUND, loc))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @nextcord.slash_command(
        name="stats",
        description="Show stats",
        description_localizations={
            Locale.ru: "Показать статистику",
        },
        dm_permission=False,
        default_member_permissions=Permissions(administrator=True)
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

    @stats.subcommand(
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

    @stats.subcommand(
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
                if member is not None:
                    roles = [r.mention for r in member.roles if r.name != '@everyone']
                    messages.append("- {} ({})".format(member.mention, ", ".join(roles)))
                    if u.characters is not None:
                        for c in u.characters:
                            messages.append("  - {} `ID: {}`".format(c.character_name, c.character_id))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))
