import nextcord
import tenacity
from nextcord import Permissions
from nextcord.ext import commands

from commissar.bot.cogs.ui import RegisterMessage, CharacterDropdownView
from commissar.bot import BotException
from commissar.bot import ZKILLBOARD_CHARACTER_URL_PATTERN
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import AuthAttempt, AUTH_ATTEMPT_TTL_MINUTES, server_repo
from commissar.core.data import auth_attempt_repo, user_data_repo
from commissar import LOGGER
from commissar.core.oauth.oauth_service import OAuthService


class PublicCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="character",
        dm_permission=False
    )
    async def character(self, interaction: nextcord.Interaction):
        pass

    @character.subcommand(
        name="register",
        description="Register your EVE Online character on Discord server with EVECommissar",
        description_localizations={
            Locale.ru: "Регистрация своего персонажа EVE Online на Discord сервере с помощью EVECommissar"
        }
    )
    async def register(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            server_repo.find_or_create(interaction.guild.id, interaction.guild.name)
            auth = OAuthService()
            info = auth.authorize()
            p = AuthAttempt(
                discord_server_id=interaction.guild.id,
                discord_user_id=interaction.user.id,
                discord_user_name=interaction.user.name,
                state=info.state,
                code_verifier=info.code_verifier,
                locale=interaction.locale.__str__()
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

    @character.subcommand(
        name="info",
        description="Show your registered characters",
        description_localizations={
            Locale.ru: "Показать информацию о своих зарегистрированных персонажах",
        }
    )
    async def info(self,interaction: nextcord.Interaction):
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

    @character.subcommand(
        name="remove",
        description="Initiate registered character removal",
        description_localizations={
            Locale.ru: "Инициировать удаление зарегистрированного персонажа",
        }
    )
    async def remove(
            self,
            interaction: nextcord.Interaction
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            u = user_data_repo.find(interaction.guild.id, interaction.user.id)
            if u is None:
                raise BotException(get_localized(USER_NOT_REGISTERED, loc).format(interaction.user.mention))
            else:
                if u.characters is None or len(u.characters) == 0:
                    await bot_response(interaction, get_localized(USER_CHARACTERS_NOT_FOUND, loc))
                await interaction.send(
                    get_localized(PICK_USER_CHARACTER, loc), view=CharacterDropdownView(u.characters), ephemeral=True)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except (BaseException, tenacity.RetryError) as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))
