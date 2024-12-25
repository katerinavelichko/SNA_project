from node2vec import Node2Vec
import networkx as nx
import numpy as np
import pandas as pd


def generate_graph_embeddings(graph, dimensions=128, walk_length=30, num_walks=200, workers=4):
    # Создание модели Node2Vec
    node2vec = Node2Vec(
        graph,
        dimensions=dimensions,
        walk_length=walk_length,
        num_walks=num_walks,
        workers=workers
    )
    # Обучение модели
    model = node2vec.fit(window=10, min_count=1, batch_words=4)

    # Получение эмбеддингов
    embeddings = {str(node): model.wv[str(node)] for node in graph.nodes()}
    return embeddings


def save_embeddings(embeddings, output_file):
    df = pd.DataFrame.from_dict(embeddings, orient='index')
    df.index.name = 'node_id'
    df.to_csv(output_file)


# Чтение графа из ранее созданной NetworkX модели
graph = nx.read_graphml("D:/PychramProjects/SNA_project/graph.gpickle")

# Генерация эмбеддингов
embeddings = generate_graph_embeddings(graph)

# Сохранение эмбеддингов
save_embeddings(embeddings, "../embed_graph/group_embeddings.csv")
print("Эмбеддинги сохранены в 'group_embeddings.csv'")
