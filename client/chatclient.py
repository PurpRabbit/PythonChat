import socket
import threading

from interfacecontrol import InterfaceControl


class Client:
    def __init__(self) -> None:
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _start_login_window(self) -> None:
        self._userinterface = InterfaceControl()
        self._userinterface.draw_login_interface(on_login_button_pressed=self._connect_to_server)
        self._userinterface.execute_application()

    def _start_chat_window(self) -> None:
        message_receiver_thread = threading.Thread(target=self._connection_loop)
        message_receiver_thread.start()

        self._userinterface.draw_chat_interface(on_send_message_button_pressed=self._send_message_to_server)

    def _connect_to_server(self) -> None:
        address, nickname = self._userinterface.current_interface.get_user_input()

        if not self._try_make_connection(address):
            return
        if (accept:=self._send_nickname_to_server(nickname)) == 'True':
            self._start_chat_window()
            return

        self._userinterface.current_interface.set_invalid_nickname_message(accept)

    def _try_make_connection(self, address: str) -> bool:
        try:
            ip, port = address.split(':')
            self._client_socket.connect((ip, int(port)))
        except ValueError:
            self._userinterface.current_interface.set_invalid_ip_address_message('Invalid address format')
            return False
        except (ConnectionRefusedError, TimeoutError):
            self._userinterface.current_interface.set_invalid_ip_address_message('Invalid ip address')
            return False
        return True

    def _send_nickname_to_server(self, nickname: str) -> str:
        self._client_socket.sendall(nickname.encode())
        server_accept = self._client_socket.recv(1024).decode()
        return server_accept

    def _send_message_to_server(self) -> None:
        message = self._userinterface.current_interface.get_message_from_input()
        self._client_socket.sendall(message.encode())

    def _receive_message_from_server(self) -> None:
        message = self._client_socket.recv(1024)
        if message:
            self._userinterface.current_interface.display_new_message(message.decode())

    def _connection_loop(self) -> str:
        while True:
            try:
                self._receive_message_from_server()
            except (OSError, ConnectionResetError):
                self._client_socket.close()
                self._userinterface.close_current_window()
                break

    def start(self) -> None:
        self._start_login_window()
        