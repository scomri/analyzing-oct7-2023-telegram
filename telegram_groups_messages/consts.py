TELEGRAM_GROUPS_MAP = {
    # The Israeli side groups
    'idf_telegram': {'group_name': 'IDF - The Official Channel', 'language': 'Hebrew', 'type': 'Israeli side'},
    'ForumPressReleases': {'group_name': 'Until the Last Hostage - The Official Page', 'language': 'Hebrew', 'type': 'Israeli side'},

    # Israeli commentary groups
    'abualiexpress': {'group_name': 'Abu Ali Express', 'language': 'Hebrew', 'type': 'Israeli commentary'},
    'arabworld301news': {'group_name': 'Arab World 301 News', 'language': 'Hebrew', 'type': 'Israeli commentary'},
    'salehdesk1': {'group_name': 'Abu Saleh The Arab Desk', 'language': 'Hebrew', 'type': 'Israeli commentary'},

    # Israeli news groups
    'yediotnews': {'group_name': 'News from the Field on Telegram', 'language': 'Hebrew', 'type': 'Israeli news'},
    'Realtimesecurity1': {'group_name': 'Real-Time News', 'language': 'Hebrew', 'type': 'Israeli news'},
    'New_security8200': {'group_name': 'News Channel 8200', 'language': 'Hebrew', 'type': 'Israeli news'},

    # The Palestinian side groups
    'hamasps': {'group_name': 'Hamas Movement', 'language': 'Arabic', 'type': 'Palestinian side'},
    'qassambrigades': {'group_name': 'Al-Qassam Brigades', 'language': 'Arabic', 'type': 'Palestinian side'},

    # Palestinian news groups
    'gazaalannet': {'group_name': 'Gaza Now', 'language': 'Arabic', 'type': 'Palestinian news'},
    'SerajSat': {'group_name': 'Al-Aqsa Channel', 'language': 'Arabic', 'type': 'Palestinian news'},
    'ShehabTelegram': {'group_name': 'Shehab Agency', 'language': 'Arabic', 'type': 'Palestinian news'},
}


if __name__ == '__main__':
    print(TELEGRAM_GROUPS_MAP.keys())
