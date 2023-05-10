import PyPDF2 as pp
import pandas as pd
import numpy as np


def get_data(pdf_path, octane_path, octane_sheet, pdf_cols, octane_cols):

    """
    read pdf
    """

    pdf = open(pdf_path, 'rb')
    reader = pp.PdfReader(pdf)
    data = []

    for i in range(len(reader.pages)):
        page = reader.pages[i]
        lines = page.extract_text().split('\n')

        for j in range(len(lines)):
            line = lines[j]
            line = ' '.join(line.split())

            if not (len(line) > 5 and (line.endswith('ПИД-1')
                                       or line.endswith('ПИД-2')
                                       or line.endswith('ДТП-1')
                                       or line.endswith('ДТП-2'))):
                continue

            has_units = False
            if '%' in line:
                has_units = True

            line = line.split(' ')
            has_component = False
            if not line[0].replace('.', '', 1).isdigit():
                has_component = True

            sensor = line.pop()
            if has_units:
                temp = line.pop()
                units = line.pop() + ' ' + temp
            else:
                units = ''
            concentration = float(line.pop())
            height = float(line.pop())
            area = float(line.pop())
            time = float(line.pop())
            if has_component:
                component = ' '.join(line)
            else:
                component = 'X'

            entry = [component, time, area, height, concentration, units, sensor]
            data.append(entry)

    df = pd.DataFrame(data, columns=pdf_cols)
    pdf.close()

    """
    throw out minority sensors
    """

    sensor_counts = df.value_counts("sensor")
    majority = sensor_counts.index[0]
    df = df[df.sensor == majority]

    """
    add octane
    """

    octane = pd.read_excel(octane_path, sheet_name=octane_sheet, skiprows=range(0, 3), usecols='B:D')
    octane = octane.set_axis(octane_cols, axis=1)
    df = pd.merge(df, octane, how='outer', on='component')

    """
    add default octane values
    """

    default_ioc = octane.iloc[-1][1]
    default_moc = octane.iloc[-1][2]
    df.ioc = df.ioc.replace(np.nan, default_ioc)
    df.moc = df.moc.replace(np.nan, default_moc)

    """
    formatting
    """

    df = df[pd.to_numeric(df['time'], errors='coerce').notnull()]
    df = df.sort_values(by='time', key=lambda x: x.astype('float64'), ignore_index=True)
    df = df.reset_index(drop=True)

    """
    output
    """

    return df


def cname(component, name):
    if '&' in component and name in component.split('&')[0]:
        return True
    if '&' not in component and name in component:
        return True
    return False
