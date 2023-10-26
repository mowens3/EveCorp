from nextcord import Locale
from nextcord.ext import commands

from bot.bot import APP_NAME, get_localized, ROLE_GRANTED_LOC, ROLE_ALREADY_GRANTED_LOC


async def bot_grant(
        _bot: commands.Bot,
        discord_server_id: int,
        discord_user_id: int,
        discord_role_id: int,
        locale: Locale = Locale.en_US,
):
    """
    :param _bot:
    :param discord_server_id:
    :param discord_user_id:
    :param discord_role_id:
    :param locale:
    :return:
    """
    # _bot.get_interaction()
    server = _bot.get_guild(discord_server_id)
    member = server.get_member(discord_user_id)
    role = server.get_role(discord_role_id)
    if role not in member.roles:
        # LOGGER.info("Assigning role {}".format(role.name))
        await member.add_roles(role, reason=APP_NAME)
        await member.send(get_localized(ROLE_GRANTED_LOC, locale).format(role.name, member.name))
    else:
        # LOGGER.info("Role already assigned")
        await member.send(get_localized(ROLE_ALREADY_GRANTED_LOC, locale))
