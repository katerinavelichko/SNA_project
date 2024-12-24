import matplotlib.pyplot as plt
from collections import Counter

with open('sizes.txt', 'r') as file:
    data = list(map(int, file.read().split()))

# data = [
#     1000, 1000, 1000, 108, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
#     402, 1000, 1000, 108, 1000, 1000, 413, 1000, 1000, 1000, 1000, 1000,
#     1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 388, 1000, 1000, 1000,
#     1000, 1000, 1000, 1000, 1000, 182
# ]

groups = []
cur_group = 0
left_side = 10000
right_side = 30000

for number in data:
    if number == 1000:
        cur_group += number
    else:
        if cur_group > 0:
            cur_group += number
            if cur_group <= right_side and cur_group >= left_side:
                groups.append(cur_group)

        cur_group = 0


l = 10000
r = 15000
if cur_group > 0:
    groups.append(cur_group)
rng = len([x for x in groups if l <= x <= r])
print(f'Количество групп в диапазоне {l}-{r}: {rng}')


interval_size = 1000

def get_interval(group_size, interval_size):
    return (group_size // interval_size) * interval_size

intervals = [get_interval(group, interval_size) for group in groups]
interval_counts = Counter(intervals)

intervals_sorted = sorted(interval_counts.keys())
frequencies = [interval_counts[interval] for interval in intervals_sorted]

plt.figure(figsize=(24, 12))
plt.bar(intervals_sorted, frequencies, width=interval_size * 0.9, edgecolor='black')
plt.title(f'Распределение количества групп по интервалам размера {interval_size}')
plt.xlabel(f'Размер группы (интервалы по {interval_size}: от {left_side} до {right_side})')
plt.ylabel('Количество групп')
plt.xticks(intervals_sorted, [f'{i / 1000}-{(i + interval_size) / 1000}k' for i in intervals_sorted])
plt.grid(True)
plt.show()

print("Интервалы и количество групп:", list(zip(intervals_sorted, frequencies)))
