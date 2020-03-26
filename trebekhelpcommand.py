from discord.ext.commands import DefaultHelpCommand

class TrebekHelpCommand(DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.no_category = "Discord Jeopardy"