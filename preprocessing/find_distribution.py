import os
import struct
import matplotlib.pyplot as plt

filtered_file = "D:/PychramProjects/SNA_project/filtered_groups.bin"

group_sizes = []
total_groups = 0

with open(filtered_file, "rb") as f:
    while True:
        data = f.read(8)  # Чтение group_id (4 байта) и user_count (4 байта)
        if not data:
            break
        group_id, user_count = struct.unpack("ii", data)
        group_sizes.append(user_count)
        total_groups += 1
        # Пропустить user IDs
        f.seek(user_count * 4, os.SEEK_CUR)

# Общая статистика
total_users = sum(group_sizes)
min_size = min(group_sizes)
max_size = max(group_sizes)
avg_size = total_users / total_groups

print("Анализ filtered_groups.bin:")
print(f"Общее количество групп: {total_groups}")
print(f"Общее количество пользователей во всех группах: {total_users}")
print(f"Минимальный размер группы: {min_size}")
print(f"Максимальный размер группы: {max_size}")
print(f"Средний размер группы: {avg_size:.2f}")

# Гистограмма размеров групп
plt.figure(figsize=(12, 6))
plt.hist(group_sizes, bins=50, edgecolor='black')
plt.title("Распределение размеров групп")
plt.xlabel("Количество пользователей в группе")
plt.ylabel("Частота")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# Диаграмма размаха (box plot) для размеров групп
plt.figure(figsize=(12, 6))
plt.boxplot(group_sizes, vert=False, patch_artist=True)
plt.title("Диаграмма размаха размеров групп")
plt.xlabel("Размер группы (количество пользователей)")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.show()
