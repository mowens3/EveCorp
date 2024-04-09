from nextcord import Locale


def get_localized(a: dict, locale: str):
    return a[locale] if locale in [Locale.ru] else a[Locale.en_US.__str__()]


"""Generic messages
"""

SOMETHING_WENT_WRONG = {
    Locale.en_US.__str__(): "Something went wrong.",
    Locale.ru.__str__(): "Что-то пошло не так."
}

GUILD_ONLY = {
    Locale.en_US.__str__(): "This command should me executed on server channel.",
    Locale.ru.__str__(): "Эта команда должна выполняться только на канале сервера."
}

"""Server related messages
"""

SERVER_SETTINGS_UPDATED = {
    Locale.en_US.__str__(): "Server settings for ***{}***:\n"
                            "* Notification channel: {}\n"
                            "* Notification language: {}",
    Locale.ru.__str__(): "Настройки сервера для ***{}***:\n"
                         "* Канал для уведомлений: {}\n"
                         "* Язык для уведомлений: {}"
}

"""Server Rules related messages
"""

SERVER_RULES_NOT_FOUND = {
    Locale.en_US.__str__(): "Rules for ***{}*** not found.",
    Locale.ru.__str__(): "Правила для ***{}*** не найдены."
}

SERVER_RULE_CREATED = {
    Locale.en_US.__str__(): "New rule for ***{}***:\n"
                            "* Server role: {}\n"
                            "* EVE Online Corporation: [{} [{}]]({})",
    Locale.ru.__str__(): "Новое правило для ***{}***:\n"
                         "* Роль на сервере: {}\n"
                         "* Корпорация EVE Online: [{} [{}]]({})"
}

SERVER_RULE_UPDATED = {
    Locale.en_US.__str__(): "Rule updated.",
    Locale.ru.__str__(): "Правило обновлено."
}

SERVER_RULE_PICK = {
    Locale.en_US.__str__(): "Pick rule:",
    Locale.ru.__str__(): "Выберите правило:"
}

SERVER_RULE_EXISTS = {
    Locale.en_US.__str__(): "Rule already exists.",
    Locale.ru.__str__(): "Правило уже существует."
}

SERVER_RULE_NOT_FOUND = {
    Locale.en_US.__str__(): "Rule doesn't exists.",
    Locale.ru.__str__(): "Правило не существует."
}

SERVER_RULE_REMOVED = {
    Locale.en_US.__str__(): "Rule removed.",
    Locale.ru.__str__(): "Правило удалено."
}

SERVER_RULES_INFO_HEADER = {
    Locale.en_US.__str__(): "Rules for ***{}***:\n",
    Locale.ru.__str__(): "Правила для ***{}***:\n"
}

SERVER_RULES_INFO_ROW = {
    Locale.en_US.__str__(): "* Rule #{}:\n"
                            "  * Server role: {}\n"
                            "  * EVE Online Corporation: [{} [{}]]({})",
    Locale.ru.__str__(): "* Rule {}:\n"
                         "  * Роль на сервере: {}\n"
                         "  * Корпорация EVE Online: [{} [{}]]({})"
}

CORP_NOT_FOUND = {
    Locale.en_US.__str__(): "EVE Online Corporation with ID `{}` not found.",
    Locale.ru.__str__(): "Корпорация EVE Online c ID `{}` не найдена."
}

ROLE_NOT_FOUND = {
    Locale.en_US.__str__(): "Server role {} `ID: {}` no longer exist.",
    Locale.ru.__str__(): "Роль на сервере {} `ID: {}` не существует."
}

MEMBER_INFO = {
    Locale.en_US.__str__(): "User {}\n"
                            "Roles: {}\n"
                            "Registered characters:\n",
    Locale.ru.__str__(): "Пользователь {}:\n"
                         "Роли: {}\n"
                         "Зарегистрированные персонажи:\n"
}

CHARACTER_INFO_HEADER = {
    Locale.en_US.__str__(): "Found characters:\n",
    Locale.ru.__str__(): "Найденные персонажи:\n"
}

REPORTS_STATS_INFO = {
    Locale.en_US.__str__(): "Statistics:\n"
                            "* Total users count: {}\n"
                            "* Users registered with bot: {}\n"
                            "* Users not registered with bot: {}\n"
                            "* Total characters count: {}",
    Locale.ru.__str__(): "Статистика:\n"
                         "* Всего пользователей: {}\n"
                         "* Пользователей зарегистрировано с помощью бота: {}\n"
                         "* Незарегистрированных пользователей: {}\n"
                         "* Всего персонажей: {}"
}

"""Registration related messages
"""

REGISTER_LINK_TEXT = {
    Locale.en_US.__str__():
        "Hello, {}!\n\n"
        "Please use link below to verify your EVE Online character on **'{}'** Discord server.\n"
        "After authorization in on `{}` you will be redirected to `{}`.\n\n"
        "Link will be valid for {} minutes and could be used to register several characters.",
    Locale.ru.__str__():
        "Привет, {}!\n\n"
        "Используй ссылку в конце сообщения для подтверждения персонажа EVE Online на сервере Discord **'{}'**.\n"
        "После авторизации на `{}` ты будешь перенаправлен на `{}`.\n\n"
        "Ссылка будет действительна в течение {} минут и может быть использована для регистрации нескольких персонажей."
}


REGISTER_COMPLETE_TEXT = {
    Locale.en_US.__str__():
        "Hello, {}!\n\n"
        "You successfully registered!!",

    Locale.ru.__str__():
        "Hello, {}!\n\n"
        "You successfully registered!!",
}

REGISTER_LINK_SENT = {
    Locale.en_US.__str__(): "Registration link has been sent to user {}.",
    Locale.ru.__str__(): "Ссылка для регистрации отправлена пользователю {}."
}

USER_NOT_REGISTERED = {
    Locale.en_US.__str__(): "User {} is not registered.",
    Locale.ru.__str__(): "Пользователь {} не зарегистрирован."
}

NO_REGISTERED_USERS = {
    Locale.en_US.__str__(): "No registered users.",
    Locale.ru.__str__(): "Нет зарегистрированных пользователей"
}

CHARACTER_ALREADY_REGISTERED = {
    Locale.en_US.__str__(): "EVE Online character with ID `{}` already registered.",
    Locale.ru.__str__(): "Персонаж EVE Online с ID `{}` уже зарегистрирован."
}

REGISTERED_USERS_HEADER = {
    Locale.en_US.__str__(): "Registered users ({}):\n",
    Locale.ru.__str__(): "Зарегистрированные пользователи ({}):\n"
}

NO_UNREGISTERED_USERS_HEADER = {
    Locale.en_US.__str__(): "All users registered.",
    Locale.ru.__str__(): "Все пользователи зарегистрированы."
}

UNREGISTERED_USERS_HEADER = {
    Locale.en_US.__str__(): "Unregistered users ({}):\n",
    Locale.ru.__str__(): "Незарегистрированные пользователи ({}):\n"
}

USER_CHARACTERS_NOT_FOUND = {
    Locale.en_US.__str__(): "EVE Online Characters not found.",
    Locale.ru.__str__(): "Персонажи EVE Online не найдены."
}

PICK_USER_CHARACTER = {
    Locale.en_US.__str__(): "Pick character:",
    Locale.ru.__str__(): "Выбери персонажа:"
}

CHARACTER_NOT_FOUND = {
    Locale.en_US.__str__(): "EVE Online Character with ID `{}` not found.",
    Locale.ru.__str__(): "Персонаж EVE Online с ID `{}` не найден."
}

CHARACTER_REGISTERED = {
    Locale.en_US.__str__(): "EVE Online character ***{}*** has been registered to user {}.",
    Locale.ru.__str__(): "Персонаж EVE Character ***{}*** привязан к пользователю {}."
}

USER_CHARACTER_REMOVED = {
    Locale.en_US.__str__(): "EVE Online character ***{}*** has been removed from {} character list.",
    Locale.ru.__str__(): "Персонаж EVE Character ***{}*** удален из списка персонажей {}."
}

ROLE_GRANTED = {
    Locale.en_US.__str__(): "Role {} was granted to {}.",
    Locale.ru.__str__(): "Роль {} выдана пользователю {}."
}

ROLE_REVOKED = {
    Locale.en_US.__str__(): "Role {} has been revoked from {}.",
    Locale.ru.__str__(): "Роль {} пользователя {} отозвана."
}

INVALID_PERMISSIONS_MEMBER_LIST = {
    Locale.en_US.__str__(): "EVECommissar probably doesn't have permissions to access member list.",
    Locale.ru.__str__(): "EVECommissar вероятно не имеет разрешений для доступа к списку пользователей сервера."
}

# '/who' query related messages

QUERY_STRING_TOO_SHORT = {
    Locale.en_US.__str__(): "Query string is too short. Minimum length: {} symbols",
    Locale.ru.__str__(): "Значение поискового запроса слишком короткое. Минимальная длина: {} символа"
}

QUERY_CHARACTERS_NOT_FOUND = {
    Locale.en_US.__str__(): "EVE Online Characters not found.",
    Locale.ru.__str__(): "Персонажи EVE Online не найдены."
}
