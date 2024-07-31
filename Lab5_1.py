import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Завдання 1
url = 'https://uk.wikipedia.org/wiki/%D0%9D%D0%B0%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%BD%D1%8F_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8#%D0%9D%D0%B0%D1%80%D0%BE%D0%B4%D0%B6%D1%83%D0%B2%D0%B0%D0%BD%D1%96%D1%81%D1%82%D1%8C'
dfs = pd.read_html(url)

# Відобразити перші рядки таблиці
df = dfs[21]
print(df.head())

# Кількість рядків і стовпців
print('Розмір датафрейму:', df.shape)

# Замініть значення "-" в таблиці значеннями NaN
df = df.replace('-', np.nan)

# Типи всіх стовпців
print(df.dtypes)

# Замініть типи нечислових стовпців числовими стовпцями
df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# Скільки пропусків у кожному стовпці
print(df.isnull().sum())

# Видалити дані для всієї країни з таблиці в останньому рядку таблиці
df = df[:-1]

# Заміна відсутніх даних у стовпцях середніми значеннями для цих стовпців
df.fillna(df.mean(), inplace=True)

# Отримайте список регіонів, де народжуваність у 2019 році була вищою за середню по Україні
higher_than_average = df[df['2019'] > df['2019'].mean()]
print(higher_than_average['Регіон'].tolist())

# В якому регіоні була найвища народжуваність у 2014 році?
max_birth_rate_2014 = df['2014'].max()
region_with_max_birth_rate_2014 = df.loc[df['2014'] == max_birth_rate_2014, 'Регіон'].values[0]
print('Регіон з найвищою народжуваністю у 2014 році:'), region_with_max_birth_rate_2014
