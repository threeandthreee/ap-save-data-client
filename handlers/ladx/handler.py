from handler_interface import HandlerInterface
from .item_giver import ItemGiver
from .location_tracker import LocationTracker
from .util import SaveDataManager, ladxr_loc_to_ap, ap_item_to_ladxr
from .constants import Addr


class Handler(HandlerInterface):
    connect_info = {
        'game': 'Links Awakening DX',
        'uuid': "Link's Awakening DX Save Data Client",
        'version': {'major': 0, 'minor': 5, 'build': 1, 'class': 'Version'},
        'items_handling': 0b101,
        'tags': ['NoText'],
        'slot_data': False,
    }

    def __init__(self, save_data):
        self.sdm = SaveDataManager(save_data)
        self.location_tracker = LocationTracker(self.sdm)
        self.item_giver = ItemGiver(self.sdm)

    def send(self):
        checks = self.location_tracker.readChecks()
        locations = [ladxr_loc_to_ap[check.id] for check in checks]
        victory = bool(self.sdm.get(Addr.TRADE_SEQUENCE_ITEM_2) & 1 << 7)
        return (locations, victory)

    def receive(self, connected, received_items):
        received_index = self.sdm.get_2(Addr.RECEIVED_INDEX)
        start_index = received_items['index']
        for index, item in enumerate(received_items['items']):
            item_index = start_index + index
            if item_index == received_index:
                item_name = ap_item_to_ladxr[item['item']]
                self.item_giver.give(item_name)
                received_index += 1
        self.sdm.set_2(Addr.RECEIVED_INDEX, received_index)
        return self.sdm.dump()
