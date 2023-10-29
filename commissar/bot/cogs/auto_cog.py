from datetime import datetime

import aiocron
import nextcord
from nextcord import Locale
from nextcord.ext import commands

from commissar.bot import APP_NAME
from commissar.bot.localizations import get_localized, ROLE_GRANTED, ROLE_REVOKED
from commissar.core.data import auth_attempt_repo, character_repo, user_data_repo, server_rule_repo
from commissar.core.esi.esi import ESI
from commissar import LOGGER, ConfigLoader

cfg = ConfigLoader().config
CRON_EXPIRE_AUTH = cfg['auto']['expire_auth']
CRON_GRANTS = cfg['auto']['grants']
CRON_UPDATES = cfg['auto']['updates']


class AutoCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        LOGGER.info("CRON_EXPIRE_AUTH: {}".format(CRON_EXPIRE_AUTH))
        LOGGER.info("CRON_GRANTS: {}".format(CRON_GRANTS))
        LOGGER.info("CRON_UPDATES: {}".format(CRON_UPDATES))
        cron_jobs = CronJobs(self)

    @staticmethod
    async def delete_expired_auth_attempts():
        start = datetime.now()
        deleted = auth_attempt_repo.remove_expired()
        LOGGER.info("Deleted auth records: {}".format(deleted))
        elapsed = datetime.now() - start
        LOGGER.info("Elapsed time: {}".format(elapsed))

    async def fetch_and_update_characters_data(self):
        start = datetime.now()
        characters = []
        count = 0
        # only connected servers
        for guild in self.bot.guilds:
            rules = server_rule_repo.find_by_discord_server_id(guild.id)
            # update character info only if there are at least one valid rule
            if rules is not None and len(rules) > 0:
                valid = 0
                for r in rules:
                    role = guild.get_role(r.discord_role_id)
                    if role is not None:
                        valid += 1
                if valid > 0:
                    server_characters = character_repo.find_by_discord_server_id(guild.id)
                    characters += server_characters
                else:
                    LOGGER.warn("No valid rules for server '{}'".format(guild.name))
        characters_ids = []
        characters_dict = {}
        for c in characters:
            characters_dict[c.character_id] = c
            characters_ids.append(c.character_id)
        results = await ESI().async_get_characters(characters_ids)
        for character_id, data in results:
            c = characters_dict[character_id]
            c.corporation_id = data['corporation_id']
            c.alliance_id = data['alliance_id'] if 'alliance_id' in data else None
            count += 1
        character_repo.save_multiple(characters)
        elapsed = datetime.now() - start
        LOGGER.info("Updated characters: {}".format(count))
        LOGGER.info("Elapsed time: {}".format(elapsed))

    @staticmethod
    async def grant(member: nextcord.Member, role: nextcord.Role, channel: nextcord.TextChannel,
                    locale: nextcord.Locale = Locale.en_US):
        result = False
        try:
            try:
                await member.add_roles(role, reason=APP_NAME)
                result = True
            except nextcord.errors.Forbidden:
                LOGGER.error("Failed to grant role '{}' to '{}' on server '{}'".format(
                    role.name, member.name, member.guild.name
                ))
                return False
            if channel is not None:
                await channel.send(get_localized(ROLE_GRANTED, locale).format(role.mention, member.mention))
            else:
                LOGGER.warn("Server channel for notification is None")
            LOGGER.info("Role '{}' has been granted to '{}' on server '{}'".format(
                role.name, member.name, member.guild.name))
        except Exception as e:
            LOGGER.error(e, exc_info=True)
        finally:
            return result

    @staticmethod
    async def revoke(member: nextcord.Member, role: nextcord.Role, channel: nextcord.TextChannel,
                     locale: nextcord.Locale = Locale.en_US):
        result = False
        try:
            try:
                await member.remove_roles(role, reason=APP_NAME)
                result = True
            except nextcord.errors.Forbidden:
                LOGGER.error("Failed to revoke role '{}' from '{}' on server '{}'".format(
                    role.name, member.name, member.guild.name
                ))
                return False
            if channel is not None:
                await channel.send(get_localized(ROLE_REVOKED, locale).format(role.mention, member.mention))
            else:
                LOGGER.warn("Server channel for notification is None")
            LOGGER.info("Role '{}' has been revoked from '{}' on server '{}'".format(
                role.name, member.name, member.guild.name))
        except Exception as e:
            LOGGER.error(e, exc_info=True)
        finally:
            return result

    async def grant_revoke_roles(self):
        start = datetime.now()
        # only connected servers
        for guild in self.bot.guilds:
            LOGGER.info(guild.name)
            rules = server_rule_repo.find_by_discord_server_id(guild.id)
            if rules is None or len(rules) == 0:
                LOGGER.debug('No rules')
                break
            grants = 0
            revokes = 0
            failed = 0
            for rule in rules:
                LOGGER.debug("Evaluating '{}' rule for role '{}'...".format(
                    rule.discord_server_name, rule.discord_role_name
                ))
                role = guild.get_role(rule.discord_role_id)
                # do nothing if role is invalid
                if role is None:
                    LOGGER.debug('No role')
                    break
                channel = guild.get_channel(rule.discord_channel_id)
                locale = Locale[rule.locale]
                for u in user_data_repo.find_by_server_id(guild.id):
                    member = guild.get_member(u.discord_user_id)
                    if member is None:
                        LOGGER.debug("No member '{}' (ID: {}).".format(u.discord_user_name, u.discord_user_id))
                        break
                    found = False
                    for c in u.characters:
                        LOGGER.info(c.character_name)
                        if c.corporation_id == rule.corporation_id:
                            found = True
                            break
                    if found:
                        LOGGER.debug('Found.')
                        if role not in member.roles:
                            result = await self.grant(member, role, channel, locale)
                            if result:
                                grants += 1
                            else:
                                failed += 1
                    else:
                        LOGGER.debug('Not found.')
                        if role in member.roles:
                            result = self.revoke(member, role, channel, locale)
                            if result:
                                revokes += 1
                            else:
                                failed += 1
            LOGGER.info("Server '{}': Grants: {}, Revokes: {}, Failed: {}".format(
                guild.name, grants, revokes, failed)
            )
        elapsed = datetime.now() - start
        LOGGER.info("Elapsed time: {}".format(elapsed))


class CronJobs:
    def __init__(self, auto_cog: AutoCog) -> None:

        @aiocron.crontab(CRON_EXPIRE_AUTH, start=False)
        async def expire_auth_task():
            try:
                await auto_cog.delete_expired_auth_attempts()
            except Exception as e:
                LOGGER.error(e, exc_info=True)

        @aiocron.crontab(CRON_UPDATES, start=False)
        async def updates_task():
            try:
                await auto_cog.fetch_and_update_characters_data()
            except Exception as e:
                LOGGER.error(e, exc_info=True)

        @aiocron.crontab(CRON_GRANTS, start=False)
        async def grants_task():
            try:
                await auto_cog.grant_revoke_roles()
            except Exception as e:
                LOGGER.error(e, exc_info=True)

