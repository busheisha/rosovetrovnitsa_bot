

import pandas as pd
import plotly.express as px
import datetime as dt
import numpy as np




def clean_data(file_path: str) -> pd.DataFrame:


    df = pd.read_excel(file_path)
    df.columns = df.iloc[5]
    df = df.drop(range(6))

    t = {df.columns[0]:'time'}
    df = df.rename(columns=t)
    windnames = {
    'Переменное направление': 'ХХ',
    'Штиль, безветрие': 'Х',
    'Ветер, дующий с севера': 'С',
    'Ветер, дующий с северо-северо-востока': 'ССВ',
    'Ветер, дующий с северо-востока': 'СВ',
    'Ветер, дующий с востоко-северо-востока': 'ВСВ',
    'Ветер, дующий с востока': 'В',
    'Ветер, дующий с востоко-юго-востока': 'ВЮВ',
    'Ветер, дующий с юго-востока': 'ЮВ',
    'Ветер, дующий с юго-юго-востока': 'ЮЮВ',
    'Ветер, дующий с юга': 'Ю',
    'Ветер, дующий с юго-юго-запада': 'ЮЮЗ',
    'Ветер, дующий с юго-запада': 'ЮЗ',
    'Ветер, дующий с западо-юго-запада': 'ЗЮЗ',
    'Ветер, дующий с запада': 'З',
    'Ветер, дующий с западо-северо-запада': 'ЗСЗ',
    'Ветер, дующий с северо-запада': 'СЗ',
    'Ветер, дующий с северо-северо-запада': 'ССЗ'
    }


    df['DD'] = df['DD'].replace(windnames)
    df = df.loc[df['DD'] != 'Х']
    df = df.loc[df['DD'] != 'ХХ']
    print(df)
    return df


def create_additional_df(winds: list[str]) -> pd.Series:
    rs2 = pd.Series(data = 0, index = winds)
    rs2 = rs2.to_frame(name= 'DD')
    return rs2


def processing(df: pd.DataFrame, winds: list[str], additional_df: pd.DataFrame) -> pd.DataFrame:
    rs = df[['time', 'DD', 'Ff']].copy()
    rs = rs.groupby(['DD']).size().to_frame(name= 'DD')
   
    rs1 = pd.concat([rs, additional_df]).reset_index()
    rs1 = rs1.drop_duplicates(subset = ['index'])
    rs1 = rs1.set_index('index')
    rs1 = rs1.reindex(index = winds)
    rs1 = rs1.reset_index()
    return rs1


def smartrose_processing (df: pd.DataFrame, winds: list[str], additional_df: pd.DataFrame) -> pd.DataFrame:
    rose = df.copy()
    rose['time'] = pd.to_datetime(rose['time'])
    reftime = rose.at[6, 'time']
    rose['reftime'] = reftime
    rose['age'] = rose['reftime'] - rose['time']
    rose['age'] = (rose['age'].dt.components.hours + (rose['age'].dt.components.days * 24)) / 24
    rose['importance'] = np.exp(rose['age']* -0.22)
    rose['importance_wind']= rose['Ff'] * rose['importance']
    windrose = rose.groupby('DD').importance_wind.sum()
    additional_df = additional_df.rename(columns = {'DD': 'importance_wind'})
    windrose = pd.concat([windrose, additional_df]).reset_index()
    windrose = windrose.drop_duplicates(subset = ['index'])
    windrose = windrose.set_index('index')
    windrose = windrose.reindex(index = winds)
    windrose = windrose.reset_index()
    return windrose


def create_windrose(file_path: str, first_image_path: str) -> str:
    winds = ['С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЗСЗ', 'СЗ', 'ССЗ']
    df = clean_data(file_path)
    rs2 = create_additional_df(winds)
    rs1 = processing(df, winds, rs2)


    fig1 = px.line_polar(rs1, r='DD',
                        theta='index', 
                        width = 600, height = 600, line_close=True, title = 'windrose')
    fig1.update_traces(fill='toself')
    fig1.write_image(first_image_path) 
    return first_image_path

def create_smartrose (file_path: str, second_image_path: str) -> str:
    winds = ['С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЗСЗ', 'СЗ', 'ССЗ']
    df = clean_data(file_path)
    rs2 = create_additional_df(winds)
    windrose = smartrose_processing(df, winds, rs2)

    fig2 = px.line_polar(windrose, r='importance_wind',
                    theta='index', width = 600, height = 600, line_close=True, title = 'smartrose')
    fig2.update_traces(fill='toself')
    fig2.write_image(second_image_path) 
    return second_image_path


