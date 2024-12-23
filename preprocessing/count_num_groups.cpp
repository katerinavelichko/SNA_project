#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <string>

namespace fs = std::filesystem;

void count_groups_in_folder(const std::string& folder_path) {
    int total_groups = 0;

    // Проход по всем файлам в указанной папке
    for (const auto& entry : fs::directory_iterator(folder_path)) {
        if (entry.is_regular_file() && entry.path().extension() == ".bin") {
            std::ifstream infile(entry.path(), std::ios::binary);

            if (!infile.is_open()) {
                std::cerr << "Failed to open file: " << entry.path() << std::endl;
                continue;
            }

            while (true) {
                int group_id, user_count;

                // Считываем ID группы (4 байта)
                infile.read(reinterpret_cast<char*>(&group_id), sizeof(group_id));
                if (infile.eof() || infile.gcount() < sizeof(group_id)) break;

                // Считываем количество пользователей (4 байта)
                infile.read(reinterpret_cast<char*>(&user_count), sizeof(user_count));
                if (infile.eof() || infile.gcount() < sizeof(user_count)) break;

                // Пропускаем пользовательские ID (user_count * 4 байта)
                infile.seekg(user_count * sizeof(int), std::ios::cur);

                // Увеличиваем счетчик групп
                total_groups++;
            }

            infile.close();
        }
    }

    std::cout << "Total groups: " << total_groups << std::endl;
}

int main() {
    std::string folder_path = "D:/PychramProjects/SNA_project/vk_bin_files";

    auto start = std::chrono::high_resolution_clock::now();
    count_groups_in_folder(folder_path);
    auto end = std::chrono::high_resolution_clock::now();

    std::cout << "Elapsed time: "
              << std::chrono::duration_cast<std::chrono::seconds>(end - start).count() << " seconds." << std::endl;

    return 0;
}
