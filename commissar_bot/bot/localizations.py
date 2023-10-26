from nextcord import Locale


def get_localized(a: dict, locale: str):
    return a[locale] if locale in [Locale.ru] else a[Locale.en_US.__str__()]


def get_localized_f(a: dict, locale: str, *args):
    return a[locale].format(args) if locale in [Locale.ru] else a[Locale.en_US.__str__()]


"""Generic messages
"""

SOMETHING_WENT_WRONG_LOC = {
    Locale.en_US.__str__(): "Something went wrong",
    Locale.ru.__str__(): "Что-то пошло не так"
}

GUILD_ONLY_LOC = {
    Locale.en_US.__str__(): "This command should me executed on server channel.",
    Locale.ru.__str__(): "Эта команда должна выполняться только на канале сервера."
}

"""Settings related messages
"""

SETTINGS_NOT_FOUND_LOC = {
    Locale.en_US.__str__(): "Settings for ***{}*** not found.",
    Locale.ru.__str__(): "Настройки для ***{}*** не найдены."
}

INVALID_SETTINGS_LOC = {
    Locale.en_US.__str__(): "Bot hasn't been configured properly.",
    Locale.ru.__str__(): "Бот не настроен корректно."
}

CURRENT_SETTINGS_LOC = {
    Locale.en_US.__str__(): "Current settings for ***{}***:\n"
                            "* Linked server role: {}\n"
                            "* Linked EVE Online Corporation: [{} [{}]]({})",
    Locale.ru.__str__(): "Текущие настройки для ***{}***:\n"
                         "* Связанная роль на сервере: ***@{}***\n"
                         "* Связанная корпорация EVE Online: [{} [{}]]({})"
}

CORP_NOT_FOUND_LOC = {
    Locale.en_US.__str__(): "EVE Online Corporation with ID `{}` not found.",
    Locale.ru.__str__(): "Корпорация EVE Online c ID `{}` не найдена."
}

CORP_ID_SET_LOC = {
    Locale.en_US.__str__(): "Linked EVE Online Corporation: ***{} [{}]***.",
    Locale.ru.__str__(): "Связанная корпорация EVE Online: ***{} [{}]***."
}

ROLE_ID_SET_LOC = {
    Locale.en_US.__str__(): "Linked server role: **@{}**.",
    Locale.ru.__str__(): "Связанная роль на сервере: **@{}**."
}

ROLE_NOT_FOUND_LOC = {
    Locale.en_US.__str__(): "Linked server role no longer exist.",
    Locale.ru.__str__(): "Связанная роль на сервере не существует."
}

MEMBER_INFO_LOC = {
    Locale.en_US.__str__(): "User {}\n"
                            "Roles: {}\n"
                            "Registered characters:",
    Locale.ru.__str__(): "Пользователь {}: {}\n"
                         "Роли: {}\n"
                         "Зарегистрированные персонажи: {}"
}

CHARACTER_INFO_LOC = {
    Locale.en_US.__str__(): "Found characters:",
    Locale.ru.__str__(): "Найденные персонажи:"
}

REPORT_INFO_LOC = {
    Locale.en_US.__str__(): "Statistics:\n"
                            "* Total users: {}\n"
                            "* Users registered with bot: {}\n"
                            "* Characters: {}\n"
                            "* Characters in corp: {}\n"
                            "* Characters not in corp: {}",
    Locale.ru.__str__(): "Статистика:\n"
                         "* Всего пользователей: {}\n"
                         "* Пользователей зарегистрировано ботом: {}\n"
                         "* Персонажей: {}\n"
                         "* Персонажей в корпорации: {}\n"
                         "* Персонажей не в корпорации: {}"
}

"""Registration related messages
"""

REGISTER_LINK_LOC = {
    Locale.en_US.__str__(): "Hello, {}!\n\n"
                            "Please use following link to verify your EVE Online character on **'{}'** Discord "
                            "server.\n"
                            "After log in you will be redirected to {} web page.\n\n"
                            "Link will be valid for {} minutes, "
                            "but can be used to register several characters.",
    Locale.ru.__str__(): "Привет, {}!\n\n"
                         "Используй следующую ссылку для подтверждения персонажа EVE Online на сервере "
                         "Discord **'{}'**.\n"
                         "После входа ты будешь перенаправлен на веб страницу {}.\n\n"
                         "Ссылка будет действительна в течение {} минут, "
                         "но может быть использована для регистрации нескольких персонажей."
}

REGISTER_LINK_SENT_LOC = {
    Locale.en_US.__str__(): "Registration link has been sent to user {}.",
    Locale.ru.__str__(): "Ссылка для регистрации отправлена пользователю {}."
}

USER_NOT_REGISTERED_LOC = {
    Locale.en_US.__str__(): "User {} is not registered.",
    Locale.ru.__str__(): "Пользователь {} не зарегистрирован."
}

CHARACTER_ALREADY_REGISTERED_LOC = {
    Locale.en_US.__str__(): "EVE Online character with ID `{}` already registered.",
    Locale.ru.__str__(): "Персонаж EVE Online с ID `{}` уже зарегистрирован."
}

CHARACTER_NOT_FOUND_LOC = {
    Locale.en_US.__str__(): "EVE Online Character with ID `{}` not found.",
    Locale.ru.__str__(): "Персонаж EVE Online с ID `{}` не найден."
}

CHARACTER_NOT_IN_CORP_LOC = {
    Locale.en_US.__str__(): "EVE Online Character is not in linked corporation currently.",
    Locale.ru.__str__(): "Персонаж EVE Online в настоящее время не в связанной корпорации."
}

CHARACTER_LINKED_LOC = {
    Locale.en_US.__str__(): "EVE Online character '{}' has been linked to user {}.",
    Locale.ru.__str__(): "Персонаж EVE Character '{}' привязан к пользователю {}."
}

ROLE_ALREADY_GRANTED_LOC = {
    Locale.en_US.__str__(): "Role {} already granted.",
    Locale.ru.__str__(): "Роль {} уже выдана."
}

ROLE_GRANTED_LOC = {
    Locale.en_US.__str__(): "Role {} granted.",
    Locale.ru.__str__(): "Роль {} выдана."
}

QUERY_STRING_TOO_SHORT_LOC = {
    Locale.en_US.__str__(): "Query string is too short. Minimum length: {} symbols",
    Locale.ru.__str__(): "Значение поискового запроса слишком короткое. Минимальная длина: {} символа"
}

QUERY_CHARACTERS_NOT_FOUND_LOC = {
    Locale.en_US.__str__(): "EVE Online Characters not found.",
    Locale.ru.__str__(): "Персонажи EVE Online не найдены."
}
