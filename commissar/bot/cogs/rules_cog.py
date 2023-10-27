import nextcord
from nextcord import Permissions, SlashOption, Locale
from nextcord.ext import commands

from commissar.bot.exception import BotException
from commissar.bot.helpers import *
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import ServerRule
from commissar.core.data import server_rule_repo
from commissar.core.esi.esi import ESI
from commissar.core.log import LOGGER


class RulesCog(commands.Cog):

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot
        self.guild_ids = [g.id for g in self._bot.guilds]

    @commands.guild_only()
    @nextcord.slash_command(
        name="add_rule",
        description="Add rule for automated role grants on Discord server",
        description_localizations={
            Locale.ru: "Добавить правило автоматического назначения ролей на сервере Discord"
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def add_rule(
            self,
            interaction: nextcord.Interaction,
            corporation_id: int = SlashOption(
                description='EVE Online corporation ID for checks',
                description_localizations={
                    Locale.ru: "ID корпорации в EVE Online для проверок"
                }
            ),
            role: nextcord.Role = SlashOption(
                description='Discord server role',
                description_localizations={
                    Locale.ru: "Роль на сервере Discord "
                }
            ),
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
                default=Locale.en_US.name
            )
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            _locale = Locale[locale].name
            # check corporation with ESI
            data = ESI().get_corporation(corporation_id)
            if data is None:
                raise BotException(get_localized(CORP_NOT_FOUND, loc).format(corporation_id))
            r = server_rule_repo.find_by_server_id_and_role_id(interaction.guild.id, role.id)
            if r is not None:
                if r.corporation_id == corporation_id:
                    raise BotException(get_localized(RULE_EXISTS, loc))
                r.corporation_id = corporation_id,
                r.corporation_name = data['name'],
                r.corporation_ticker = data['ticker']
                server_rule_repo.save(r)
                await bot_response(interaction, get_localized(RULE_UPDATED, loc))
            else:
                r = ServerRule(
                    discord_server_id=interaction.guild.id,
                    discord_server_name=interaction.guild.name,
                    discord_role_id=role.id,
                    discord_role_name=role.name,
                    discord_channel_id=channel.id,
                    discord_channel_name=channel.name,
                    corporation_id=corporation_id,
                    corporation_name=data['name'],
                    corporation_ticker=data['ticker'],
                    locale=_locale
                )
                server_rule_repo.save(r)
                _link = ZKILLBOARD_CORPORATION_URL_PATTERN.format(r.corporation_id)
                await bot_response(
                    interaction,
                    get_localized(RULE_CREATED, loc).format(
                        interaction.guild.name, role.mention, data['name'], data['ticker'], _link,
                        channel.mention, _locale
                    )
                )
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="remove_rule",
        description="Remove rule",
        description_localizations={
            Locale.ru: "Удалить правило"
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def delete_rule(
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
                raise BotException(get_localized(GUILD_ONLY, loc))
            r = server_rule_repo.find_by_server_id_and_role_id(interaction.guild.id, role.id)
            if r is None:
                raise BotException(get_localized(RULE_NOT_EXISTS, loc))
            server_rule_repo.remove(r)
            await bot_response(interaction, get_localized(RULE_REMOVED, loc))
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @commands.guild_only()
    @nextcord.slash_command(
        name="get_rules",
        description="Prints current rules",
        description_localizations={
            Locale.ru: "Выводит текущие правила для сервера",
        },
        default_member_permissions=Permissions(administrator=True)
    )
    async def get_rules(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            rules = server_rule_repo.find_by_discord_server_id(interaction.guild.id)
            if rules is None or len(rules) == 0:
                raise BotException(get_localized(SERVER_RULES_NOT_FOUND, loc).format(interaction.guild.name))
            messages.append(get_localized(RULES_INFO_HEADER, loc).format(interaction.guild.name))
            i = 1
            for r in rules:
                role = interaction.guild.get_role(r.discord_role_id)
                if role is None:
                    raise BotException(get_localized(ROLE_NOT_FOUND, loc).format(
                        r.discord_role_name, r.discord_role_id))
                channel = interaction.guild.get_channel(r.discord_channel_id)
                if channel is None:
                    raise BotException(get_localized(CHANNEL_NOT_FOUND, loc).format(
                        r.discord_channel_name, r.discord_channel_name))
                _link = ZKILLBOARD_CORPORATION_URL_PATTERN.format(r.corporation_id)
                messages.append(get_localized(RULES_INFO_ROW, loc).format(
                    i, role.mention, r.corporation_name, r.corporation_ticker, _link, channel.mention, r.locale)
                )
                i += 1
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

