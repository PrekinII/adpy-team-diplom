from VK_access.vk_access_creds import vk_token, vk_token_group
from VK_access.vk_group_api import VKBotAPI

# 313568452
if __name__ == "__main__":
    vk_inst = VKBotAPI(vk_token, "Щелково", 0, 1)  # make exception handler if user profile is private
    vk_inst.process_user_pics(5469708)
