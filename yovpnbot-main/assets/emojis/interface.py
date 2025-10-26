"""
Эмодзи для интерфейса бота
Современные и понятные эмодзи для всех элементов UI
"""

# Основные категории эмодзи
EMOJI = {
    # Пользователь и профиль
    'user': '👤',
    'profile': '👨‍💼',
    'avatar': '🖼️',
    'account': '👤',
    
    # Подписки и VPN
    'subscription': '📱',
    'vpn': '🔒',
    'shield': '🛡️',
    'lock': '🔒',
    'unlock': '🔓',
    'security': '🛡️',
    'privacy': '🔐',
    'anonymous': '🎭',
    
    # Финансы и платежи
    'balance': '💰',
    'money': '💵',
    'payment': '💳',
    'card': '💳',
    'wallet': '👛',
    'coins': '🪙',
    'dollar': '💲',
    'ruble': '₽',
    
    # Навигация и действия
    'home': '🏠',
    'back': '⬅️',
    'forward': '➡️',
    'up': '⬆️',
    'down': '⬇️',
    'refresh': '🔄',
    'reload': '🔄',
    'search': '🔍',
    'filter': '🔍',
    'sort': '🔀',
    
    # Статусы и состояния
    'active': '🟢',
    'inactive': '🔴',
    'pending': '🟡',
    'loading': '⏳',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'check': '✅',
    'cross': '❌',
    'question': '❓',
    'exclamation': '❗',
    
    # Настройки и конфигурация
    'settings': '⚙️',
    'gear': '⚙️',
    'config': '🔧',
    'tools': '🛠️',
    'preferences': '🎛️',
    'options': '📋',
    
    # Связь и поддержка
    'support': '🆘',
    'help': '❓',
    'contact': '📞',
    'phone': '📱',
    'email': '📧',
    'message': '💬',
    'chat': '💬',
    'call': '📞',
    
    # Социальные функции
    'referral': '👥',
    'friends': '👥',
    'invite': '📨',
    'share': '📤',
    'like': '👍',
    'dislike': '👎',
    'star': '⭐',
    'favorite': '❤️',
    
    # Технические элементы
    'server': '🖥️',
    'computer': '💻',
    'mobile': '📱',
    'tablet': '📱',
    'wifi': '📶',
    'signal': '📶',
    'connection': '🔗',
    'link': '🔗',
    'url': '🌐',
    'website': '🌐',
    
    # QR-коды и копирование
    'qr': '📱',
    'qrcode': '📱',
    'copy': '📋',
    'clipboard': '📋',
    'paste': '📋',
    'download': '⬇️',
    'upload': '⬆️',
    'export': '📤',
    'import': '📥',
    
    # Время и даты
    'time': '⏰',
    'clock': '🕐',
    'calendar': '📅',
    'date': '📅',
    'schedule': '📅',
    'timer': '⏱️',
    'stopwatch': '⏱️',
    'hourglass': '⏳',
    
    # История и статистика
    'history': '📊',
    'stats': '📈',
    'chart': '📊',
    'graph': '📈',
    'analytics': '📊',
    'data': '📊',
    'report': '📋',
    'log': '📝',
    
    # Купоны и акции
    'coupon': '🎫',
    'ticket': '🎫',
    'discount': '🏷️',
    'sale': '🏷️',
    'offer': '🎁',
    'gift': '🎁',
    'present': '🎁',
    'bonus': '🎁',
    
    # Устройства и платформы
    'device': '📱',
    'android': '🤖',
    'ios': '🍎',
    'windows': '🪟',
    'mac': '🍎',
    'linux': '🐧',
    'browser': '🌐',
    'app': '📱',
    
    # Скорость и производительность
    'speed': '⚡',
    'fast': '⚡',
    'slow': '🐌',
    'performance': '⚡',
    'boost': '🚀',
    'rocket': '🚀',
    'turbo': '💨',
    
    # Безопасность и конфиденциальность
    'no_logs': '🔒',
    'encryption': '🔐',
    'secure': '🔒',
    'protected': '🛡️',
    'verified': '✅',
    'trusted': '✅',
    'safe': '✅',
    
    # Уведомления и алерты
    'notification': '🔔',
    'bell': '🔔',
    'alert': '🚨',
    'alarm': '🚨',
    'reminder': '⏰',
    'announcement': '📢',
    'broadcast': '📢',
    'channel': '📢',
    
    # Дополнительные элементы
    'plus': '➕',
    'minus': '➖',
    'add': '➕',
    'remove': '➖',
    'edit': '✏️',
    'delete': '🗑️',
    'trash': '🗑️',
    'save': '💾',
    'folder': '📁',
    'file': '📄',
    'document': '📄'
}

# Специальные комбинации эмодзи для разных сценариев
EMOJI_COMBINATIONS = {
    'welcome': '👋🎉',
    'goodbye': '👋😊',
    'success': '✅🎉',
    'error': '❌😔',
    'loading': '⏳🔄',
    'thinking': '🤔💭',
    'celebration': '🎉🎊',
    'congratulations': '🎉👏',
    'thank_you': '🙏💙',
    'sorry': '😔🙏',
    'warning': '⚠️🚨',
    'info': 'ℹ️📋',
    'question': '❓🤔',
    'money': '💰💵',
    'security': '🔒🛡️',
    'speed': '⚡🚀',
    'connection': '🔗📶',
    'settings': '⚙️🔧',
    'support': '🆘💬',
    'referral': '👥🎁',
    'subscription': '📱🔒',
    'payment': '💳💰',
    'balance': '💰💵',
    'history': '📊📈',
    'qr_code': '📱📱',
    'copy_link': '📋🔗',
    'download': '⬇️📥',
    'upload': '⬆️📤'
}

# Эмодзи для прогресс-баров
PROGRESS_BAR_EMOJIS = {
    'filled': '█',
    'half_filled': '▌',
    'empty': '░',
    'border_left': '[',
    'border_right': ']',
    'percentage': '%'
}

def get_emoji(key: str) -> str:
    """
    Получить эмодзи по ключу
    
    Args:
        key: Ключ эмодзи
    
    Returns:
        str: Эмодзи или пустая строка если не найдено
    """
    return EMOJI.get(key, '')

def get_emoji_combination(key: str) -> str:
    """
    Получить комбинацию эмодзи по ключу
    
    Args:
        key: Ключ комбинации
    
    Returns:
        str: Комбинация эмодзи или пустая строка если не найдено
    """
    return EMOJI_COMBINATIONS.get(key, '')

def create_progress_bar(current: int, total: int, width: int = 10) -> str:
    """
    Создать прогресс-бар из эмодзи
    
    Args:
        current: Текущее значение
        total: Максимальное значение
        width: Ширина прогресс-бара
    
    Returns:
        str: Прогресс-бар
    """
    if total == 0:
        return f"{PROGRESS_BAR_EMOJIS['border_left']}{PROGRESS_BAR_EMOJIS['empty'] * width}{PROGRESS_BAR_EMOJIS['border_right']} 0%"
    
    percentage = (current / total) * 100
    filled_width = int((current / total) * width)
    empty_width = width - filled_width
    
    bar = (
        PROGRESS_BAR_EMOJIS['border_left'] +
        PROGRESS_BAR_EMOJIS['filled'] * filled_width +
        PROGRESS_BAR_EMOJIS['empty'] * empty_width +
        PROGRESS_BAR_EMOJIS['border_right']
    )
    
    return f"{bar} {percentage:.0f}%"

def format_balance(amount: float) -> str:
    """
    Форматировать баланс с эмодзи
    
    Args:
        amount: Сумма баланса
    
    Returns:
        str: Отформатированный баланс
    """
    return f"{EMOJI['balance']} {amount:.2f} ₽"

def format_days(days: int) -> str:
    """
    Форматировать количество дней с эмодзи
    
    Args:
        days: Количество дней
    
    Returns:
        str: Отформатированные дни
    """
    if days == 1:
        return f"{EMOJI['time']} {days} день"
    elif days in [2, 3, 4]:
        return f"{EMOJI['time']} {days} дня"
    else:
        return f"{EMOJI['time']} {days} дней"

def format_status(status: str) -> str:
    """
    Форматировать статус с соответствующим эмодзи
    
    Args:
        status: Статус (active, inactive, pending, etc.)
    
    Returns:
        str: Статус с эмодзи
    """
    status_emojis = {
        'active': EMOJI['active'],
        'inactive': EMOJI['inactive'],
        'pending': EMOJI['pending'],
        'loading': EMOJI['loading'],
        'success': EMOJI['success'],
        'error': EMOJI['error'],
        'warning': EMOJI['warning']
    }
    
    emoji = status_emojis.get(status.lower(), '')
    return f"{emoji} {status.title()}" if emoji else status.title()