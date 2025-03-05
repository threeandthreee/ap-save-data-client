from handlers.ladx.handler import Handler as LADXHandler

class Handler(LADXHandler):
    connect_info = {
        'game': 'Links Awakening DX Beta',
        'uuid': "Link's Awakening DX Beta Save Data Client",
        'version': {'major': 0, 'minor': 5, 'build': 1, 'class': 'Version'},
        'items_handling': 0b101,
        'tags': ['NoText'],
        'slot_data': False,
    }