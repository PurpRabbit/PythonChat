import sys
from typing import Callable

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from designerinterface.designerchatinterface import Ui_MainWindow as Ui_ChatWindow
from designerinterface.designerlogininterface import Ui_MainWindow as Ui_LoginWindow
from threadutil import run_in_main_thread


class LoginInterface(QMainWindow, Ui_LoginWindow):
    def __init__(self, login_button_signal: Callable):
        super(LoginInterface, self).__init__()
        self.setupUi(self)

        self._set_login_button_signal(login_button_signal)

    def _set_login_button_signal(self, func: Callable) -> None:
        """DEBUG"""
        self.input_ip_address.setText('127.0.0.1:8080')
        
        self.login_button.clicked.connect(func)

    def set_invalid_nickname_message(self, message: str) -> None:
        self.input_nickname.setText(f'{message}')

    def set_invalid_ip_address_message(self, message: str) -> None:
        self.input_ip_address.setText(f'{message}')
    
    def get_user_input(self) -> tuple[str, str]:
        address = self.input_ip_address.text()
        nickname = self.input_nickname.text()
        return (address, nickname)


class ChatInterface(QMainWindow, Ui_ChatWindow):
    MESSAGES_FONT_SIZE = 10

    def __init__(self, send_message_signal: Callable):
        super(ChatInterface, self).__init__()
        self.setupUi(self)
        #self.client_socket: socket.socket = None
        self._set_send_message_button_signal(send_message_signal)

        #chat settings
        self.chatfont = QtGui.QFont()
        self.chatfont.setPointSize(self.MESSAGES_FONT_SIZE)

    def clear_message_input(self) -> None:
        self.input_message.setText('')
    
    def get_message_from_input(self) -> str:
        message = self.input_message.text()
        self.clear_message_input()
        return message

    def display_new_message(self, msg: str) -> None:
        message = self._prepare_message(msg)
        self.chat_list.addItem(message)

    def _prepare_message(self, msg: str) -> QListWidgetItem:
        message = QListWidgetItem()
        message.setFont(self.chatfont)
        message.setText(msg)
        return message
        
    def _set_send_message_button_signal(self, func: Callable) -> None:
        self.send_message_button.clicked.connect(func)
        self.input_message.returnPressed.connect(func)     


class InterfaceControl:
    def __init__(self) -> None:
        self._app = QApplication(sys.argv)

    def execute_application(self) -> None:
        sys.exit(self._app.exec())

    def close_current_window(self) -> None:
        self.current_interface.close()

    def draw_login_interface(self, on_login_button_pressed: Callable) -> None:
        self.current_interface = LoginInterface(on_login_button_pressed)
        self.current_interface.show()

    def draw_chat_interface(self, on_send_message_button_pressed: Callable) -> None:
        self.close_current_window()
        self.current_interface = ChatInterface(on_send_message_button_pressed)
        self.current_interface.show()