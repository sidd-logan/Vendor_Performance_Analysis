import pandas as pd
import os
from sqlalchemy import create_engine
import logging as lg
import time

lg.basicConfig(
    filename=r"D:\Project2\data\logs\ingestion.db.log",
    level=lg.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine=create_engine('sqlite:///inventory.db')
folder=r"D:\Project2\data\data\\"
def ingest_db(df,table_name,engine):
    ''' insert into db '''
    df.to_sql(table_name,con=engine ,if_exists='replace', index=False)

def load_raw_data():
    '''this function will load csv and inget in db'''
    start=time.time()
    for file in os.listdir(folder):
        if '.csv' in file:
            df=pd.read_csv(folder+'\\'+file)
            lg.info(f'ingesting {file} in db')
            ingest_db(df,file[:-4],engine)
    end=time.time()
    print("------- Ingetion complete -------")
    print(f'time taken {end-start}/60 in minutes')
            #print(f'{folder}'+'\\'+file)
if __name__=='__main__':
    load_raw_data()

