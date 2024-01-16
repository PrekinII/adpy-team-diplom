import vk_api
from random import random
from itertools import chain
from pprint import pprint


class VKBotAPI:
    def __init__(self, api_token: str, hometown: str, age: int, sex: int):
        self.api_token = api_token
        self.hometown = hometown
        self.age = age
        self.sex = sex
        self.user_init_link = "https://vk.com/id"
        self.vk_session = vk_api.VkApi(token=self.api_token)

    @staticmethod
    def likes_finder(user_pics) -> list:
        likes_cnt = []
        for pic in chain.from_iterable([user_pics["items"]]):
            max_likes = str(pic["likes"]["count"])
            likes_cnt.append(int(max_likes))
        likes_cnt = sorted(likes_cnt)[-3:]

        return likes_cnt

    def get_user_pics(self, user_id):
        user_pics = self.vk_session.method(
            "photos.getAll", {"owner_id": user_id, "extended": True}
        )

        pics_ids = []
        for likes in user_pics["items"]:
            pics_selection = [
                x
                for x in [likes["likes"]["count"]]
                if x in self.likes_finder(user_pics)
            ]
            if pics_selection:
                # max_pics_size = max(likes["sizes"], key=lambda x: x.get("height", 0) + x.get("width", 0))
                pics_ids.append(likes["id"])

        return pics_ids

    def make_attachment(self, media_id=456239116, user_id=5469708):
        # for media_id in media_ids:
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
        for usr_lnk in user_search_res["items"]:
            get_pics_ids = self.get_user_pics(
                usr_lnk["id"]
            )  # implement below in self.make_attachment()
            user_data = [
                usr_lnk["first_name"],
                usr_lnk["last_name"],
                self.user_init_link + str(usr_lnk["id"]),
                self.make_attachment(),  # here
            ]
            users_main_data.append(user_data)
        pprint(users_main_data)
        return users_main_data
