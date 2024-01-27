import itertools

import vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from urllib.parse import urlencode
from datetime import datetime
from random import random
from providers.vk_group_api import VKBotAPI
from postgres_db.main import (
    add_user,
    add_offer,
    add_interest,
    show_offer,
    add_user_offer,
    get_offer_list,
)


class ServerBot:
    def __init__(self, api_token, group_id, api_id):
        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        self.vk_api = self.vk.get_api()
        self.group_id = group_id
        self.api_id = api_id
        self.user_info = []
        self.user_token = ""

    def send_msg(self, send_id, message, keyboard=None):
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

    def find_pair(
        self,
    ):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]
                if request == "Привет" or "Ghbdtn":
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Come with me if you want to date!",
                    )
                    keyboard_oauth = self.user_token_button(self.api_id)
                    self.send_msg(
                        event.obj.message["peer_id"],
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

                    age_range = range(age - 1, age + 2)
                    usr_token = self.get_user_token()
                    for usr_age in itertools.chain([age_range]):
                        user_inst = VKBotAPI(usr_token, city, usr_age, sex)
                        for users_tup in itertools.chain(user_inst.process_user_info()):
                            first_name, last_name, user_id, profile_link = users_tup
                            add_offer(first_name, last_name, profile_link, user_id)

                    break

                elif request == "Пока" or "Gjrf":
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Is it dead? Terminated.",
                    )
                else:
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Напиши 'Привет' и мы найдем тебе друзей, "
                        "'Пока' - если хочешь умереть в одиночестве",
                    )

    def get_user_info(self, user_id):
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

    def user_token_button(self, group_id):
        base_url = "https://oauth.vk.com/authorize"
        params = {
            "client_id": group_id,
            "redirect_uri": "https://oauth.vk.com/authorize",
            "display": "page",
            "scope": "notify,photos,notes,pages,wall,stories",
            "response_type": "token",
        }
        oauth_url = f"{base_url}?{urlencode(params)}"
        keyboard_settings = dict(one_time=True)
        keyboard_1 = VkKeyboard(**keyboard_settings)
        keyboard_1.add_openlink_button(label="Получить токен", link=oauth_url)

        return keyboard_1

    @staticmethod
    def show_friends_button():  # Кнопки для фото и прочего
        keyboard_settings = dict(one_time=False)
        keyboard_2 = VkKeyboard(**keyboard_settings)

        keyboard_2.add_button(
            label="Следующий",
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "show_next_user"},
        )

        keyboard_2.add_button(label="В Избранное", color=VkKeyboardColor.SECONDARY)
        keyboard_2.add_button(label="Заблокировать", color=VkKeyboardColor.SECONDARY)
        keyboard_2.add_line()

        keyboard_2.add_button(
            label="Показать избранных", color=VkKeyboardColor.POSITIVE
        )
        return keyboard_2

    def get_user_token(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.user_token = event.obj.message["text"]
                self.send_msg(
                    event.obj.message["peer_id"],
                    message="Спасибо, можете удалить сообщение с токеном в целях безопасноти",
                )  # messages.delete упорно не работает, может на свежую голову допилю
                self.send_msg(
                    event.obj.message["peer_id"],
                    message="Rotate the two locking cylinders counterclockwise. Do it. Now, open the port cover. "
                    "Pull to break the seal. Good. Now, remove the shock dampening assembly. "
                    "You can now access the CPU. Do you see it? "
                    "Hey, dont touch your laptop! I'm joking - just enter 'Старт' in the dialog window below",
                )
                return self.user_token

    def show_friends(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]
                if request == "Старт" or "Cnfhn":
                    keyboard_show = self.show_friends_button()
                    self.send_msg(
                        event.obj.message["peer_id"],
                        message="Я все нашел, тебе надо только пожмякать",
                        keyboard=keyboard_show,
                    )
                    self.choose_friends()
                else:
                    self.send_msg(event.obj.message["peer_id"], message="Введите Старт")

    def choose_friends(self):
        person_count = 1
        favorites_show_flag = False
        button_add_flag = False

        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = event.obj.message["text"]

                if request == "Следующий":
                    try:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message=show_offer(person_count)["person"],
                        )

                        user_inst = VKBotAPI(
                            self.user_token, age=None, hometown=None, sex=None
                        )
                        liked_pics_ids = user_inst.process_user_pics(
                            show_offer(person_count)["user_id"]
                        )
                        self.make_attachment(
                            liked_pics_ids,
                            event.obj.message["from_id"],
                            show_offer(person_count)["user_id"],
                        )
                    except:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="It's a room with a user you don't like. "
                            "Sorry I'm still struggling to find out a way how to pass it completely. "
                            "Just hit 'Следующий'",
                        )

                    if person_count < len(user_inst.process_user_info()):
                        person_count += 1
                    else:
                        person_count = 1

                    button_add_flag = True

                elif request == "Заблокировать":
                    if not button_add_flag:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="Cyborgs don't feel pain. I do. Don't do that again.",
                        )
                    else:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="Hasta la vista, baby",
                        )
                        add_user_offer(
                            person_count - 1, event.obj.message["peer_id"], "foe"
                        )

                elif request == "В Избранное":
                    if not button_add_flag:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="Cyborgs don't feel pain. I do. Don't do that again.",
                        )
                    else:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="I'll be back",
                        )
                        add_user_offer(
                            person_count - 1, event.obj.message["peer_id"], "friend"
                        )
                        favorites_show_flag = True

                elif request == "Показать избранных":
                    if not favorites_show_flag:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message="Cyborgs don't feel pain. I do. Don't do that again.",
                        )
                    else:
                        self.send_msg(
                            event.obj.message["peer_id"],
                            message=get_offer_list(event.obj.message["peer_id"]),
                        )

    def make_attachment(self, media_ids, user_id_hunter, user_id_prey):
        for media_id in media_ids:
            self.vk.method(
                "messages.send",
                {
                    "user_id": user_id_hunter,
                    "random_id": random(),
                    "message": "========",
                    "attachment": f"photo{user_id_prey}_{media_id}",
                },
            )
