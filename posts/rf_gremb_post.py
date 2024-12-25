import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from collections import OrderedDict


def parse_embeddings(embedding_str):
    return np.fromstring(embedding_str.strip('[]'), sep=' ')


matrix_file = 'jaccard_matrix.txt'
matrix = pd.read_csv(matrix_file, header=None, delim_whitespace=True)

ids_file = 'ids.txt'
with open(ids_file, 'r') as f:
    ids = f.read().split()
matrix.columns = ids
matrix.index = ids

# j = matrix[str(13457639)]

df = pd.read_csv("posts_embeddings_cleaned.csv")
df['post_embedding'] = df['post_embedding'].apply(parse_embeddings)
print(df)

groups = df['group_id'].unique()
group_mse = {}
group_mae = {}
models = {}

rf_params = OrderedDict([
    ('max_depth', 30),
    ('max_features', 'sqrt'),
    ('min_samples_leaf', 8),
    ('min_samples_split', 16),
    ('n_estimators', 195)
])

group_stats = df.groupby('group_id')['likes'].agg(['mean', 'median'])

for group in groups:
    group_df = df[df['group_id'] == group]

    if len(group_df) < 100:
        continue

    # group_mean_likes = group_df['group_id'].map(group_stats['mean'])
    # y = group_df['likes'] / group_mean_likes
    # y.fillna(0, inplace=True)

    X = group_df['post_embedding'].tolist()

    y = group_df['likes']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train = np.vstack(X_train)
    X_test = np.vstack(X_test)

    rf = RandomForestRegressor(**rf_params, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    group_mse[group] = mse
    group_mae[group] = mae
    models[group] = rf
    print(f'group {group}, mse {mse}, mae {mae}')

# MSE для каждой группы
# for group, mse in group_mse.items():
#     print(f'Group {group} - MSE: {mse}, MAE: {group_mae[group]}')

print(np.mean(list(group_mse.values())))
print(np.mean(list(group_mae.values())))

m_l = list(models.keys())


def weighted_prediction(group, X_test, threshold=0.02):
    weights = matrix[str(group)]
    valid_weights = {other_group: weight for other_group, weight in weights.items() if
                     (weight > threshold and weight < 1.0 and int(other_group) in m_l)}
    total_weight = sum(valid_weights.values())

    weighted_preds = 0
    for other_group, weight in valid_weights.items():
        weighted_preds += weight * models[int(other_group)].predict(X_test)

    weighted_preds += models[group].predict(X_test) * (1 - total_weight)

    return weighted_preds


for group in groups:
    group_df = df[df['group_id'] == group]

    if len(group_df) < 100:
        continue

    # group_mean_likes = group_df['group_id'].map(group_stats['mean'])
    # y = group_df['likes'] / group_mean_likes
    # y.fillna(0, inplace=True)

    X = group_df['post_embedding'].tolist()

    y = group_df['likes']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train = np.vstack(X_train)
    X_test = np.vstack(X_test)

    y_pred = weighted_prediction(group, X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    if group_mse[group] > mse:
        group_mse[group] = mse
    if group_mae[group] > mae:
        group_mae[group] = mae

    print(f'WEIGHTED group {group}, mse {mse}, mae {mae}')

print(np.mean(list(group_mse.values())))
print(np.mean(list(group_mae.values())))
