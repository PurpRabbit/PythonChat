import socket
import threading

from settings import COMMAND_PREFIX


class ClientData:
    """Class to manage new clients.
       
    Arguments:
        connection -- socket.socket instance of client connection.
    
    Attributes:
        connection -- handle client's connection
        admin (default 'False') -- represents clients status on server ('True' if client is administrator, otherwise 'False') 
        nickname -- client's name
        messages_queue -- list of Message instances. Messages which were received from client
    """
    def __init__(self, connection: socket.socket) -> None:
        self.connection = connection
        self.admin = False
        self.nickname = self._get_nickname()
        self.messages_queue: list[Message] = []

    def _connection_handler(self) -> str:
        """Handle connection with client"""
        while self.connection:
            try:
                self._get_message_from_client()
            except (OSError, ConnectionAbortedError, ConnectionResetError):
                return f'{self.nickname} disconnected'

    def _get_message_from_client(self) -> None:
        """Receive message from client"""
        message = self.connection.recv(1024)
        if not message:
            return
        self._add_message_to_queue(message.decode())

    def _add_message_to_queue(self, message: str) -> None:
        """Create Message instance and add it to messages_queue list"""
        msg = Message(message, sender=self)
        self.messages_queue.append(msg)

    def _create_new_connection_thread(self) -> threading.Thread:
        """Create new thread to handle connection with client"""
        self.connection_thread = threading.Thread(target=self._connection_handler)
        self.connection_thread.start()

    def _get_nickname(self) -> str:
        """Receive nickname from client"""
        while True:
            try:
                nickname = self.connection.recv(64).decode()
                if nickname:
                    return nickname
            except (OSError, ConnectionAbortedError, ConnectionResetError):
                break
    
    def send_message(self, msg: str) -> None:
        self.connection.sendall(msg.encode())

    def decline(self, reason: str) -> None:
        """Close connection if client was not verified and send a reason to client"""
        self.connection.sendall(f'{reason}'.encode())
        self.connection.close()

    def accept(self) -> None:
        """Send 'True' if client was successfully verified"""
        self.connection.sendall(b'True')
        self._create_new_connection_thread()


class Message:
    """Class to create client's message instance.

    Attributes:
        msg -- client's message
        sender -- ClientData instance
        is_command -- represents message type. 'True' if message is command, otherwise 'False'
    """
    def __init__(self, msg: str, sender: ClientData = None) -> None:
        self._msg = msg
        self._sender = sender
        self._is_command = True if self._msg.startswith(COMMAND_PREFIX) else False

    @property
    def text(self) -> str:
        return self._msg

    @property
    def is_command(self) -> bool:
        return self._is_command

    @property
    def get_sender(self) -> ClientData:
        return self._sender

    @property
    def edited(self) -> str:
        return f"{self._sender.nickname}: {self._msg}"

    def __repr__(self) -> str:
        return self.edited