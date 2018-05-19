

class QueueSettings:
    def __init__(self):
        self.commands = {}


    def set_command_error_handling(self, command, cont, retry):
        self.commands[command] = {
            'continue': cont,
            'retry': retry
        }

    def get_command_error_handling(self, command):
        return self.commands.get(command, {
            'continue': False,
            'retry': 0
        })

