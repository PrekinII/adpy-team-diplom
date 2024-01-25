from config import GROUP_TOKEN, GROUP_ID, API_ID
from providers.server_bot import ServerBot

bot_start = ServerBot(GROUP_TOKEN, GROUP_ID, API_ID)

if __name__ == "__main__":
    bot_start.find_pair()
    bot_start.show_friends()
