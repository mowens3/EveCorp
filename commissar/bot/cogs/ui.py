import nextcord
from nextcord import ButtonStyle

from commissar.bot.localizations import get_localized, USER_CHARACTER_REMOVED, SOMETHING_WENT_WRONG, RULE_REMOVED
from commissar.core.data import character_repo, Character, ServerRule, server_rule_repo
from commissar import LOGGER


class RegisterMessage(nextcord.ui.View):
    LABEL = 'LOG IN with EVE Online'

    def __init__(self, url: str):
        super().__init__()
        self.add_item(nextcord.ui.Button(label=RegisterMessage.LABEL, url=url, style=ButtonStyle.link))


class CharacterDropdown(nextcord.ui.Select):

    def __init__(self, characters: list[Character]):
        options = [nextcord.SelectOption(label=c.character_name, value=c.character_id) for c in characters]
        self.selected = None
        super().__init__(placeholder="", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        self.selected = int(self.values[0])


class CharacterDropdownView(nextcord.ui.View):
    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green, emoji='✅', row=2)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            character_id = self.dropdown.selected
            c = character_repo.find_by_character_id(character_id)
            loc = interaction.locale
            character_repo.remove(c)
            await interaction.response.send_message(get_localized(USER_CHARACTER_REMOVED, loc).format(
                c.character_name, interaction.user.mention), ephemeral=True)
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            await interaction.response.send_message(get_localized(SOMETHING_WENT_WRONG, loc), ephemeral=True)
        finally:
            self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.grey, emoji='❌', row=2)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    def __init__(self, characters: list[Character]):
        super().__init__()
        self.dropdown = CharacterDropdown(characters)
        self.add_item(self.dropdown)


class RuleDropdown(nextcord.ui.Select):

    def __init__(self, rules: list[ServerRule]):
        options = [
            nextcord.SelectOption(label='@' + r.discord_role_name, value=r.id) for r in rules
        ]
        self.selected = None
        super().__init__(placeholder="", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        self.selected = int(self.values[0])


class RuleDropdownView(nextcord.ui.View):
    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green, emoji='✅', row=2)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        loc = interaction.locale
        try:
            rule_id = self.dropdown.selected
            r = server_rule_repo.find_by_id(rule_id)
            server_rule_repo.remove(r)
            await interaction.response.send_message(get_localized(RULE_REMOVED, loc), ephemeral=True)
        except Exception as e:
            LOGGER.error(e, exc_info=True)
            await interaction.response.send_message(get_localized(SOMETHING_WENT_WRONG, loc), ephemeral=True)
        finally:
            self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.grey, emoji='❌', row=2)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.stop()

    def __init__(self, rules: list[ServerRule]):
        super().__init__()
        self.dropdown = RuleDropdown(rules)
        self.add_item(self.dropdown)

