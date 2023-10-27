from commissar.core.esi.esi import ESI


def verify_single(character_id: int, corporation_id: int) -> bool:
    esi = ESI()
    data = esi.get_character(character_id)
    return corporation_id == data['corporation_id']


def verify_multiple(character_ids: list[int], corporation_id: int) -> bool:
    esi = ESI()
    count = 0
    for character_id in character_ids:
        data = esi.get_character(character_id)
        if corporation_id == data['corporation_id']:
            count += 1
    return count > 0


async def async_verify_single(character_id: int, corporation_id: int) -> bool:
    esi = ESI()
    data = await esi.async_get_character(character_id)
    return corporation_id == data['corporation_id']

