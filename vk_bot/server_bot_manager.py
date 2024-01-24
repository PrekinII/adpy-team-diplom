from config import GROUP_TOKEN, GROUP_ID, API_ID
from server_bot import Server_bot

bot_start = Server_bot(GROUP_TOKEN, GROUP_ID, API_ID)


if __name__ == "__main__":
    bot_start.find_pair()  # Функция завершит работу как только получит инфу и токен пользователя
    #print(server_bot_info_token.user_info)
    # print(server_bot_info_token.user_token)
    bot_start.show_friends()  # Отправляет кнопки, потом инфу по кнопкам
