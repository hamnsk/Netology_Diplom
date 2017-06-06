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
        result = requests.post(url, args)
        return result.json()['response']

    def fetch_groups(self, user_id):
        args = dict()
        args['access_token'] = self.vk_token
        args['user_id'] = user_id
        try:
            result = self.call_api('groups.get', args)
        except KeyError:
            time.sleep(3)
            result = self.call_api('groups.get', args)
        return result

    def fetch_friends(self, user_id):
        args = dict()
        args['access_token'] = self.vk_token
        args['user_id'] = user_id
        try:
            result = self.call_api('friends.get', args)
        except KeyError:
            time.sleep(3)
            result = self.call_api('friends.get', args)
        return result

    def is_member(self, group_id, user_ids):
        args = dict()
        args['group_id'] = group_id
        args['user_ids'] = ','.join(str(uid) for uid in user_ids)
        args['access_token'] = self.vk_token
        try:
            result = self.call_api('groups.isMember', args)
        except KeyError:
            time.sleep(3)
            result = self.call_api('groups.isMember', args)
        return result

    def fetch_by_id(self, group_ids, fields):
        args = dict()
        args['group_ids'] = ','.join(str(gid) for gid in group_ids)
        args['fields'] = fields
        args['access_token'] = self.vk_token
        try:
            result = self.call_api('groups.getById', args)
        except KeyError:
            time.sleep(3)
            result = self.call_api('groups.getById', args)
        return result

    def fetch_user_id(self, user_name):
        args = dict()
        args['user_ids'] = user_name
        args['access_token'] = self.vk_token
        try:
            result = self.call_api('users.get', args)
        except KeyError:
            time.sleep(3)
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
    bad_groups = []
    for group in groups:
        time.sleep(1)
        result = vk_api.is_member(group_id=group, user_ids=user_ids)
        for item in result:
            if item['member']:
                print('.')
                bad_groups.append(group)
                break
    for group in bad_groups:
        groups.remove(group)
    return groups


def dump_to_json(response):
    with open('groups.json', 'w', encoding='utf-8') as json_file:
        data_list = []
        for item in response:
            group = dict()
            group['gid'] = item['gid']
            group['members_count'] = item['members_count']
            group['name'] = item['name']
            data_list.append(group)

        data = json.dumps(data_list, indent=2, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
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
                                     fields='description,'
                                            'members_count')
    pprint(response)
    dump_to_json(response)


def old_method():
    native_vk = NativeVk(VK_TOKEN)
    vk_user = input('Введите имя пользователя для обработки данных: ')
    try:
        int(vk_user)
    except ValueError:
        vk_user = native_vk.fetch_user_id(vk_user)

    groups_native = native_vk.fetch_groups(vk_user)
    friends_native = native_vk.fetch_friends(vk_user)
    step = 500
    for i in range(0, len(friends_native), step):
        groups_native = check_member_native(native_vk, friends_native[i: i + step], groups_native)
    # while True:
    #     if not friends_native:
    #         break
    #     groups_native = check_member_native(native_vk, friends_native[:500], groups_native)
    #     friends_native = friends_native[500:]

    response = native_vk.fetch_by_id(group_ids=groups_native, fields='description,'
                                                                     'members_count')
    pprint(response)
    dump_to_json(response)

if __name__ == '__main__':
    # new_method()
    old_method()
