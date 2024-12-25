#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <omp.h>
#include <iomanip>

// Функция для сохранения матрицы в текстовый файл
void saveMatrix(const std::vector<std::vector<double>>& matrix, const std::string& fileName) {
    std::ofstream outFile(fileName);
    if (!outFile.is_open()) {
        std::cerr << "Ошибка при открытии файла для записи: " << fileName << std::endl;
        return;
    }
    for (const auto& row : matrix) {
        for (double value : row) {
            outFile << value << " ";
        }
        outFile << "\n";
    }
    outFile.close();
    std::cout << "Матрица Жаккара сохранена в файл: " << fileName << std::endl;
}

int main() {
    const std::string filteredFile = "D:/PychramProjects/SNA_project/random_filtered_groups.bin";
    const std::string outputFile = "D:/PychramProjects/SNA_project/jaccard_matrix.txt";

    std::unordered_map<int, std::vector<int>> groupUsers;

    // Чтение бинарного файла
    std::ifstream inFile(filteredFile, std::ios::binary);
    if (!inFile.is_open()) {
        std::cerr << "Ошибка при открытии файла: " << filteredFile << std::endl;
        return 1;
    }

    while (true) {
        int groupId, userCount;
        inFile.read(reinterpret_cast<char*>(&groupId), sizeof(int));
        inFile.read(reinterpret_cast<char*>(&userCount), sizeof(int));
        if (inFile.eof()) break;

        std::vector<int> userIds(userCount);
        inFile.read(reinterpret_cast<char*>(userIds.data()), userCount * sizeof(int));
        groupUsers[groupId] = std::move(userIds);
    }
    inFile.close();

    // Построение матрицы Жаккара
    std::vector<int> groupIds;
    for (const auto& pair : groupUsers) {
        groupIds.push_back(pair.first);
    }

    int numGroups = groupIds.size();
    std::vector<std::vector<double>> jaccardMatrix(numGroups, std::vector<double>(numGroups, 0.0));

    // Распараллеливание вычислений
#pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < numGroups; ++i) {
        for (int j = i; j < numGroups; ++j) {
            const auto& vec1 = groupUsers[groupIds[i]];
            const auto& vec2 = groupUsers[groupIds[j]];

            std::vector<int> intersectionVec(std::min(vec1.size(), vec2.size()));
            auto it = std::set_intersection(vec1.begin(), vec1.end(), vec2.begin(), vec2.end(), intersectionVec.begin());
            intersectionVec.resize(it - intersectionVec.begin());

            int intersection = intersectionVec.size();
            int unionSize = vec1.size() + vec2.size() - intersection;

            double jaccardIndex = unionSize > 0 ? static_cast<double>(intersection) / unionSize : 0.0;
            jaccardMatrix[i][j] = jaccardIndex;
            jaccardMatrix[j][i] = jaccardIndex; // Матрица симметрична
        }
    }

    // Сохранение матрицы в файл
    saveMatrix(jaccardMatrix, outputFile);

    // Вычисление среднего значения матрицы
    double totalValue = 0.0;
    int totalElements = 0;
    for (const auto& row : jaccardMatrix) {
        for (double value : row) {
            totalValue += value;
            ++totalElements;
        }
    }
    double averageJaccardValue = totalValue / totalElements;
    std::cout << "Average value: " << std::fixed << std::setprecision(4) << averageJaccardValue << std::endl;

    return 0;
}
