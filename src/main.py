import argparse
import importlib
import json
import os
import socket
from wsproto import WSConnection, ConnectionType
from wsproto.events import (
    AcceptConnection,
    Request,
    Message,
    TextMessage,
    CloseConnection,
)


RECEIVE_BYTES = 4096

def main(args:argparse.Namespace):
    with open(args.config_file) as f:
        config = json.loads(f.read())

    for game_config in config['games']:
        game_config = config.get('base',{}) | game_config
        msg = synchronize(game_config) or 'Synchronized'
        print(f'{game_config['name']}[{game_config['handler']}] - {msg}')


def synchronize(config:dict):
    # read file
    save_path = os.path.join(config.get('base_path', ''), config['save_file'])
    try:
        with open(save_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        return 'Save file not found'

    # initialize handler
    handler_str = f'handlers.{config['handler']}.handler'
    handler = importlib.import_module(handler_str).Handler(save_data)

    # get outgoing data from handler
    outgoing_checks, victory = handler.send()

    # connect to ap room
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(5)
    conn.connect((config['host'], config['port']))
    ws = WSConnection(ConnectionType.CLIENT)
    send_recv(ws, conn, Request(host=config['host'], target="server"))
    if not [e for e in ws.events() if isinstance(e, AcceptConnection)]:
        return f'Initial connection failed'
    send_recv(ws, conn)
    send_recv(ws, conn, Message(data=json.dumps([{
        'cmd': 'Connect',
        'name': config['name'],
        'password': config.get('password'),
        **handler.connect_info,
    }])))
    connected = get_message(ws, 'Connected')
    if not connected:
        connection_refused = get_message(ws, 'ConnectionRefused')
        return f'Connection refused: {connection_refused.get('errors')}'

    # sync with server, close connection (get race mode to force response)
    to_send = [{'cmd': 'Sync'}, {'cmd': 'Get', 'keys': 'race_mode'}]
    if outgoing_checks:
        to_send.append({'cmd': 'LocationChecks', 'locations': outgoing_checks})
    if victory or config.get('force_victory'):
        to_send.append({'cmd': 'StatusUpdate', 'status': 30})
    send_recv(ws, conn, Message(data=json.dumps(to_send)))
    received_items = get_message(ws, 'ReceivedItems')

    close(ws, conn)

    # give incoming data to handler
    save_data = handler.receive(connected, received_items)

    # write to save file
    with open(save_path, 'wb') as f:
        f.write(save_data)


def send_recv(ws, conn, msg=None):
    if(msg):
        conn.send(ws.send(msg))
    ws.receive_data(conn.recv(RECEIVE_BYTES) or None)


def get_message(ws, cmd):
    for event in ws.events():
        if isinstance(event, TextMessage):
            msgs = json.loads(event.data)
            for msg in msgs:
                if msg['cmd'] == cmd:
                    return msg


def close(ws, conn):
    send_recv(ws, conn, CloseConnection(code=1000, reason="done"))
    conn.shutdown(socket.SHUT_WR)
    send_recv(ws, conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Archipelago Save Data Client',
        usage="config_file"
    )
    parser.add_argument('config_file', help='JSON config file')
    main(parser.parse_args())
