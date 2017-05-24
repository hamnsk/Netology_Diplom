import vk
import time
from pprint import pprint

USER_ID = 5030613
VK_TOKEN = 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22'


def get_auth_api(access_token):
    session = vk.Session(access_token=access_token)
    return vk.API(session)


def check_member(vk_api, user_id, groups):
    for group in groups:
        time.sleep(1)
        print('Проверяем пользователя {} в группе {}'.format(user_id, group))
        result = vk_api.groups.isMember(group_id=group, user_id=user_id)
        print('Результат членства {}'.format(result))
        if result:
            print('Пользователь {} состоит в группе {} следовательно удаляемм ее из списка'.format(user_id, group))
            groups.remove(group)
    return groups


def main():
    vk_api = get_auth_api(VK_TOKEN)
    friends = vk_api.friends.get(user_id=USER_ID)
    groups = vk_api.groups.get(user_id=USER_ID)
    for friend in friends:
        print(len(groups))

        groups = check_member(vk_api, friend, groups)
    pprint(groups)


if __name__ == '__main__':
    main()
