

import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import datetime as dt
import gzip
import shutil


def opengz (file_path: str) -> str:
    with gzip.open(file_path, 'rb') as file_in:
        with open(f'{file_path.replace(".xls.gz","")}.xls', 'wb') as file_out:
            shutil.copyfileobj(file_in, file_out)
    return f'{file_path.replace(".xls.gz","")}.xls'

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
    rose['time'] = pd.to_datetime(rose['time'], dayfirst=True)
    print(f'тестовая строка \n{rose.iloc[0, 0]}')
    try:
        reftime = rose.iloc[0, 0]
    except KeyError as e:
        print(f'**********\n{rose['time']}\n')
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
    file_path = opengz(file_path)
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
    file_path = opengz(file_path)
    df = clean_data(file_path)
    rs2 = create_additional_df(winds)
    windrose = smartrose_processing(df, winds, rs2)

    fig2 = px.line_polar(windrose, r='importance_wind',
                    theta='index', width = 600, height = 600, line_close=True, title = 'smartrose')
    fig2.update_traces(fill='toself')
    fig2.write_image(second_image_path) 
    return second_image_path


def temperature_processing (df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.iloc[::-1]
    sorted_df['U'] = pd.to_numeric(sorted_df['U'], errors='coerce')
    sorted_df['U'] = sorted_df['U']  - sorted_df['U'].min()
    sorted_df['U'] = sorted_df['U'].fillna(0).astype(int)
    sorted_df['T'] = pd.to_numeric(sorted_df['T'], errors='coerce')
    return sorted_df

custom_colors = [
    "#4B0082",  # Темно-синий (индиго)
    "#0000FF",  # Ярко-синий
    "#4682B4",  # Стальной синий
    "#5F9EA0",  # Бирюзовый синий
    "#708090",  # Серый с синим оттенком
    "#A9A9A9",  # Тёмно-серый
    "#D3D3D3",  # Светло-серый
]


def rain_processing (df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[::-1]
    rain_df = df[['time', 'W1', 'RRR', 'tR', 'sss']].copy()
    rain_df['RRR'] = pd.to_numeric(rain_df['RRR'], errors='coerce') 
    rain_df['RRR'] = rain_df['RRR'].fillna(0)
    rain_df['sss'] = pd.to_numeric(rain_df['sss'], errors='coerce')
    rain_df['sss'] = rain_df['sss'].interpolate(method='linear')
    rain_df['tR'] = pd.to_numeric(rain_df['tR'], errors='coerce')
    rain_df['time'] = pd.to_datetime(rain_df['time'], errors='coerce', dayfirst=True).dt.date
    rain_df['W1'] = rain_df['W1'].fillna('').apply(lambda x: (x[:20] + '...') if len(x) > 20 else x)
    grouped_rain_df = rain_df.groupby('time').agg({
        'W1': lambda x: x.mode()[0] if not x.mode().empty else np.nan,  # Мода по W1
        # 'RRR': 'sum',  # Сумма значений в RRR
        'RRR': lambda x: (x.sum() / rain_df.loc[x.index, 'tR'].sum()) * 24 if rain_df.loc[x.index, 'tR'].sum() != 0 else np.nan,  # Условие расчета RRR
        'sss': 'max'   # Максимальное значение в sss
        }).reset_index()

    print(grouped_rain_df)
    return grouped_rain_df

def create_rain (file_path: str, fourth_image_path: str) -> str:
    file_path = opengz(file_path)
    df = clean_data(file_path)
    rain_df = rain_processing(df)
    fig4 = px.bar(
        rain_df, x='time', y='RRR', color='W1', title="осадки",
        labels={"time": "время", "RRR": "количество осадков, мм", "W1": "тип осадков"},
        color_discrete_sequence=custom_colors

        )
    fig4.add_scatter(x=rain_df['time'], y=rain_df['sss'], mode='lines', name='высота снежного покрова, см', yaxis='y2',
                     line=dict(color='black'),  # Чёрный цвет линии
                     
                     )

    # Добавление второй оси Y
    fig4.update_layout(
        yaxis2=dict(
            title='высота снежного покрова, см',
            overlaying='y',
            side='right'
        )
        )
    fig4.update_layout(
    legend=dict(
        title="тип осадков",  # Заголовок для легенды (если нужно)
        x=1.22,          # Расположить легенду справа за границей графика
        xanchor="left",  # Привязка к левой границе позиции
        y=1,             # Расположить сверху
        yanchor="top",   # Привязка к верхней границе позиции        )
    )
    )

    fig4.write_image(fourth_image_path) 
    return fourth_image_path



def create_temperature (file_path: str, third_image_path: str) -> str:
    file_path = opengz(file_path)
    df = clean_data(file_path)
    sorted_df= temperature_processing(df)
    fig3 = px.scatter(sorted_df, x = 'time', y = 'T', size = sorted_df['U'], width= 1000, title = 'температура и влажность', color='T', 
                color_continuous_scale = px.colors.diverging.RdBu[::-1]
               
                )
    
    fig3.update_traces(marker=dict(line=dict(width=0.5, color='black')), showlegend=False)

    fig3.update_coloraxes(cmax=30, cmin = -10)
    fig3.write_image(third_image_path) 
    return third_image_path