import vk
import time
import json
import requests
from pprint import pprint

# USER_ID = 'tim_leary'
USER_ID = 5030613
VK_TOKEN = 'd13e692be69592b09fd22c77a590dd34e186e6d696daa88d6d981e1b4e296b14acb377e82dcbc81dc0f22'


class NativeVk(object):

    def __init__(self, token):
        self.vk_token = token
        self.vk_url = 'https://api.vk.com/method/{method}'

    def call_api(self, method_name, args):
        url = self.vk_url.format(method=method_name)
        for err_count in range(0, 100):
            try:
                response = requests.post(url, args).json()
                result = response['response']
            except KeyError:
                err_result = {
                    'error_msg': response['error']['error_msg'],
                    'error_code': response['error']['error_code']
                }
                pprint(err_result)
            else:
                return result
        exit(1)

    def fetch_groups(self, user_id):
        args = {
            'access_token': self.vk_token,
            'user_id':  user_id
        }
        result = self.call_api('groups.get', args)
        return result

    def fetch_friends(self, user_id):
        args = {
            'access_token': self.vk_token,
            'user_id': user_id
        }
        result = self.call_api('friends.get', args)
        return result

    def is_member(self, group_id, user_ids):
        args = {
            'group_id': group_id,
            'user_ids': ','.join(str(uid) for uid in user_ids),
            'access_token': self.vk_token
        }
        result = self.call_api('groups.isMember', args)
        return result

    def fetch_by_id(self, group_ids, fields):
        args = {
            'group_ids': ','.join(str(gid) for gid in group_ids),
            'fields': fields,
            'access_token': self.vk_token
        }
        result = self.call_api('groups.getById', args)
        return result

    def fetch_user_id(self, user_name):
        args = {
            'user_ids': user_name,
            'access_token': self.vk_token
        }
        result = self.call_api('users.get', args)
        result = result[0]['uid']
        return result


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
                print('.')
                bad_groups.append(group)
                break
    for group in bad_groups:
        groups.remove(group)
    return groups


def check_member_native(vk_api, user_ids, groups):
    bad_groups = set()
    for group in groups:
        # time.sleep(0.5)
        result = vk_api.is_member(group_id=group, user_ids=user_ids)
        for item in result:
            if item['member']:
                print('.')
                bad_groups.add(group)
                break
    # for group in bad_groups:
    #     groups.remove(group)
    groups = groups - bad_groups
    return groups


def result_data_generator(response):
    for item in response:
        group = {
            'gid': item['gid'],
            'members_count': item['members_count'],
            'name': item['name']
        }
        yield group


def dump_to_json(response):
    with open('groups.json', 'w', encoding='utf-8') as json_file:
        data = json.dumps(list(result_data_generator(response)),
                          indent=2, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        json_file.write(data)


def new_method():

    vk_api = get_auth_api(VK_TOKEN)
    friends = vk_api.friends.get(user_id=USER_ID)
    groups = vk_api.groups.get(user_id=USER_ID)
    while True:
        if not friends:
            break
        groups = check_member(vk_api, friends[:500], groups)
        friends = friends[500:]
    response = vk_api.groups.getById(group_ids=groups,
                                     fields='members_count')
    pprint(response)
    dump_to_json(response)


def old_method():
    native_vk = NativeVk(VK_TOKEN)
    vk_user = input('Введите имя пользователя для обработки данных: ')
    try:
        int(vk_user)
    except ValueError:
        vk_user = native_vk.fetch_user_id(vk_user)

    groups_native = set(native_vk.fetch_groups(vk_user))
    friends_native = native_vk.fetch_friends(vk_user)
    step = 500
    for i in range(0, len(friends_native), step):
        groups_native = check_member_native(native_vk, friends_native[i: i + step], groups_native)
    response = native_vk.fetch_by_id(group_ids=groups_native, fields='description,'
                                                                     'members_count')
    pprint(response)
    dump_to_json(response)

if __name__ == '__main__':
    # new_method()
    old_method()
