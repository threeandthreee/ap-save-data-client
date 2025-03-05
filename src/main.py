import argparse
import importlib
import json
import os
import socket
from wsproto import WSConnection, ConnectionType
from wsproto.utilities import RemoteProtocolError
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
        print(f"{game_config['name']}[{game_config['handler']}] - {msg}")


def synchronize(config:dict):
    # read file
    save_path = os.path.join(config.get('base_path', ''), config['save_file'])
    try:
        with open(save_path, 'rb') as f:
            save_data = f.read()
    except FileNotFoundError:
        return 'Save file not found'

    # initialize handler
    handler_str = f"handlers.{config['handler']}.handler"
    handler = importlib.import_module(handler_str).Handler(save_data)

    # get outgoing data from handler
    outgoing_checks, victory = handler.send()

    # connect to ap room, switch to ssl if fail
    socket.setdefaulttimeout(5)
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((config['host'], int(config['port'])))
        ws = WSConnection(ConnectionType.CLIENT)
        received = send_recv(ws, conn, Request(host=config['host'], target="/"))
    except RemoteProtocolError:
        import ssl
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = ctx.wrap_socket(conn, server_hostname=config['host'])
        conn.connect((config['host'], int(config['port'])))
        ws = WSConnection(ConnectionType.CLIENT)
        received = send_recv(ws, conn, Request(host=config['host'], target="/"))

    if not received.get('AcceptConnection'):
        return 'Initial connection failed'

    received |= send_recv(ws, conn) # room data
    received |= send_recv(ws, conn, Message(data=json.dumps([{
        'cmd': 'Connect',
        'name': config['name'],
        'password': config.get('password'),
        **handler.connect_info,
    }])))
    connected = received.get('Connected')
    if not connected:
        connection_refused = received.get('ConnectionRefused', {})
        return f"Connection refused: {connection_refused.get('errors')}"

    # sync with server, close connection (get race mode to force response)
    to_send = [{'cmd': 'Sync'}, {'cmd': 'Get', 'keys': 'race_mode'}]
    if outgoing_checks:
        to_send.append({'cmd': 'LocationChecks', 'locations': outgoing_checks})
    if victory or config.get('force_victory'):
        to_send.append({'cmd': 'StatusUpdate', 'status': 30})
    received |= send_recv(ws, conn, Message(data=json.dumps(to_send)))
    received_items = received.get('ReceivedItems')

    close(ws, conn)

    # give incoming data to handler
    save_data = handler.receive(connected, received_items)

    # write to save file
    with open(save_path, 'wb') as f:
        f.write(save_data)


def send_recv(ws, conn, msg=None) -> dict:
    if(msg):
        conn.send(ws.send(msg))
    ws.receive_data(conn.recv(RECEIVE_BYTES) or None)
    received = {}
    for event in ws.events():
        if isinstance(event, TextMessage):
            msgs = json.loads(event.data)
            for msg in msgs:
                received[msg['cmd']] = msg
        elif isinstance(event, AcceptConnection):
            received['AcceptConnection'] = True
    return received


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
