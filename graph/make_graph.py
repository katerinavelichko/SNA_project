import networkx as nx
import matplotlib.pyplot as plt


def read_jaccard_matrix(file_path):
    with open(file_path, 'r') as f:
        matrix = []
        for line in f:
            row = list(map(float, line.strip().split()))
            matrix.append(row)
    return matrix


def read_ids(file_path):
    with open(file_path, 'r') as f:
        ids = []
        for line in f:
            row = line.strip().split()
            ids.extend(row)
    return ids


def build_graph_from_jaccard(matrix, ids):
    G = nx.Graph()
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):  # Используем только верхний треугольник
            if matrix[i][j] > 0.05:
                G.add_edge(ids[i], ids[j], weight=matrix[i][j])
    return G


def visualize_graph(G):
    pos = nx.spring_layout(G, k=0.3)  # Увеличенная разрядка между узлами
    node_colors = [G.degree(n) for n in G.nodes()]  # Цвет узлов по их степени

    plt.figure(figsize=(12, 10))  # Увеличенный размер графика
    nx.draw(
        G, pos,
        with_labels=True,
        node_color=node_colors,
        cmap=plt.cm.Blues,
        node_size=800,
        edge_color='gray',
        font_size=8
    )
    plt.title("Improved Graph Visualization")
    plt.show()


def save_graph(graph, file_path):
    nx.write_graphml(graph, output_graph_file)
    print(f"Graph saved to {file_path}")


if __name__ == "__main__":
    # Путь к текстовому файлу с матрицей Жаккара и идентификаторами
    input_file = "D:/PychramProjects/SNA_project/jaccard_matrix.txt"
    input_ids_file = "D:/PychramProjects/SNA_project/ids.txt"
    output_graph_file = "D:/PychramProjects/SNA_project/graph.gpickle"

    # Чтение матрицы Жаккара
    jaccard_matrix = read_jaccard_matrix(input_file)

    # Чтение идентификаторов
    input_ids = read_ids(input_ids_file)

    # Построение графа
    graph = build_graph_from_jaccard(jaccard_matrix, input_ids)

    # Визуализация графа
    visualize_graph(graph)

    # Сохранение графа
    save_graph(graph, output_graph_file)
