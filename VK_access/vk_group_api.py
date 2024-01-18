import vk_api
from random import random
from itertools import chain, count
from pprint import pprint


class VKBotAPI:
    def __init__(self, api_token: str, hometown: str, age: int, sex: int):
        self.api_token = api_token
        self.hometown = hometown
        self.age = age
        self.sex = sex
        self.user_init_link = "https://vk.com/id"
        self.vk_session = vk_api.VkApi(token=self.api_token)

    def get_user_pics(self, user_id):

        return_values_length = len(self.vk_session.method(
            "photos.getAll", {"owner_id": user_id}
        )["items"])

        all_pics = []
        for offset in count(0, return_values_length):
            user_pics = self.vk_session.method(
                "photos.getAll", {"owner_id": user_id, "offset": offset, "extended": True}
            )

            if not user_pics["items"]:
                break
            all_likes = [[x["id"], x["likes"]["count"]] for x in user_pics["items"]]
            all_pics.extend(all_likes)

        liked_pics_ids = sorted(all_pics, key=lambda x: x[1])[-3:]
        liked_pics_ids = [x[0] for x in chain.from_iterable([liked_pics_ids])]
        return liked_pics_ids

    # media_id = 456239116, user_id = 5469708 user_id=1046913
    def make_attachment(self, media_ids, user_id=5469708):
        for media_id in media_ids:
            self.vk_session.method(
                "messages.send",
                {
                    "user_id": user_id,
                    "random_id": random(),
                    "attachment": f"photo{user_id}_{media_id}",
                },
            )

    def get_user_info(self):
        user_search_res = self.vk_session.method(
            "users.search",
            {
                "hometown": self.hometown,
                "sex": self.sex,
                "age": self.age,
                "has_photo": 1,
            },
        )

        users_main_data = []
        for usr_lnk in chain.from_iterable([user_search_res["items"]]):
            get_pics_ids = self.get_user_pics(
                usr_lnk["id"]
            )
            pprint(get_pics_ids)
            user_data = [
                usr_lnk["first_name"],
                usr_lnk["last_name"],
                self.user_init_link + str(usr_lnk["id"]),
            ]
            # self.make_attachment(get_pics_ids)
            users_main_data.append(user_data)
        pprint(users_main_data)

        return users_main_data
