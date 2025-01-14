import vk_api
from itertools import chain

from decorators.api_slicer_dec import api_slicer_decorator


class VKBotAPI:
    def __init__(self, api_token: str, hometown, age, sex):
        self.api_token = api_token
        self.hometown = hometown
        self.age = age
        self.sex = sex
        self.user_init_link = "https://vk.com/id"
        self.vk_session = vk_api.VkApi(token=self.api_token)

    def api_slicer(
        self,
        method_name: str,
        method_val_name="owner_id",
        value="user_id",
        sub_dict="items",
    ) -> int:
        call_slice_length = len(
            self.vk_session.method(method_name, {method_val_name: value})[sub_dict]
        )

        return call_slice_length

    @api_slicer_decorator("photos.getAll")
    def get_user_pics(self, offset, user_id):
        user_pics = self.vk_session.method(
            "photos.getAll",
            {"owner_id": user_id, "offset": offset, "extended": True},  # add url
        )

        return user_pics

    def process_user_pics(self, user_id):
        raw_user_pics = self.get_user_pics(user_id)
        all_pics = []
        for pic in raw_user_pics:
            pic_id = pic["id"]
            likes_count = pic["likes"]["count"]
            all_pics.append([pic_id, likes_count])

        liked_pics_ids = sorted(all_pics, key=lambda x: x[1])[-3:]
        liked_pics_ids = [x[0] for x in chain.from_iterable([liked_pics_ids])]

        return liked_pics_ids

    @api_slicer_decorator("users.search")
    def get_user_info(self, offset):
        user_search = self.vk_session.method(
            "users.search",
            {
                "hometown": self.hometown,
                "sex": self.sex,
                "age": self.age,
                "has_photo": 1,
                "offset": offset,
            },
        )

        return user_search

    def process_user_info(self):
        user_search_res = self.get_user_info()

        users_main_data = []
        for usr_lnk in chain.from_iterable([user_search_res]):
            user_data = (
                usr_lnk["first_name"],
                usr_lnk["last_name"],
                usr_lnk["id"],
                self.user_init_link + str(usr_lnk["id"]),
            )
            users_main_data.append(user_data)

        return users_main_data
