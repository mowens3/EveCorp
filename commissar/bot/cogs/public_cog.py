import nextcord
import tenacity
from nextcord import SlashOption, Permissions, ButtonStyle
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.helpers import ZKILLBOARD_CHARACTER_URL_PATTERN
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import AuthAttempt, AUTH_ATTEMPT_TTL_MINUTES, character_repo
from commissar.core.data import auth_attempt_repo, user_data_repo
from commissar.core.esi.esi import ESI
from commissar.core.log import LOGGER
from commissar.core.oauth.oauth_service import OAuthService


class RegisterMessage(nextcord.ui.View):
    LABEL = 'LOG IN with EVE Online'

    def __init__(self, url: str):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=RegisterMessage.LABEL, url=url, style=ButtonStyle.link))


class PublicCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @nextcord.slash_command(
        name="register",
        description="Register EVE Online character on Discord server with EVECommissar",
        description_localizations={
            Locale.ru: "Регистрация персонажа EVE Online на Discord сервере с помощью EVECommissar",
        })
    async def register(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
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
            auth_attempt_repo.save(p)
            # send direct message with link
            await interaction.user.send(get_localized(REGISTER_LINK_TEXT, loc).format(
                interaction.user.name, interaction.guild.name, auth.HOST, auth.callback_host, AUTH_ATTEMPT_TTL_MINUTES
            ), view=RegisterMessage(info.location_url))
            # send response to command
            await bot_response(interaction, get_localized(REGISTER_LINK_SENT, loc).format(interaction.user.mention))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="info",
        description="Show info",
        description_localizations={
            Locale.ru: "Показать информацию о пользователе",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def info(
            self,
            interaction: nextcord.Interaction
    ):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            u = user_data_repo.find(interaction.guild.id, interaction.user.id)
            if u is None:
                raise BotException(get_localized(USER_NOT_REGISTERED, loc).format(interaction.user.mention))
            # except default permissions
            roles = [r.mention for r in interaction.user.roles if r.name != '@everyone']
            messages.append(get_localized(MEMBER_INFO, loc).format(interaction.user.mention, ", ".join(roles)))
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

    @commands.guild_only()
    @nextcord.slash_command(
        name="remove_character",
        description="Remove registered character",
        description_localizations={
            Locale.ru: "Удалить зарегистрированного персонажа",
        }
    )
    async def remove_character(
            self,
            interaction: nextcord.Interaction,
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
            u = user_data_repo.find(interaction.guild.id, interaction.user.id)
            if u is None:
                raise BotException(get_localized(USER_NOT_REGISTERED, loc).format(interaction.user.mention))
            else:
                character_ids = [c.id for c in u.characters]
                if character_id not in character_ids:
                    raise BotException(get_localized(USER_CHARACTER_NOT_FOUND, loc).format(
                        character_id, interaction.user.mention))
                c = character_repo.find(character_id)
                character_repo.remove(c)
                messages.append(get_localized(USER_CHARACTER_REMOVED, loc).format(
                    c.character_name, interaction.user.mention))
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except (BaseException, tenacity.RetryError) as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))
