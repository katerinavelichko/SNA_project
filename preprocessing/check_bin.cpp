#include <iostream>
#include <fstream>
#include <vector>
#include <string>

void read_binary_file(const std::string& file_path) {
    std::ifstream infile(file_path, std::ios::binary);
    if (!infile.is_open()) {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        return;
    }

    while (infile.good()) {
        int group_id;
        int user_count;

        infile.read(reinterpret_cast<char*>(&group_id), sizeof(group_id));
        infile.read(reinterpret_cast<char*>(&user_count), sizeof(user_count));

        if (infile.eof()) break;

        std::vector<int> user_ids(user_count);
        infile.read(reinterpret_cast<char*>(user_ids.data()), user_count * sizeof(int));

        std::cout << "Group ID: " << group_id << ", User Count: " << user_count << "\nUsers: ";
        for (int user_id : user_ids) {
            std::cout << user_id << " ";
        }
        std::cout << std::endl;
    }

    infile.close();
}

int main() {
    std::string file_path = "D:/PychramProjects/SNA_project/vk_bin_files_2/0BB45C45DC330EE2F75730E4081B8CF5AC038BBB.bin";
    read_binary_file(file_path);

    return 0;
}
