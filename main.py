import argparse
import importlib
import json
import os
import yaml
from websockets.sync.client import connect


def main(args:argparse.Namespace):
    with open(args.config_file) as f:
        config = yaml.safe_load(f)

    for game_config in config['games']:
        #try:
            if 'base' in config:
                game_config = config['base'] | game_config
            synchronize(game_config)
        #except Exception as e:
        #    print(f'Failed to synchronize {game_config["name"]}')
        #    print(e)


def synchronize(config:dict):
    save_path = os.path.join(config['base_path'], config['save_file'])
    with open(save_path, 'rb') as f:
        save_data = f.read()

    handler_str = f'handlers.{config['handler']}.handler'
    handler = importlib.import_module(handler_str).Handler(save_data)

    outgoing_checks, victory = handler.send()

    with connect(f'ws://{config['host']}:{config['port']}') as websocket:
        received_data = []
        def receive_until(targets:list[str]) -> dict:
            while True:
                new_data = json.loads(websocket.recv(timeout=5))
                received_data.extend(new_data)
                match = next((x for x in new_data if x['cmd'] in targets), None)
                if match:
                    return match

        receive_until(['RoomInfo'])

        websocket.send(json.dumps([{
            'cmd': 'Connect',
            'name': config['name'],
            'password': config.get('password'),
            **handler.connect_info,
        }]))
        connected = receive_until(['Connected', 'ConnectionRefused'])
        if connected['cmd'] == 'ConnectionRefused':
            raise Exception(connected['errors'])

        to_send = [{'cmd': 'Sync'}]
        if outgoing_checks:
            to_send.append({'cmd': 'LocationChecks', 'locations': outgoing_checks})
        if victory or config.get('force_victory'):
            to_send.append({'cmd': 'StatusUpdate', 'status': 30})
        websocket.send(json.dumps(to_send))

        received_items = receive_until(['ReceivedItems'])

    new_save_data = handler.receive(connected, received_items)

    with open(save_path, 'wb') as f:
        f.write(new_save_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Archipelago Save Data Client',
        usage="config_file"
    )
    parser.add_argument('config_file', help="YAML config file")
    main(parser.parse_args())
