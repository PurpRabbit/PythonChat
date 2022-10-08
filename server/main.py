import argparse

from server import Server


parser = argparse.ArgumentParser(description="Server settings")
parser.add_argument(
    "-i", "--ipAddress",
    type=str,
    required=False,
    dest='server_ip',
    help="Ip address ('127.0.0.1' by default)"
    )
parser.add_argument(
    "-p", "--port",
    type=int,
    required=False,
    dest='server_port',
    help="Port to listen (8080 by default)")
parser.add_argument(
    "-mu", "--maxUsers",
    type=int,
    required=False,
    dest='max_users',
    help='Max users to be able to connect to the server (8 by default)'
)


def main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()

    SERVER_IP = args.server_ip if args.server_ip else '127.0.0.1'
    SERVER_PORT = args.server_port if args.server_port else 8080
    MAX_USERS = args.max_users if args.max_users else 8

    server = Server(SERVER_IP, SERVER_PORT, max_connected_users=MAX_USERS)
    server.run()

if __name__ == '__main__':
    main(parser)