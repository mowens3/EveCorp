import nextcord
import tenacity
from nextcord import SlashOption, Permissions
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core import AuthAttempt, UserData, Character, AUTH_ATTEMPT_TTL_MINUTES
from commissar.core.data import auth_attempt, server_settings
from commissar.core.data import character, user_data
from commissar.core.esi.esi import ESI
from commissar.core.log import LOGGER
from commissar.core.oauth.oauth_service import OAuthService


class RegisterMessage(nextcord.ui.View):
    LABEL = 'LOG IN with EVE Online'

    def __init__(self, url: str):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=RegisterMessage.LABEL, url=url))


class RegisterCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_ids = [g.id for g in self.bot.guilds]

    @commands.guild_only()
    @nextcord.slash_command(
        name="register",
        description="Register self on Discord server",
        description_localizations={
            Locale.ru: "Регистрация себя на Discord сервере",
        })
    async def register_self(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            if not server_settings.check(settings):
                raise BotException(get_localized(INVALID_SETTINGS_LOC, loc))
            auth = OAuthService()
            info = auth.authorize()
            p = AuthAttempt(
                discord_server_id=interaction.guild.id,
                discord_user_id=interaction.user.id,
                discord_user_name=interaction.user.name,
                discord_interaction_id=interaction.id,
                state=info.state,
                code_verifier=info.code_verifier
            )
            auth_attempt.save(p)
            # send direct message with link
            await interaction.user.send(get_localized(REGISTER_LINK_LOC, loc).format(
                interaction.user.name, interaction.guild.name, APP_NAME, AUTH_ATTEMPT_TTL_MINUTES
            ), view=RegisterMessage(info.location_url))
            # send response to command
            await bot_response(interaction, get_localized(REGISTER_LINK_SENT_LOC, loc).format(interaction.user.mention))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="register_member",
        description="Register server member",
        description_localizations={
            Locale.ru: "Зарегистрировать пользователя",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def register_member(
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
                raise BotException(get_localized(GUILD_ONLY_LOC, loc))
            settings = server_settings.find(interaction.guild.id)
            if settings is None:
                raise BotException(get_localized(SETTINGS_NOT_FOUND_LOC, loc).format(interaction.guild.name))
            LOGGER.info("Settings found.")
            if not server_settings.check(settings):
                raise BotException(get_localized(INVALID_SETTINGS_LOC, loc))
            # check character with ESI
            data = ESI().get_character(character_id)
            if data is None:
                raise BotException(get_localized(CHARACTER_NOT_FOUND_LOC, loc).format(character_id))
            LOGGER.info("Character found.")
            character_name = data['name']
            character_corporation_id = data['corporation_id']
            if character_corporation_id != settings.corporation_id:
                raise BotException(get_localized(CHARACTER_NOT_IN_CORP_LOC, loc))
            LOGGER.info("Character in linked corp.")
            u = user_data.find(interaction.guild.id, member.id)
            if u is None:
                LOGGER.info("User not yet registered.")
                u = UserData(
                    discord_server_id=interaction.guild.id,
                    discord_user_id=member.id,
                    discord_user_name=member.name
                )
                user_data.save(u)
            else:
                LOGGER.info("User already registered.")
                character_ids = [c.id for c in u.characters]
                if character_id in character_ids:
                    LOGGER.info("Character already linked.")
                    raise BotException(get_localized(CHARACTER_ALREADY_REGISTERED_LOC, loc).format(character_id))
            c = Character(
                id=character_id, name=character_name,  discord_server_id=interaction.guild.id, user_data_id=u.id
            )
            character.save(c)
            LOGGER.info("Character linked.")
            messages.append(get_localized(CHARACTER_LINKED_LOC, loc).format(character_name, member.mention))
            role = interaction.guild.get_role(settings.discord_role_id)
            if role not in member.roles:
                LOGGER.info("Role not yet granted.")
                await member.add_roles(role, reason=APP_NAME)
                messages.append(get_localized(ROLE_GRANTED_LOC, loc).format(role.mention))
            else:
                LOGGER.info("Role already granted.")
                messages.append(get_localized(ROLE_ALREADY_GRANTED_LOC, loc).format(role.mention))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except (BaseException, tenacity.RetryError) as e:
            LOGGER.error(e)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG_LOC, loc))
