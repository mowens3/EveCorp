import nextcord
from nextcord import Permissions, SlashOption
from nextcord.ext import commands

from commissar.bot.cogs.ui import RuleDropdownView
from commissar.bot import *
from commissar.bot.localizations import *
from commissar.bot.response import bot_response, bot_response_multi
from commissar.core.data import ServerRule, server_repo
from commissar.core.data import server_rule_repo
from commissar.core.esi.esi import ESI
from commissar import LOGGER


class RulesCog(commands.Cog, name="Rules"):

    def __init__(self, _bot: commands.Bot):
        self._bot = _bot
        self.guild_ids = [g.id for g in self._bot.guilds]

    @nextcord.slash_command(
        name="rules",
        dm_permission=False,
        default_member_permissions=Permissions(administrator=True)
    )
    async def rules(self, interaction: nextcord.Interaction):
        pass

    @rules.subcommand(
        name="add",
        description="Add rule for automated role grants on Discord server",
        description_localizations={
            Locale.ru: "Добавить правило автоматического назначения ролей на сервере Discord"
        }
    )
    async def rules_add(
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
            )
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            server = server_repo.find_by_discord_server_id(interaction.guild.id)
            if server is None:
                raise BotException(get_localized(SERVER_SETTINGS_NOT_FOUND, loc))
            # check corporation with ESI
            data = ESI().get_corporation(corporation_id)
            if data is None:
                raise BotException(get_localized(CORP_NOT_FOUND, loc).format(corporation_id))
            r = server_rule_repo.find_by_server_id_and_role_id(interaction.guild.id, role.id)
            if r is not None:
                if r.corporation_id == corporation_id:
                    raise BotException(get_localized(SERVER_RULE_EXISTS, loc))
                r.corporation_id = corporation_id,
                r.corporation_name = data['name'],
                r.corporation_ticker = data['ticker']
                server_rule_repo.save(r)
                await bot_response(interaction, get_localized(SERVER_RULE_UPDATED, loc))
            else:
                r = ServerRule(
                    discord_server_id=interaction.guild.id,
                    discord_role_id=role.id,
                    discord_role_name=role.name,
                    corporation_id=corporation_id,
                    corporation_name=data['name'],
                    corporation_ticker=data['ticker']
                )
                server_rule_repo.save(r)
                _link = ZKILLBOARD_CORPORATION_URL_PATTERN.format(r.corporation_id)
                await bot_response(interaction, get_localized(SERVER_RULE_CREATED, loc).format(
                        interaction.guild.name, role.mention, data['name'], data['ticker'], _link
                    )
                )
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @rules.subcommand(
        name="remove",
        description="Initiate rule removal dialog",
        description_localizations={
            Locale.ru: "Инициировать удаления правила"
        }
    )
    async def rules_remove(
            self,
            interaction: nextcord.Interaction
    ):
        loc = interaction.locale
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            server = server_repo.find_by_discord_server_id(interaction.guild.id)
            if server is None:
                raise BotException(get_localized(SERVER_SETTINGS_NOT_FOUND, loc))
            rules = server_rule_repo.find_by_discord_server_id(interaction.guild.id)
            if rules is None or len(rules) == 0:
                raise BotException(get_localized(SERVER_RULES_NOT_FOUND, loc).format(interaction.guild.name))
            await interaction.send(
                get_localized(SERVER_RULE_PICK, loc), view=RuleDropdownView(rules), ephemeral=True)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

    @rules.subcommand(
        name="show",
        description="Shows current rules for automated role grants",
        description_localizations={
            Locale.ru: "Выводит текущие правила автоматического назначения ролей",
        }
    )
    async def rules_show(self, interaction: nextcord.Interaction):
        loc = interaction.locale
        messages = []
        try:
            if interaction.guild is None:
                raise BotException(get_localized(GUILD_ONLY, loc))
            server = server_repo.find_by_discord_server_id(interaction.guild.id)
            if server is None:
                raise BotException(get_localized(SERVER_SETTINGS_NOT_FOUND, loc))
            rules = server_rule_repo.find_by_discord_server_id(interaction.guild.id)
            if rules is None or len(rules) == 0:
                raise BotException(get_localized(SERVER_RULES_NOT_FOUND, loc).format(interaction.guild.name))
            messages.append(get_localized(SERVER_RULES_INFO_HEADER, loc).format(interaction.guild.name))
            i = 1
            for r in rules:
                role = interaction.guild.get_role(r.discord_role_id)
                if role is None:
                    raise BotException(get_localized(ROLE_NOT_FOUND, loc).format(
                        r.discord_role_name, r.discord_role_id))
                _link = ZKILLBOARD_CORPORATION_URL_PATTERN.format(r.corporation_id)
                messages.append(get_localized(SERVER_RULES_INFO_ROW, loc).format(
                    i, role.mention, r.corporation_name, r.corporation_ticker, _link)
                )
                i += 1
            # send response with all messages
            await bot_response_multi(interaction, messages)
        except BotException as e:
            await bot_response(interaction, e.__str__())
        except BaseException as e:
            LOGGER.error(e, exc_info=True)
            await bot_response(interaction, get_localized(SOMETHING_WENT_WRONG, loc))

