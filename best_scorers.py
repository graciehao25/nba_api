#best_scorers.py
#Gracie Hao Watchbox take home assignment

import requests
from tqdm import trange
import json
import time
import pandas as pd
import numpy as np

#get max page for stats endpoint
test=requests.get('https://www.balldontlie.io/api/v1/stats?seasons[]=2018&page=1').json()
max_page=test['meta']['total_pages']


## get all stats for season 2018-2019
all_stats=[]
for i in trange(max_page):
    stats=requests.get(f'https://www.balldontlie.io/api/v1/stats?seasons[]=2018&per_page=100&page={i+1}').json()
#     if stats["meta"]["next_page"]:
    all_stats.extend(stats['data'])
    time.sleep(1/2)

## save Json file
with open('all_stats.json', 'w') as f:
    json.dump(all_stats, f)

## get top 10 Scorers
pts_all_game=[]
for i in trange(len(all_stats)):
    if all_stats[i]['player']:
        player_id=all_stats[i]['player']['id']
        game_id=all_stats[i]['game']['id']
        pts=all_stats[i]['pts']
        pts_each_game = (player_id, game_id, pts)
        pts_all_game.append(pts_each_game)


df=pd.DataFrame.from_records(pts_all_game, columns=['player_id','game_id','pts'])

top_10_df = df.groupby('player_id')\
            .agg({'game_id':'size', 'pts':'mean'}) \
            .rename(columns={'game_id':'num_game','pts':'avg_pts_per_game'})\
            .sort_values(by=['avg_pts_per_game'], ascending=False)\
            .reset_index()\
            .head(10)


## Get all players information
IDs=top_10_df['id'].to_list()
all_infos=[]
for i in IDs:
    player_info=requests.get(f'https://www.balldontlie.io/api/v1/players/{i}').json()
    all_infos.append(player_info)
    time.sleep(1/2)

info_column=['id',
    'first_name',
    'last_name',
    'height_feet',
    'height_inches',
    'position',
    'team',
    'weight_pounds']


info_df=pd.DataFrame.from_records(all_infos, columns=info_column)\
        .drop(columns=['team'])\ 
        .rename(columns={'id':'player_id'})        #TODO: didnt have enough time, otherwise could add more team info

result= top_10_df.merge(info_df, on='player_id').reset_index().rename(columns={'index':'rank'}) #TODO: hacky way of listing rank, run out of time. should start from 1

result.to_csv('result.csv',index=False)