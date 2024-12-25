import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import json
import nltk
import pymorphy2
from nltk.stem import WordNetLemmatizer

# nltk.download('stopwords')
# nltk.download('wordnet')
stop_words_en = set(stopwords.words('english'))
stop_words_ru = set(stopwords.words('russian'))
stop_words = stop_words_en.union(stop_words_ru)

morph = pymorphy2.MorphAnalyzer()


def lemmatize_text(tokens, lang='en'):
    if lang == 'ru':
        return [morph.parse(word)[0].normal_form for word in tokens]
    else:
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word) for word in tokens]


with open("posts.json", "r", encoding="utf-8") as file:
    data = json.load(file)

posts = []
likes = []
group_ids = []

for block in data:
    for i, post in enumerate(block['posts'], start=1):
        post_id = f"{block['group_id']}_{i}"
        post_text = post['text']
        post_likes = post['likes']
        group_id = block['group_id']

        posts.append(post_text)
        likes.append(post_likes)
        group_ids.append(group_id)

import re


def remove_emojis(data):
    emoj = re.compile("["
                      u"\U0001F600-\U0001F64F"  # emoticons
                      u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                      u"\U0001F680-\U0001F6FF"  # transport & map symbols
                      u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                      u"\U00002500-\U00002BEF"  # chinese char
                      u"\U00002702-\U000027B0"
                      u"\U000024C2-\U0001F251"
                      u"\U0001f926-\U0001f937"
                      u"\U00010000-\U0010ffff"
                      u"\u2640-\u2642"
                      u"\u2600-\u2B55"
                      u"\u200d"
                      u"\u23cf"
                      u"\u23e9"
                      u"\u231a"
                      u"\ufe0f"  # dingbats
                      u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)


def clean_and_lemmatize(text):
    text = remove_emojis(text)
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
    lang = 'ru' if any('а' <= char <= 'я' for char in text) else 'en'
    tokens = lemmatize_text(tokens, lang)
    # print(tokens)
    return tokens


cleaned_posts = [clean_and_lemmatize(post) for post in posts]
model = Word2Vec(sentences=cleaned_posts, vector_size=100, window=5, min_count=1, workers=4)


#  получение эмбединга поста (усреднение эмбедингов слов)
def get_embedding(post):
    words = word_tokenize(post.lower())
    word_vectors = [model.wv[word] for word in words if word in model.wv]
    return np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.vector_size)


embeddings = [get_embedding(post) for post in posts]

df = pd.DataFrame({
    'posts': posts,
    'post_embedding': embeddings,
    'likes': likes,
    'group_id': group_ids
})

print(df)
df.to_csv("posts_embeddings_cleaned.csv", index=False, encoding='utf-8')
