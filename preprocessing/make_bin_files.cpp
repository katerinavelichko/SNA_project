#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>
#include <string>
#include <filesystem>
#include <stdexcept>
#include <algorithm>
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <chrono>

namespace fs = std::filesystem;

constexpr size_t BUFFER_SIZE = 1 << 20;
constexpr size_t MAX_THREADS = 4;
constexpr size_t MAX_USERS_PER_GROUP = 100000;

std::mutex queue_mutex;
std::condition_variable queue_cv;
std::queue<fs::path> file_queue;

std::string trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) return "";
    size_t last = str.find_last_not_of(" \t\n\r");
    return str.substr(first, last - first + 1);
}

int extract_id(const std::string& group_info, const std::string& prefix) {
    if (group_info.find(prefix) == 0) {
        const char* start = group_info.c_str() + prefix.size();
        return std::atoi(start);
    }
    throw std::runtime_error("Unrecognized group prefix in " + group_info);
}

void process_file(const std::string& output_folder) {
    while (true) {
        fs::path file_path;
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            queue_cv.wait(lock, [] { return !file_queue.empty(); });

            if (file_queue.empty()) return;

            file_path = file_queue.front();
            file_queue.pop();
        }

        std::string file_name = file_path.filename().string();

        try {
            std::ifstream infile(file_path, std::ios::in | std::ios::binary);
            infile.rdbuf()->pubsetbuf(new char[BUFFER_SIZE], BUFFER_SIZE);

            if (!infile.is_open()) {
                throw std::runtime_error("Could not open file: " + file_path.string());
            }

            std::unordered_map<int, std::vector<int>> group_data;
            std::string line;

            while (std::getline(infile, line)) {
                if (line.rfind("\xEF\xBB\xBF", 0) == 0) {
                    line = line.substr(3);
                }

                std::istringstream iss(line);
                std::string group_info, user_ids_part;

                if (!std::getline(iss, group_info, ';')) {
                    throw std::runtime_error("Malformed line: " + line);
                }

                group_info = trim(group_info);
                int group_id;

                if (group_info.find("http://vk.com/club") == 0) {
                    group_id = extract_id(group_info, "http://vk.com/club");
                } else if (group_info.find("http://vk.com/public") == 0) {
                    group_id = extract_id(group_info, "http://vk.com/public");
                } else if (group_info.find("http://vk.com/event") == 0) {
                    group_id = extract_id(group_info, "http://vk.com/event");
                } else {
                    throw std::runtime_error("Unrecognized group prefix in " + group_info);
                }

                if (!std::getline(iss, user_ids_part)) {
                    throw std::runtime_error("Missing user IDs in line: " + line);
                }

                user_ids_part = trim(user_ids_part);
                std::vector<int> user_ids;
                std::istringstream user_stream(user_ids_part);
                std::string user_id;

                while (std::getline(user_stream, user_id, ',')) {
                    user_id = trim(user_id);
                    user_ids.push_back(std::stoi(user_id));
                }

                auto& existing_users = group_data[group_id];
                existing_users.insert(existing_users.end(), user_ids.begin(), user_ids.end());
            }

            infile.close();

            // Remove duplicate users for each group and filter out large groups
            for (auto it = group_data.begin(); it != group_data.end(); ) {
                auto& users = it->second;
                std::sort(users.begin(), users.end());
                users.erase(std::unique(users.begin(), users.end()), users.end());

                if (users.size() > MAX_USERS_PER_GROUP) {
                    it = group_data.erase(it); // Remove groups with too many users
                } else {
                    ++it;
                }
            }

            // Save processed data to a binary file
            std::string output_file = output_folder + "/" + file_name + ".bin";
            std::ofstream outfile(output_file, std::ios::binary | std::ios::out | std::ios::trunc);
            outfile.rdbuf()->pubsetbuf(new char[BUFFER_SIZE], BUFFER_SIZE);

            if (!outfile.is_open()) {
                throw std::runtime_error("Could not open output file: " + output_file);
            }

            for (const auto& [group_id, user_ids] : group_data) {
                outfile.write(reinterpret_cast<const char*>(&group_id), sizeof(group_id));
                int user_count = user_ids.size();
                outfile.write(reinterpret_cast<const char*>(&user_count), sizeof(user_count));
                outfile.write(reinterpret_cast<const char*>(user_ids.data()), user_count * sizeof(int));
            }

            outfile.close();

            std::cout << "Processed " << file_name << " and saved to " << output_file << "." << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "Error processing file " << file_name << ": " << e.what() << std::endl;
        }
    }
}

void process_large_files(const std::string& input_folder, const std::string& output_folder) {
    if (!fs::exists(output_folder)) {
        fs::create_directories(output_folder);
    }

    for (const auto& entry : fs::directory_iterator(input_folder)) {
        if (entry.is_regular_file()) {
            file_queue.push(entry.path());
        }
    }

    std::vector<std::thread> threads;
    for (size_t i = 0; i < MAX_THREADS; ++i) {
        threads.emplace_back(process_file, output_folder);
    }

    for (auto& thread : threads) {
        thread.join();
    }
}

int main() {
    std::string input_path = "D:/SNA 2/vk";
    std::string output_path = "D:/PychramProjects/SNA_project/vk_bin_files_2";

    auto start = std::chrono::high_resolution_clock::now();
    process_large_files(input_path, output_path);
    auto end = std::chrono::high_resolution_clock::now();

    std::cout << "Total elapsed time: "
              << std::chrono::duration_cast<std::chrono::seconds>(end - start).count() << " seconds." << std::endl;

    return 0;
}
