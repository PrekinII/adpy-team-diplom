import itertools

import vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from urllib.parse import urlencode
from datetime import datetime


from VK_access.vk_group_api import VKBotAPI
from VKinder_DB.main import add_user, add_offer, add_interest, show_offer


class Server_bot:
    def __init__(self, api_token, group_id, api_id):

        self.vk = vk_api.VkApi(token=api_token)  # Для использования Long Poll
        self.long_poll = VkBotLongPoll(self.vk, group_id)  # Для Long Poll Api
        self.vk_api = self.vk.get_api()  # Для методов ВК апи
        self.group_id = group_id
        self.api_id = api_id
        self.user_info = []  # Информация о юзере
        self.user_token = ""  # Токен юзера

    def send_msg(
        self, send_id, message, keyboard=None
    ):  # send_id он же peer_id, он же id пользователя, которому отвечаем
        if keyboard:
            self.vk_api.messages.send(
                peer_id=send_id,
                message=message,
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
            )
        else:
            self.vk_api.messages.send(
                peer_id=send_id,
                message=message,
                random_id=get_random_id(),
            )

    # def test_send(self):  # Тест отправки сообщений
    #     self.send_msg(ID пользователя, "Я живой!!! Я могу писать тебе сообщения")

    def find_pair(
        self,
    ):  # При получении сообщения от пользователя предлагаем найти пару
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]
                if request == "Привет" or "Ghbdtn":
                    self.send_msg(event.obj.message["peer_id"], message="Хелоу")
                    keyboard_oauth = self.user_token_button(self.api_id)
                    self.send_msg(
                        event.obj.message[
                            "peer_id"
                        ],  # Отправляем пользователю кнопку на токен
                        message="Получите и отправьте нам токен",
                        keyboard=keyboard_oauth,
                    )

                    user_id = event.obj.message["from_id"]
                    sex, age, city = self.get_user_info(user_id)
                    if sex == 1:
                        sex = 2
                    elif sex == 2:
                        sex = 1
                    else:
                        sex = 0

                    user_inst = VKBotAPI(self.get_user_token(), city, age, sex)
                    for users_tup in itertools.chain(user_inst.process_user_info()):
                        first_name, last_name, profile_link = users_tup
                        add_offer(user_id, first_name, last_name, profile_link)
                    break

                elif request == "Пока" or "Gjrf":
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Жаль, но ты умрешь в одиночестве",
                    )
                else:
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Напиши 'Привет' и мы найдем тебе друзей, "
                        "'Пока' - если хочешь умереть в одиночестве",
                    )

    def get_user_info(self, user_id):  # Получаем инфу о пользователе

        self.user_info = self.vk_api.users.get(
            user_ids=user_id, fields=("city", "sex", "bdate", "interests")
        )
        user_id, sex, city, bdate, interest = [
            (
                x.get("id", None),
                x.get("sex", None),
                x.get("city", {}).get("title", None),
                x.get("bdate", None),
                x.get("interests"),
            )
            for x in self.user_info
        ][0]

        day, month, year = map(int, bdate.split("."))
        bdate = datetime(year, month, day)
        age = int((datetime.today() - bdate).days // 365.25)

        add_user(user_id, sex, age, city)  # filling db "user" table
        add_interest(interest)
        return sex, age, city

    def user_token_button(self, group_id):  # Создаем кнопку запроса токена
        base_url = "https://oauth.vk.com/authorize"
        params = {
            "client_id": group_id,
            "redirect_uri": "https://oauth.vk.com/authorize",
            "display": "page",
            "scope": "photos",
            "response_type": "token",
        }
        oauth_url = f"{base_url}?{urlencode(params)}"
        keyboard_settings = dict(one_time=True)
        keyboard_1 = VkKeyboard(**keyboard_settings)
        keyboard_1.add_openlink_button(label="Получить токен", link=oauth_url)

        # print(oauth_url)
        # print(group_id)
        return keyboard_1

    def show_friends_button(self):  # Кнопки для фото и прочего
        keyboard_settings = dict(one_time=False)
        keyboard_2 = VkKeyboard(**keyboard_settings)
        keyboard_2.add_button(
            label="Следующий",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "show_next_user"},
        )
        keyboard_2.add_button(label="В избранные", color=VkKeyboardColor.SECONDARY)
        keyboard_2.add_line()
        keyboard_2.add_button(
            label="Показать избранных", color=VkKeyboardColor.POSITIVE
        )
        return keyboard_2

    def get_user_token(self):  # Вылавливаем токен от юзера и ищем людей
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.user_token = event.obj.message["text"]
                # print(user_token)
                # print(event.obj.message)
                self.send_msg(
                    event.obj.message["peer_id"],
                    message="Спасибо, можете удалить сообщение с токеном в целях безопасноти",
                )  # messages.delete упорно не работает, может на свежую голову допилю
                self.send_msg(
                    event.obj.message["peer_id"],
                    message="Введите Старт, чтобы продолжить",
                )
                return self.user_token

    def show_friends(self):  # Отправлем вторую клавиатуру
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]
                if request == "Старт":
                    keyboard_show = self.show_friends_button()
                    self.send_msg(
                        event.obj.message["peer_id"],  # Отправляем кнопки
                        message="Я все нашел, тебе надо только пожмякать",
                        keyboard=keyboard_show,
                    )
                    self.choose_friends()

                else:
                    self.send_msg(event.obj.message["peer_id"], message="Введите Старт")

    def choose_friends(self):  # Обрабатываем кнопки и отправляем инфу
        person_count = 1
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]
                # print(request)

                if request == "Следующий":

                    #add_offer(3499455, 383632700, 'Ксения', 'Тарновицкая', 'https://vk.com/id383632700')  # Тест на запись таблицу
                    self.send_msg(
                        event.obj.message[
                            "peer_id"
                        ],  # Сюда должна прилететь информация (Возможно фотки придется отправить дополнительным письмом
                        message=show_offer(person_count), #"-имя, фамилия\n-ссылка на профиль-\n-три фотографии"
                    )
                    person_count += 1
                    print(person_count)
                elif request == "В избранные":
                    self.send_msg(
                        event.obj.message["peer_id"],  # Добавляем в избранные
                        message="Добавлен в избранные",
                    )
                elif request == "Показать избранных":
                    self.send_msg(
                        event.obj.message["peer_id"],  # Отправляем список избранных
                        message="Вот Вам куча информации",
                    )
                    # print(request)
