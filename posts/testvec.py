import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import json

# posts = [
#     "пост про путешествия. в париже эйфелева башня, в риме колизей, лететь туда всего по 5 часов",
#     "еще один пост для путешественников. нужны целые сутки чтобы добраться до китая, в самолете вы проведете 11 часов",
#     "Сегодня я попробовал новый рецепт пасты с томатным соусом. Получилось очень вкусно! Рекомендую всем любителям итальянской кухни.",
#     "На выходных посетил выставку современного искусства. Некоторые работы были действительно впечатляющими, а другие — странными. Искусство всегда вызывает эмоции!",
#     "Собираюсь в путешествие в горы. Хочу насладиться природой и отдохнуть от городской суеты. Есть советы по маршрутам?"
# ]

with open("posts.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# номер группы и номер поста (через _) соответствует посту
post_dict = {}
posts = []
for block in data:
    post_dict.update({f"{block['group_id']}_{i}": post for i, post in enumerate(block['posts'], start=1)})
    posts.extend([b['text'] for b in block['posts']])

# posts = data

# номер поста соответствует посту
# post_dict = {i: post for i, post in enumerate(posts, start=1)}


tokenized_posts = [word_tokenize(post.lower()) for post in posts]
model = Word2Vec(sentences=tokenized_posts, vector_size=100, window=5, min_count=1, workers=4)


#  получение эмбединга поста (усреднение эмбедингов слов)
def get_embedding(post):
    words = word_tokenize(post.lower())
    word_vectors = [model.wv[word] for word in words if word in model.wv]
    return np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.vector_size)


embeddings = np.array([get_embedding(post) for post in posts])
similarity_matrix = cosine_similarity(embeddings)
similarity_df = pd.DataFrame(similarity_matrix, index=range(1, len(posts) + 1), columns=range(1, len(posts) + 1))

print(similarity_df)

print("Словарь постов:")
for number, text in post_dict.items():
    print(f"{number}: {text}")
