from handlers.ladx.handler import Handler as LADXHandler

class Handler(LADXHandler):
    connect_info = {
        'game': 'Links Awakening DX Beta',
        'items_handling': 0b101,
        'tags': ['NoText'],
        'slot_data': False,
    }