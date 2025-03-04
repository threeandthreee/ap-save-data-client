from .constants import *


class ItemGiver:
    def __init__(self, save_data_manager):
        self.sdm = save_data_manager

    def give(self, item_name:str) -> None:
        if item_name in inv_items:
            self.add_to_inventory(item_name)

        if item_name in simple_items:
            self.set_bit(getattr(Addr, item_name), 0)
        elif item_name[:-1] in dungeon_item_types:
            self.give_dungeon_item(item_name)
        elif item_name.startswith('TRADING_ITEM_'):
            self.give_trading_item(item_name)
        elif item_name.startswith('RUPEES_'):
            self.give_rupees(int(item_name[7:]))
        elif item_name.startswith('SONG'):
            self.give_song(item_name)
        else:
            func = self.give_mapping.get(item_name)
            if func:
                func(self)


    def add_to_inventory(self, item_name):
        for inv_slot in range(Addr.INV_START, Addr.INV_END):
            if self.sdm.get(inv_slot) == inv_items[item_name]:
                return
        for inv_slot in range(Addr.INV_START, Addr.INV_END):
            if not self.sdm.get(inv_slot):
                self.sdm.set(inv_slot, inv_items[item_name])
                break

    def increase(self, addr, amount=1, limit=0xFF):
        current = self.sdm.get(addr)
        new = current + amount
        self.sdm.set(addr, min(new, limit))

    def give_rupees(self, amount):
        hi = self.sdm.get(Addr.RUPEE_COUNT_HIGH)
        lo = self.sdm.get(Addr.RUPEE_COUNT_LOW)
        total = int(hex(hi)[2:])*100 + int(hex(lo)[2:])
        new_str = str(min(total + amount, 999)).zfill(3)
        new_hi = int(new_str[0])
        new_lo = int(new_str[1]) * 0x10 + int(new_str[2])
        self.sdm.set(Addr.RUPEE_COUNT_HIGH, new_hi)
        self.sdm.set(Addr.RUPEE_COUNT_LOW, new_lo)

    def give_ammo(self, count_addr, max_addr, amount):
        count = self.sdm.get(count_addr)
        inc_str = str((int(hex(count)[2:]) + amount)).zfill(2)
        increased = int(inc_str[0]) * 0x10 + int(inc_str[1])
        max = self.sdm.get(max_addr)
        new_count = min(increased, max)
        self.sdm.set(count_addr, new_count)

    def set_bit(self, addr, bit):
        current = self.sdm.get(addr)
        self.sdm.set(addr, current | 1 << bit)

    def give_power_bracelet(self):
        self.increase(Addr.POWER_BRACELET_LEVEL, limit = 2)

    def give_shield(self):
        self.increase(Addr.SHIELD_LEVEL, limit = 2)

    def give_sword(self):
        self.increase(Addr.SWORD_LEVEL, limit = 2)

    def give_bomb(self):
        self.give_ammo(Addr.BOMB_COUNT, Addr.MAX_BOMBS, 10)

    def give_bow(self):
        arrow_count = self.sdm.get(Addr.ARROW_COUNT)
        if arrow_count < 0x20:
            self.sdm.set(Addr.ARROW_COUNT, 0x20)

    def give_powder(self):
        self.give_ammo(Addr.POWDER_COUNT, Addr.MAX_POWDER, 10)

    def give_boots(self):
        self.set_bit(Addr.COLLECTED_TUNICS, 2)

    def give_golden_leaf(self):
        self.increase(Addr.GOLDEN_LEAVES)

    def give_seashell(self):
        current = self.sdm.get(Addr.SEASHELL_COUNT)
        if hex(current)[-1] == '9':
            self.sdm.set(Addr.SEASHELL_COUNT, current + 7)
        else:
            self.sdm.set(Addr.SEASHELL_COUNT, current + 1)

    def give_heart_piece(self):
        self.increase(Addr.HEART_PIECES)
        if self.sdm.get(Addr.HEART_PIECES) % 4 == 0:
            self.give_full_heart()

    def give_full_heart(self):
        self.increase(Addr.FULL_HEARTS, limit = 14)
        self.sdm.set(Addr.HEALTH, self.sdm.get(Addr.FULL_HEARTS))

    def give_1_arrow(self):
        self.give_ammo(Addr.ARROW_COUNT, Addr.MAX_ARROWS, 1)

    def give_10_arrows(self):
        self.give_ammo(Addr.ARROW_COUNT, Addr.MAX_ARROWS, 10)

    def upgrade_max_powder(self):
        current = self.sdm.get(Addr.POWDER_COUNT)
        if current:
            self.sdm.set(Addr.POWDER_COUNT, 0x40)
        self.sdm.set(Addr.MAX_POWDER, 0x40)

    def upgrade_max_bombs(self):
        self.sdm.set(Addr.BOMB_COUNT, 0x60)
        self.sdm.set(Addr.MAX_BOMBS, 0x60)

    def upgrade_max_arrows(self):
        self.sdm.set(Addr.ARROW_COUNT, 0x60)
        self.sdm.set(Addr.MAX_ARROWS, 0x60)

    def give_red_tunic(self):
        self.sdm.set(Addr.SELECTED_TUNIC, 1)
        self.set_bit(Addr.COLLECTED_TUNICS, 0)

    def give_blue_tunic(self):
        self.sdm.set(Addr.SELECTED_TUNIC, 2)
        self.set_bit(Addr.COLLECTED_TUNICS, 1)

    def give_song(self, item_name):
        song = int(item_name[-1])
        self.set_bit(Addr.COLLECTED_SONGS, 3-song)
        self.sdm.set(Addr.SELECTED_SONG, song-1)

    def give_dungeon_item(self, item_name):
        address = dungeon_item_addresses[item_name[-1] - 1]
        bit = dungeon_item_types.index(item_name[:-1])
        if item_name.startswith('KEY'):
            current = self.sdm.get(address)
            self.sdm.set(address, current + (1 << bit))
        else:
            self.set_bit(address, bit)

    def give_trading_item(self, item_name):
        index = trading_items.index(item_name)
        if index < 8:
            self.set_bit(Addr.TRADE_SEQUENCE_ITEM, index)
        else:
            self.set_bit(Addr.TRADE_SEQUENCE_ITEM_2, index - 8)

    give_mapping = {
        'POWER_BRACELET': give_power_bracelet,
        'SHIELD': give_shield,
        'BOW': give_bow,
        'PEGASUS_BOOTS': give_boots,
        'MAGIC_POWDER': give_powder,
        'BOMB': give_bomb,
        'SWORD': give_sword,
        'GOLD_LEAF': give_golden_leaf,
        'SEASHELL': give_seashell,
        # 'ROOSTER': give_rooster,
        'HEART_PIECE': give_heart_piece,
        'ARROWS_10': give_10_arrows,
        'SINGLE_ARROW': give_1_arrow,
        'MAX_POWDER_UPGRADE': upgrade_max_powder,
        'MAX_BOMBS_UPGRADE': upgrade_max_bombs,
        'MAX_ARROWS_UPGRADE': upgrade_max_arrows,
        'RED_TUNIC': give_red_tunic,
        'BLUE_TUNIC': give_blue_tunic,
        'HEART_CONTAINER': give_full_heart,
    }

