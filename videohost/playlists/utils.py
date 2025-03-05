def check_if_basic_playlist(title):
    '''Перевіряє, чи є створюваний або оновлюваний плейлист базовим (Переглянути пізніше або )'''
    lower_title = title.lower().strip()
    if lower_title != 'сподобалися' and lower_title != 'переглянути пізніше':
        return False
    return True
