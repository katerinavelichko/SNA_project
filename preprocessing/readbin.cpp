#include <iostream>
#include <fstream>
#include <vector>
#include <string>

void read_binary_file(const std::string& file_path, const std::string& output_path) {
    std::ifstream infile(file_path, std::ios::binary);
    if (!infile.is_open()) {
        std::cerr << "Failed infile " << file_path << std::endl;
        return;
    }

    std::ofstream outfile(output_path);
    if (!outfile.is_open()) {
        std::cerr << "Failed outfile " << output_path << std::endl;
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

        outfile << group_id;
        outfile << "\n";
    }

    infile.close();
    outfile.close();
}

int main() {
    std::string file_path = "random_filtered_groups.bin";
    std::string output_path = "group_ids_new.txt";

    read_binary_file(file_path, output_path);
    std::cout << "saved to " << output_path << std::endl;
    return 0;
}
