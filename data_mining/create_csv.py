'''
This scripts save all table in the sqlite database to csv
'''

import pandas as pd
from sqlalchemy import create_engine

# Create connection
db_url = './../datasets/sa_cricket.db'
engine = create_engine('sqlite:///'+db_url)
conn = engine.connect()

# Read table mat and save to csv
pd.read_sql_table('mat', conn).to_csv('./../datasets/mat.csv', index=False)
print('Saved mat.csv')

# Read table bat and save to csv
pd.read_sql_table('bat', conn).to_csv('./../datasets/bat.csv', index=False)
print('Saved bat.csv')

# Read table bowl and save to csv
pd.read_sql_table('bowl', conn).to_csv('./../datasets/bowl.csv', index=False)
print('Saved bowl.csv')

# Read table player and save to csv
pd.read_sql_table('player', conn).to_csv('./../datasets/player.csv', index=False)
print('Saved player.csv')

# Read table ground and save to csv
pd.read_sql_table('ground', conn).to_csv('./../datasets/ground.csv', index=False)
print('Saved ground.csv')

# Read table opposition and save to csv
pd.read_sql_table('opposition', conn).to_csv('./../datasets/opposition.csv', index=False)
print('Saved opposition.csv')

conn.close()