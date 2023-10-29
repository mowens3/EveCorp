import nextcord
import tenacity
from nextcord import Permissions, SlashOption
from nextcord.ext import commands

from commissar.bot import *
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import character_repo, Character, UserData, server_repo, Server
from commissar.core.data import user_data_repo
from commissar.core.esi.esi import ESI
from commissar import LOGGER


class AdminCog(commands.Cog):
    MIN_QUERY_LENGTH = 4

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot

    @nextcord.slash_command(
        name="setup",
        description="Setup server",
        description_localizations={
            Locale.ru: "Настройка сервера",
        },
        dm_permission=False,
        default_member_permissions=Permissions(administrator=True)
    )
    async def setup(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = SlashOption(
            description='Discord server channel for notifications',
            description_localizations={
                Locale.ru: "Канал на сервере Discord для уведомлений"
            }
        ),
        locale: str = SlashOption(
            description='Locale for channel notifications',
            description_localizations={
                Locale.ru: "Язык для уведомлений в канале"
            },
            choices={"en": "en_US", "ru": "ru"}
        )
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            _locale = Locale[locale].name
            server = server_repo.find_by_discord_server_id(interaction.guild.id)
            if server is not None:
                server.discord_channel_id = channel.id
                server.discord_channel_name = channel.name
                server.locale = locale
                server_repo.save(server)
                await bot_response(interaction, get_localized(SERVER_SETTINGS_UPDATED, loc))
            else:
                r = Server(
                    discord_server_id=interaction.guild.id,
                    discord_server_name=interaction.guild.name,
                    discord_channel_id=channel.id,
                    discord_channel_name=channel.name,
                    locale=_locale
                )
                server_repo.save(r)
                await bot_response(interaction, get_localized(SERVER_SETTINGS_CREATED, loc).format(
                        interaction.guild.name, channel.mention, _locale
                    )
                )
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

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

