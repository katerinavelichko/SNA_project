import vk_api
from vk_api.exceptions import VkApiError
import time
import json

ERRORS = []

def get_posts_from_group(vk, group_id, count=100):
    posts = []
    offset = 0

    while len(posts) < count:
        try:
            # запрос на получение постов с wall группы
            response = vk.wall.get(owner_id=f"-{group_id}", count=100, offset=offset)
            posts += response['items']

            if len(response['items']) < 100:
                break

            offset += 100  # переход к следующей порции постов
            time.sleep(1)  # чтобы избежать блокировки за частые запросы

        except VkApiError as e:
            print(f"Ошибка при запросе к API ВКонтакте: {e}")
            ERRORS.append(group_id)
            break
    res_posts = posts[:count]
    print(len(res_posts))
    return [{'group_id': group_id,
             'posts': [{'text': post['text'], 'likes': post['likes']['count']} for post in res_posts]}]


with open('group_ids_new.txt', 'r') as file:
    group_ids = list(map(int, file.readlines()))


def main():
    access_token = ''

    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()

    # group_ids = [62122883, 68123456]

    all_posts = []

    for group_id in group_ids:
        print(f"обработка группы {group_id}")
        posts = get_posts_from_group(vk, group_id)
        all_posts.extend(posts)

    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=4)

    print(f"всего {len(all_posts)} постов")

    if ERRORS:
        with open('errors.txt', 'w', encoding='utf-8') as error_file:
            for error_group_id in ERRORS:
                error_file.write(str(error_group_id))


if __name__ == "__main__":
    main()
