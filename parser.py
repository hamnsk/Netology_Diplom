import vk
import time
import json
from pprint import pprint

USER_ID = 5030613
VK_TOKEN = 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22'


def get_auth_api(access_token):
    session = vk.Session(access_token=access_token)
    return vk.API(session)


def check_member(vk_api, user_ids, groups):
    bad_groups = []
    for group in groups:
        time.sleep(1)
        result = vk_api.groups.isMember(group_id=group, user_ids=user_ids)
        for item in result:
            if item['member']:
                print('Один из пользователей состоит в группе {} следовательно удаляемм ее из списка'.format(group))
                bad_groups.append(group)
                break
    for group in bad_groups:
        groups.remove(group)
    return groups


def main():
    vk_api = get_auth_api(VK_TOKEN)
    friends = vk_api.friends.get(user_id=USER_ID)
    groups = vk_api.groups.get(user_id=USER_ID)
    while True:
        if not friends:
            break
        groups = check_member(vk_api, friends[:500], groups)
        friends = friends[500:]
    response = vk_api.groups.getById(group_ids=groups,
                                     fields='city,'
                                            'country,'
                                            'place,'
                                            'description,'
                                            'wiki_page,'
                                            'members_count,'
                                            'counters,'
                                            'start_date,'
                                            'finish_date,'
                                            'can_post,'
                                            'can_see_all_posts,'
                                            'activity,'
                                            'status,'
                                            'contacts,'
                                            'links,'
                                            'fixed_post,'
                                            'verified,'
                                            'site,'
                                            'ban_info,'
                                            'cover')
    pprint(response)
    with open('result.json', 'w', encoding='utf-8') as json_file:
        data = json.dumps(response,
                          indent=2,
                          sort_keys=True,
                          separators=(',', ':'),
                          ensure_ascii=False)
        json_file.write(data)


if __name__ == '__main__':
    main()
