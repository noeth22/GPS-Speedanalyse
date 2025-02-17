"""
GPS Speedanalyse
Autor: Michael Nöthen

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# importiere Daten
def import_data(filepath):
    try:
        df = pd.read_csv(filepath, delimiter=";", skiprows=2, header=0) # header=0 -> erste nicht übersprungene Zeile ist Header
        print(f'Datei erfolgreich eingelesen')
        return df
    except FileNotFoundError as e:
        print(f'Datei wurde nicht gefunden: {e}')
        return None
    except pd.errors.EmptyDataError as e:
        print(f'Die Datei ist leer: {e}')
        return None
    except Exception as e:
        print(f'Fehler beim Einlesen: {e}')
        return None

# extrahiere Koordinaten in Arrays
def extract_data(df):
    try:
        # Bereinige Spaltennamen
        df.columns = df.columns.str.strip()

        # Extrahiere Zeit und Geschwindigkeit
        time = df['Time']
        speed = df['Speed'].interpolate(method='polynomial', order=2)
        return time, speed
    except KeyError as e:
        print(f'Fehlende Spalte: {e}')
        return None, None
    

######################################################
#################### Main ############################

# Lies Rohdaten ein
print('Longines Export-Datei hierherziehen: ')
filepath = input().strip().strip('"').strip('{}')

# Importiere Daten
df = import_data(filepath)
time, speed = extract_data(df)

# Plotte Daten
plt.figure()
plt.plot(time,speed)
plt.show()