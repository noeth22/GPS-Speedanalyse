"""
GPS Speedanalyse mit Mehrfachdateiauswahl
Autor: Michael Nöthen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# importiere Daten aus einer Datei
def import_data(filepath):
    try:
        df = pd.read_csv(filepath, delimiter=";", skiprows=2, header=0)  # Header ab Zeile 3
        df.columns = df.columns.str.strip()  # Spaltennamen bereinigen
        print(f'Datei erfolgreich eingelesen: {os.path.basename(filepath)}')
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

# Extrahiere Koordinaten in Arrays
def extract_data(df):
    try:
        time = df['Time']
        speed = df['Speed'].interpolate(method='polynomial', order=2)  # Interpoliert NaN-Werte
        return time, speed
    except KeyError as e:
        print(f'Fehlende Spalte: {e}')
        return None, None

# GUI zur Auswahl des Ordners mit CSV-Dateien
def select_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected

# GUI zur Auswahl von mehreren Dateien aus einem Ordner
def select_files(files):
    root = tk.Tk()
    root.withdraw()  # Hauptfenster verstecken
    selected_files = filedialog.askopenfilenames(title="Wähle Dateien zum Vergleich", filetypes=[("CSV-Dateien", "*.csv")], initialdir=files)
    return selected_files

# Hauptprogramm: Lese Ordner ein und wähle Dateien aus
def main():
    print("Wähle den Ordner mit den GPS-CSV-Dateien:")
    folder_path = select_folder()
    
    if not folder_path:
        print("Kein Ordner ausgewählt.")
        return

    # Lade alle CSV-Dateien im Ordner
    all_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".csv")]
    
    if not all_files:
        print("Keine CSV-Dateien im ausgewählten Ordner gefunden.")
        return
    
    print(f"{len(all_files)} CSV-Dateien gefunden.")
    
    # GUI zur Auswahl der Dateien
    selected_files = select_files(folder_path)
    
    if not selected_files:
        print("Keine Dateien ausgewählt.")
        return

    print(f"{len(selected_files)} Dateien zum Vergleich ausgewählt.")

    # Plotte die Daten der ausgewählten Dateien
    plt.figure(figsize=(10, 5))

    for file in selected_files:
        df = import_data(file)
        if df is not None:
            time, speed = extract_data(df)
            if time is not None and speed is not None:
                plt.plot(time, speed, label=os.path.basename(file))  # Datei als Label

    # Formatierung des Plots
    plt.xlabel("Time (s)")
    plt.ylabel("Speed (km/h)")
    plt.title("Vergleich der GPS-Daten")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
