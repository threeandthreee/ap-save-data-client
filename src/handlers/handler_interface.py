class HandlerInterface:
    connect_info:dict = {} # game | version | items_handling | tags | slot_data

    def __init__(self, save_data:bytes) -> None:
        self.save_data = save_data

    def send(self) -> tuple[list[int],bool]:
        locations = []
        victory = False
        return locations, victory

    def receive(self, connected, received_items) -> bytes:
        return self.save_data
