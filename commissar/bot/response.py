import nextcord


async def bot_response(interaction: nextcord.Interaction, message: str, ephemeral=True):
    await interaction.response.send_message(message, ephemeral=ephemeral)


async def bot_response_multi(interaction: nextcord.Interaction, messages: list[str], ephemeral=True):
    current = 0
    limit = 2000
    buffer = ""
    chunks = []
    for message in messages:
        new = current + len(message)
        if new < limit:
            buffer += message
            current = new
        else:
            chunks.append(buffer)
            buffer = message
            current = len(message)
    chunks.append(buffer)
    for chunk in chunks:
        await interaction.send(chunk, ephemeral=ephemeral)

