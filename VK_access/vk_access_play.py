from VK_access.vk_access_creds import vk_token, vk_token_group
from VK_access.vk_group_api import VKBotAPI
from VKinder_DB.main import add_offer
# 313568452
if __name__ == "__main__":
    vk_inst = VKBotAPI(
        vk_token, "Щелково", 0, 1
    )  # make exception handler if user profile is private
    vk_inst.process_user_pics(5469708)

# if __name__ == "__main__":  # prekinii only
#     vk_inst = VKBotAPI(
#         'vk_token', "Щелково", 0, 1
#     )  # make exception handler if user profile is private
#     print(vk_inst.process_user_pics(3499455)) #5469708 51754857
#     print(vk_inst.process_user_info())

