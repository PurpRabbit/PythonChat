from typing import NamedTuple, Callable

from clientdata import ClientData, Message


class AdminCommandResult(NamedTuple):
    """Class that will be returned after command execution.

    Attributes:
        completed -- 'True' if request was successfully completed, otherwise 'False'
        text -- covered message after execution
    """
    completed: bool
    text: str

    def __repr__(self):
        return f"{self.completed} -- {self.text}"


class ServerAdminTools:
    """Class to process commands from server side.

    Attributes:
        clients -- link to list of connected to server users
        commands -- dict of commands, each command (key) corresponds to an action (value) 
    """
    def __init__(self, clients: list[ClientData]) -> None:
        self._clients = clients
        self._commands = {
            "/kick": self._kick, 
            "/makeadmin": self.__makeadmin, 
            "/removeadmin": self.__removeadmin
            }

    # ------------------- #
    #   Commands methods  #
    # ------------------- #
    def __removeadmin(self, client: ClientData) -> AdminCommandResult: 
        if client.admin:
            client.admin = False
            return AdminCommandResult(True, f'Admin status was removed from {client.nickname}')
        return AdminCommandResult(False, f'{client.nickname} is not admin')

    
    def __makeadmin(self, client: ClientData) -> AdminCommandResult:
        if not client.admin:
            client.admin = True
            return AdminCommandResult(True, f'{client.nickname} become admin')
        return AdminCommandResult(False, f'{client.nickname} is admin already')
    
    def _kick(self, client: ClientData) -> AdminCommandResult:
        if client.connection and not client.admin:
            client.connection.close()
            self._clients.remove(client)
            return AdminCommandResult(True, f'{client.nickname} was kicked')
        return AdminCommandResult(False, f'Client does not exists or it is admin')

    # ---------------- #
    #   Other methods  #
    # ---------------- #
    def _client_exists(self, nickname: str) -> ClientData | bool:
        for client in self._clients:
            if client.nickname == nickname:
                return client
        return False

    def _command_executor(self, action: Callable[[str], AdminCommandResult], nickname: str) -> AdminCommandResult:
        client = self._client_exists(nickname)
        if client is False:
            return AdminCommandResult(False, 'Invalid arguments')
        return action(client)

    def _validate_command(self, command: str) -> tuple[Callable, str] | None:
        try:
            command, nickname = command.split()[:2]
        except IndexError:
            return
        
        if command in self._commands:
            return (self._commands.get(command), nickname)

    def execute(self, message: Message) -> AdminCommandResult:
        if (execution_data:=self._validate_command(message.text)) is None:
            return AdminCommandResult(False, 'Invalid command')
        return self._command_executor(*execution_data)


class AdminTools(ServerAdminTools):
    """Class to process commands from clients"""
    def __init__(self, clients: list[ClientData]) -> None:
        self._commands = {
            "/kick": self._kick
            }
        self._clients = clients

    