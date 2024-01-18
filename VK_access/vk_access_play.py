from VK_access.vk_access_creds import vk_token, vk_token_group
from VK_access.vk_group_api import VKBotAPI
#313568452
if __name__ == "__main__":
    vk_inst = VKBotAPI(vk_token, "Щелково", 25, 1)
    vk_inst.get_user_info()
