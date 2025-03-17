import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

with open("games.json", "r") as file:
    json_data = json.load(file)


def get_genres(*args):
    return genres_df

country_data_list = []
for idx, row in enumerate(json_data):
    country_data = pd.Series(row["countryData"])
    country_data_list.append(country_data)

country_df = pd.DataFrame(country_data_list)


# here the game_steamId is a link to main dataframe
audience_overlap_list = []
for idx, row in enumerate(json_data):
    info = row['audienceOverlap']
    if info is None:
            continue
    for overlap in info:
        overlap["game_steamId"] = row["steamId"]
        audience_overlap_list.append(overlap)

audience_overlap_df = pd.DataFrame(audience_overlap_list)

ids = audience_overlap_df['game_steamId']
id_counts_filtered = ids[ids.isin(df['steamId'])]
# print(id_counts_filtered.size)
# print(id_counts_filtered)
# display(audience_overlap_df.head(10))


tags_list = []
for idx, row in enumerate(json_data):
    tags = pd.Series(row["tags"])
    tags['steamId'] = row['steamId']
    tags_list.append(tags)

tags_df = pd.DataFrame(tags_list)
display(tags_df.head(10))
assert len(tags_df) == tags_df['steamId'].nunique()


genres_list = []
for idx, row in enumerate(json_data):
    genres = pd.Series(row["genres"])
    genres['steamId'] = row['steamId']
    genres_list.append(genres)

genres_df = pd.DataFrame(genres_list)
assert len(genres_df) == genres_df['steamId'].nunique()


features_list = []
for idx, row in enumerate(json_data):
    features = pd.Series(row["features"])
    features['steamId'] = row['steamId']
    features_list.append(features)

features_df = pd.DataFrame(features_list)
assert len(features_df) == features_df['steamId'].nunique()


language_list = []
for idx, row in enumerate(json_data):
    language = pd.Series(row["languages"])
    language['steamId'] = row['steamId']
    language_list.append(language)

language_df = pd.DataFrame(language_list)
assert len(language_df) == language_df['steamId'].nunique()


developers_list = []
for idx, row in enumerate(json_data):
    developers = pd.Series(row["developers"])
    developers['steamId'] = row['steamId']
    developers_list.append(developers)

developers_df = pd.DataFrame(developers_list)
assert len(developers_df) == developers_df['steamId'].nunique()


publishers_list = []
for idx, row in enumerate(json_data):
    publishers = pd.Series(row["publishers"])
    publishers['steamId'] = row['steamId']
    publishers_list.append(publishers)

publishers_df = pd.DataFrame(publishers_list)
display(publishers_df.head(10))
occurences = publishers_df.groupby('steamId').apply(lambda x: x[[0, 1, 2, 3]].count().sum(), include_groups=False)


estimate_det_list = []
for idx, row in enumerate(json_data):
    details = pd.Series(row["estimateDetails"])
    details['steamId'] = row['steamId']
    estimate_det_list.append(details)

details_df = pd.DataFrame(estimate_det_list)
