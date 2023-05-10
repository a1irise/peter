import pandas as pd

from utils import get_data
from utils import cname

"""
setup
"""

pdf_path = '../input/прок 3-78-1-ж-2_2019-07-24 08-26-58.pdf'
octane_path = '../input/Октановые числа компонентов.xls'
octane_sheet = 'Октановые числа компонентов'

pdf_cols = ('component', 'time', 'area', 'height', 'concentration', 'units', 'sensor')
octane_cols = ('component', 'ioc', 'moc')
norm_cols = ('time', 'norm')

"""
get data
"""

df = get_data(pdf_path, octane_path, octane_sheet, pdf_cols, octane_cols)

"""
norm
"""

norm = []
total = 0

found = False
for i in df.index:
    if not found:
        entry = [df.time[i], 0]
        norm.append(entry)
    else:
        total += df.concentration[i]
    if df.component[i] == 'n-Butane':
        found = True

found = False
for i in df.index:
    if found:
        entry = [df.time[i], df.concentration[i] / total * 100]
        norm.append(entry)
    if df.component[i] == 'n-Butane':
        found = True

norm = pd.DataFrame(norm, columns=norm_cols)
df = pd.merge(df, norm, how='outer', on='time')

"""
TMP
"""

tmp = 0
for i in df.index:
    if cname(df.component[i], 'Trimethylpentane'):
        tmp += df.norm[i]

"""
DMH
"""

dmh = 0
for i in df.index:
    if cname(df.component[i], 'Dimethylhexane'):
        dmh += df.norm[i]

"""
Селективность С5-С9, % mass.
"""

selectivity = 0
start = False
for i in df.index:
    if df.component[i] == 'iso-Pentane':
        start = True
    if start:
        selectivity += df.norm[i]
    if df.component[i] == '2,6-Dimethylheptane' or df.component[i] == '2,5-Dimethylheptane':
        break

"""
Содержание алкилата С5+
"""

c5plus = 0
start = False
for i in df.index:
    if start:
        c5plus += df.concentration[i]
    if df.component[i] == 'iso-Pentane':
        c5plus += df.concentration[i]
        start = True

"""
Селективность С8, % mass.
"""

c8 = 0
for i in df.index:
    if cname(df.component[i], 'Trimethylpentane'):
        c8 += df.norm[i]
    if cname(df.component[i], 'Dimethylhexane'):
        c8 += df.norm[i]
    if cname(df.component[i], 'Methylheptane'):
        c8 += df.norm[i]
    if cname(df.component[i], 'Metylheptane'):
        c8 += df.norm[i]

"""
octane numbers
"""

ioc = 0
moc = 0
for i in df.index:
    ioc += df.norm[i] * df.ioc[i] / 100
    moc += df.norm[i] * df.moc[i] / 100

"""
Unidentified C5-C9
"""

unidentified_norm = 0
unidentified_concentration = 0
start = False
for i in df.index:
    if start and df.component[i] == 'X':
        unidentified_norm += df.norm[i]
        unidentified_concentration += df.concentration[i]
    if df.component[i] == 'iso-Pentane':
        start = True
    if df.component[i] == '2,6-Dimethylheptane' or df.component[i] == '2,5-Dimethylheptane':
        break
C5toC9 = pd.DataFrame({'component': 'Unidentified C5-C9',
                       'time': '',
                       'area': '',
                       'height': '',
                       'concentration': [unidentified_concentration],
                       'units': '',
                       'sensor': '',
                       'ioc': '',
                       'moc': '',
                       'norm': [unidentified_norm]})

"""
Hydrocarbons С10+
"""

hydrocarbons_norm = 0
hydrocarbons_concentration = 0
start = False
for i in df.index:
    if start and df.component[i] == 'X':
        hydrocarbons_norm += df.norm[i]
        hydrocarbons_concentration += df.concentration[i]
    if df.component[i] == '2,6-Dimethylheptane' or df.component[i] == '2,5-Dimethylheptane':
        start = True
C10plus = pd.DataFrame({'component': 'Hydrocarbons С10+',
                        'time': '',
                        'area': '',
                        'height': '',
                        'concentration': [hydrocarbons_concentration],
                        'units': '',
                        'sensor': '',
                        'ioc': '',
                        'moc': '',
                        'norm': [hydrocarbons_norm]})

"""
formatting
"""

extra = [['', 'Содержание TMP,% mass.', tmp],
         ['', 'Содержание DMH,% mass.', dmh],
         ['', 'Соотношение TMP/DMH', tmp / dmh],
         ['', '', ''],
         ['', 'Селективность С5-С9, % mass.', selectivity],
         ['', 'Содержание алкилата C5+,% mass.', c5plus],
         ['', 'Селективность С8, % mass.', c8],
         ['', '', ''],
         ['', 'ИОЧ', ioc],
         ['', 'МОЧ', moc]]
extra_df = pd.DataFrame(extra)


df = df[df.component != 'X']
df = df.sort_values(by='time', key=lambda x: x.astype('float64'), ignore_index=True)
df = df.reset_index(drop=True)

df = pd.concat([df, C5toC9, C10plus], axis=0, ignore_index=True)

main = df[['time', 'component', 'concentration', 'norm']]
main = main.set_axis(['Время, мин', 'Компонент', 'Концентрация, % mass.', 'Нормализованный состав (Алкилат), % mass.'], axis=1)

main = pd.concat([main, extra_df], axis=1)
main.to_excel('../reports/прок 3-78-1-ж-2_2019-07-24 08-26-58.xlsx')
