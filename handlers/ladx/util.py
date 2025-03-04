import struct
from .constants import BASE_ID, CHEST_ITEMS, checkMetadataTable


class SaveDataManager:
    save_data: bytearray

    def __init__(self, save_data):
        if len(save_data) != 32768: # check for correct length
            raise Exception("Invalid save data for Link's Awakening DX")
        for addr in range(0x100): # ladx save skips first 256 bytes
            if save_data[addr] != 0xff:
                raise Exception("Invalid save data for Link's Awakening DX")
        for i in range(0x5): # the next 5 bytes are 1,3,5,7,9
            addr = 0x100 + i
            verification_value = (i * 2) + 1
            if save_data[addr] != verification_value:
                raise Exception("Invalid save data for Link's Awakening DX")
        self.save_data = bytearray(save_data)

    def get(self, addr:int) -> int:
        return self.save_data[to_save_address(addr)]

    def set(self, addr:int, value:int) -> None:
        self.save_data[to_save_address(addr)] = value

    def get_2(self, addr:int) -> int:
        save_addr = to_save_address(addr)
        return struct.unpack('>H', self.save_data[save_addr:save_addr+2])[0]

    def set_2(self, addr:int, value:int) -> None:
        [hi, lo] = struct.pack('>H', value)
        self.save_data[to_save_address(addr)] = hi
        self.save_data[to_save_address(addr+1)] = lo

    def dump(self):
        return bytes(self.save_data)


def to_save_address(address):
    if 0xD800 <= address < 0xDB80: # wram copy
        return address - 0xD800 + 0x100 + 0x5
    elif 0xDDDA <= address < 0xDDDF: # color dungeon item flags
        return address - 0xDDDA + 0x100 + 0x5 + 0x380
    elif 0xDDE0 <= address < 0xDE00: # color dungeon room status
        return address - 0xDDE0 + 0x100 + 0x5 + 0x380 + 0x5
    elif 0xDC0F == address: # selected tunic
        return address - 0xDC0F + 0x100 + 0x5 + 0x380 + 0x5 + 0x20
    elif 0xDC0C <= address < 0xDC0E: # photos
        return address - 0xDC0C + 0x100 + 0x5 + 0x380 + 0x5 + 0x20 + 0x1
    else:
        return address


ap_item_to_ladxr = {}
for name, id in CHEST_ITEMS.items():
    ap_item_to_ladxr[BASE_ID + id] = name


ladxr_loc_to_ap = {}
for addr, meta in checkMetadataTable.items():
    if addr == 'None':
        continue
    splits = addr.split('-')
    main_id = int(splits[0], 16)
    sub_id = 0
    if len(splits) > 1:
        sub_id = splits[1]
        if sub_id.isnumeric():
            sub_id = (int(sub_id) + 1) * 1000
        else:
            sub_id = 1000
    ladxr_loc_to_ap[addr] = BASE_ID + main_id + sub_id
