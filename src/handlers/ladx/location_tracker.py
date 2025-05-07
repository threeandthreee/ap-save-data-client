from .constants import checkMetadataTable


# kbranch you're a hero
# https://github.com/kbranch/Magpie/blob/master/autotracking/checks.py
class Check:
    def __init__(self, id, address, mask, alternateAddress=None):
        self.id = id
        self.address = address
        self.alternateAddress = alternateAddress
        self.mask = mask
        self.value = None
        self.diff = 0

    def set(self, bytes):
        oldValue = self.value

        self.value = 0

        for byte in bytes:
            maskedByte = byte
            if self.mask:
                maskedByte &= self.mask

            self.value |= int(maskedByte > 0)

        if oldValue != self.value:
            self.diff += self.value - (oldValue or 0)
# Todo: unify this with existing item tables?


class LocationTracker:
    all_checks = []
    meta_to_check = {}

    def __init__(self, save_data_manager):
        self.sdm = save_data_manager
        maskOverrides = {
            '0x106': 0x20,
            '0x12B': 0x20,
            '0x15A': 0x20,
            '0x166': 0x20,
            '0x185': 0x20,
            '0x1E4': 0x20,
            '0x1BC': 0x20,
            '0x1E0': 0x20,
            '0x1E1': 0x20,
            '0x1E2': 0x20,
            '0x223': 0x20,
            '0x234': 0x20,
            '0x2A3': 0x20,
            '0x2FD': 0x20,
            '0x2A7': 0x20,
            '0x1F5': 0x06,
            '0x301-0': 0x10,
            '0x301-1': 0x10,
            '0x2E9-0': 0x20,
            '0x2E9-1': 0x40,
        }

        addressOverrides = {
            '0x30A-Owl': 0xDDEA,
            '0x30F-Owl': 0xDDEF,
            '0x308-Owl': 0xDDE8,
            '0x302': 0xDDE2,
            '0x306': 0xDDE6,
            '0x307': 0xDDE7,
            '0x308': 0xDDE8,
            '0x30F': 0xDDEF,
            '0x311': 0xDDF1,
            '0x314': 0xDDF4,
            '0x1F5': 0xDB7D,
            '0x301-0': 0xDDE1,
            '0x301-1': 0xDDE1,
            '0x223': 0xDA2E,
            '0x169': 0xD97C,
            '0x2A7': 0xD800 + 0x2A1
        }

        alternateAddresses = {
            '0x0F2': 0xD8B2,
        }

        blacklist = {'None', '0x2A1-2'}

        # in no dungeons boss shuffle, the d3 boss in d7 set 0x20 in fascade's room (0x1BC)
        # after beating evil eagile in D6, 0x1BC is now 0xAC (other things may have happened in between)
        # entered d3, slime eye flag had already been set (0x15A 0x20). after killing angler fish, bits 0x0C were set
        for check_id in [x for x in checkMetadataTable if x not in blacklist]:
            room = check_id.split('-')[0]
            mask = 0x10
            address = addressOverrides[check_id] if check_id in addressOverrides else 0xD800 + int(
                room, 16)

            if 'Trade' in check_id or 'Owl' in check_id:
                mask = 0x20

            if check_id in maskOverrides:
                mask = maskOverrides[check_id]

            check = Check(
                check_id,
                address,
                mask,
                (alternateAddresses[check_id] if check_id in alternateAddresses else None),
            )

            if check_id == '0x2A3':
                self.start_check = check
            self.all_checks.append(check)
            self.meta_to_check[check.id] = check
        self.remaining_checks = [check for check in self.all_checks]

    def has_start_item(self):
        return self.start_check not in self.remaining_checks

    def readChecks(self):
        new_checks = []
        for check in self.remaining_checks:
            addresses = [check.address]
            if check.alternateAddress:
                addresses.append(check.alternateAddress)
            bytes = [self.sdm.get(address) for address in addresses]
            check.set(bytes)

            if check.value:
                self.remaining_checks.remove(check)
                new_checks.append(check)

        return new_checks