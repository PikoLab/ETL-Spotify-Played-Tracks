import requests
import pandas as pd 
import sqlalchemy
import sqlite3
from datetime import datetime
import datetime

#Global Variables
DATABASE_LOCATION='sqlite:///spotify_played_tracks.sqlite'
TOKEN=' ' #your spotify API token

# Data Validation Function
def check_if_validate(df:pd.DataFrame):
    #check if df is empty
    if df.empty:
        print('No songs downloaded. Finishing execution.')
        return False
    
    #check if there is any null values:
    if df.isnull().values.any():
        raise Exception('Null values found!')
    
    #check primary key:
    if pd.Series(df['played_datetime']).is_unique:
        pass
    else: 
        raise Exception('Primary Key Check is violated.') 
    
    #check if the data is for yesterday
    yesterday=datetime.datetime.now()-datetime.timedelta(days=1)
    yesterday=yesterday.replace(hour=0,minute=0,second=0,microsecond=0)

    timestamps=df['played_date'].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d')!=yesterday:
            raise Exception('At least one of the returned songs are not played yesterday')
    
    return True

if __name__=="__main__":

    # Step1: Extract Data From Spotify API (https://developer.spotify.com/console/get-recently-played/)
    headers={
        'Accept' : 'application/json',
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer {token}'.format(token=TOKEN) 
    }

    # Extract data everyday(for yesterday)
    today=datetime.datetime.now()
    yesterday=today-datetime.timedelta(days=1)
    yesterday_unix_timestamp=int(yesterday.timestamp())*1000
    yesterday_date=yesterday.strftime('%Y-%m-%d')

    req=requests.get('https://api.spotify.com/v1/me/player/recently-played?=after{}&limit=50'.format(yesterday_unix_timestamp),headers=headers)
    data=req.json()

    # Step2-1:Transform from json object to pandas datafram
    song_name=[]
    singer_name=[]
    played_datetime=[]
    played_date=[]

    for song in data['items']:
        # if song['played_at'][0:10]==yesterday_date:
        song_name.append(song['track']['name'])
        singer_name.append(song['track']['album']['artists'][0]['name'])
        played_datetime.append(song['played_at'])
        played_date.append(song['played_at'][0:10])
    
    song_dict={
        'song_name': song_name,
        'singer_name': singer_name,
        'played_datetime': played_datetime,
        'played_date':played_date
    }

    song_df=pd.DataFrame(song_dict, columns=['song_name','singer_name','played_datetime','played_date'])
    print(song_df)

    # Step2-2: check data validation: check df.empty, null values, primary key constraint, data for yesterday
    if check_if_validate(song_df):
        print('Data is Valid. Proceed to Load stage.')

    # Step3: Load data to sql database
    engine=sqlalchemy.create_engine(DATABASE_LOCATION)
    conn=sqlite3.connect('spotify_played_tracks.sqlite')
    cursor=conn.cursor()

    sql_query='''
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        singer_name VARCHAR(200),
        played_datetime VARCHAR(200),
        played_date VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY(played_datetime)
    )
    '''
    cursor.execute(sql_query)
    print('Database opened successfully.')

    try:
        song_df.to_sql('my_played_tracks', engine, index=False, if_exists='append')
    except:
        print('Data already exists in the database!')

    conn.close()
    print ('Database closed successfully.')



