import nextcord


async def bot_response(interaction: nextcord.Interaction, message: str, ephemeral=True):
    await interaction.response.send_message(message, ephemeral=ephemeral)


async def bot_response_multi(interaction: nextcord.Interaction, messages: list[str], ephemeral=True):
    text = "\n".join(messages)
    await interaction.response.send_message(text, ephemeral=ephemeral)