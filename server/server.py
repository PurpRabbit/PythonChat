import socket
import threading

from clientdata import ClientData, Message
from admintools import AdminTools, ServerAdminTools


class Server:
    """Class to create a server for text chat.

    Arguments:
        ip -- Internet Protocol address for connecting clients
        port -- port for receiving data from clients
        max_connected_users (default 8) -- max clients which server will handle
        max_connections_queue (default 1) -- specifies the number of unaccepted connections 
                that the system will allow before refusing new connections

    Attributes:
        server_socket -- socket.socket instance with socket.AF_INET, socket.SOCK_STREAM init arguments.
                AF_INET - Internet Protocol version 4 (IPv4)
                SOCK_STREAM - Transmission Control Protocol (TCP)
        clients -- list of active connected clients to server
        max_connected_users -- max clients which server can handle
        admintools -- AdminTools instance with 'clients' init argument.
                Execute client's commands (if client is admin)
        terminal -- Terminal instance with 'clients' init argument.
                Create interactive terminal which handle commands/messages from server side

    """
    def __init__(
        self, ip: str, port: int, max_connected_users: int=8, max_connections_queue: int = 1
    ) -> None:
        
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((ip, port))
        self._server_socket.listen(max_connections_queue)

        self._clients: list[ClientData] = []
        self._max_connected_users = max_connected_users
        self._admintools = AdminTools(self._clients)
        self._terminal = Terminal(self._clients)
    
    # ----------------------------- # 
    #  Client's connection methods  #
    # ----------------------------- #
    def _create_new_client(self, connection: socket.socket) -> None:
        """Create new ClientData instance if server is not full"""
        if self._max_clients_count_riched(connection):
            return

        client = ClientData(connection)
        self._verify_client(client)

    def _max_clients_count_riched(self, connection: socket.socket) -> bool:
        """Check count of connected users. 
           Broke connection if server is full and return 'True', otherwise return 'False'
        """
        if len(self._clients) >= self._max_connected_users:
            connection.sendall(b'Max users count reached')
            connection.close()
            return True
        return False
        
    def _verify_client(self, client: ClientData) -> None:
        """Close connection with user if nickname was reserved for another user 
           or leght of nickname is invalid, otherwise adding user to clients list"""

        if not self._nickname_is_unique(client):
            client.decline('Client with this name already exist')
            return
        if not 3 < len(client.nickname) <= 16:
            client.decline('Invalid nickname lenght')
            return

        self._add_new_client_to_list(client)
        client.accept()

    def _nickname_is_unique(self, client: ClientData) -> bool:
        """Check if new user set nickname that already have some connected user"""
        for cl in self._clients:
            if cl.nickname == client.nickname:
                return False
        return True

    def _add_new_client_to_list(self, client: ClientData) -> str:
        """Add client to clients list after verifying"""
        self._clients.append(client)
        return f'{client.nickname} connected'

    # ------------------- #
    #   Messages methods  #
    # ------------------- #
    def _send_message_to_all(self, message: str) -> str:
        """Send message to users from clients list"""
        for client in self._clients:
            if client.connection:
                try:
                    client.send_message(message)
                except OSError:
                    client.connection.close()
                    break

    def _clients_messages_checker(self) -> None:
        """Check new messages from all users"""
        while self._server_socket:
            for client in self._clients:
                if not client.messages_queue:
                    continue
                message = client.messages_queue.pop(0)
                self._process_message(message)    

    def _process_message(self, message: Message) -> None:
        """Check message type.
           If message is command, it will be executed in admintools (if client which sent message is admin),
           otherwise message will be sent to all users
        """
        if message.is_command and message.get_sender.admin:
            return self._admintools.execute(message)
        self._send_message_to_all(message.edited)

    def _start_messages_checker(self) -> None:
        """Create thread which checks new messages"""
        thread = threading.Thread(target=self._clients_messages_checker)
        thread.start()

    # ---------------- #
    #   Other methods  #
    # ---------------- #
    def _receive_connections(self) -> None:
        """Wait for new connection.
           Call create_new_client method if new connection was detected
        """
        while self._server_socket:
            try:
                connection, _ = self._server_socket.accept()
                self._create_new_client(connection)
            except (KeyboardInterrupt, OSError):
                self._stop_server()

    def run(self) -> None:
        """Start server"""
        self._start_messages_checker()
        self._terminal.start()
        self._receive_connections()


class Terminal:
    """Class to create server interactive terminal.
    
    Arguments:
        clients -- link to list of connected to server users

    Attributes:
        admintools -- instance with 'clients' init argument. Execute commands from server side 
    """
    def __init__(self, clients: list[ClientData]) -> None:
        self._admintools = ServerAdminTools(clients)
    
    def start(self):
        """Start terminal in new thread"""
        thread = threading.Thread(target=self._server_terminal_handler)
        thread.start()

    def _server_terminal_handler(self) -> None:
        """Wait for message/command input"""
        while True:
            try:
                message = input('~ ')
                self._process_terminal_message(Message(message))
            except EOFError:
                return

    def _process_terminal_message(self, message: Message) -> None:
        """Check message type. Execute if command
           !ToDo: send messages to users
        """
        if message.is_command:
            return self._admintools.execute(message)