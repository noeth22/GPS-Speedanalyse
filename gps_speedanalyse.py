"""
GPS Speedanalyse 
Autor: Michael Nöthen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, messagebox

class GPSAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPS Speedanalyse")

        # Ordnerauswahl-Button
        self.folder_btn = tk.Button(root, text="Ordner auswählen", command=self.select_folder)
        self.folder_btn.pack(pady=5)

        # Listbox für Dateiauswahl
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=10)
        self.listbox.pack(pady=5)

        # Button zum Plotten
        self.plot_btn = tk.Button(root, text="Vergleichen", command=self.plot_selected_files)
        self.plot_btn.pack(pady=5)

        self.folder_path = ""
        self.files = []

    def select_folder(self):
        """Wählt einen Ordner und listet alle CSV-Dateien auf."""
        self.folder_path = filedialog.askdirectory()
        if not self.folder_path:
            messagebox.showwarning("Warnung", "Kein Ordner ausgewählt!")
            return
        
        # Lade alle CSV-Dateien
        self.files = [f for f in os.listdir(self.folder_path) if f.endswith(".csv")]
        
        if not self.files:
            messagebox.showwarning("Warnung", "Keine CSV-Dateien im ausgewählten Ordner gefunden!")
            return

        # Liste aktualisieren
        self.listbox.delete(0, tk.END)
        for file in self.files:
            self.listbox.insert(tk.END, file)

    def plot_selected_files(self):
        """Liest ausgewählte Dateien ein, wählt die längste Zeitachse als Referenz und plottet die Daten."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Keine Dateien ausgewählt!")
            return

        selected_files = [self.files[i] for i in selected_indices]

        # Lade alle ausgewählten Dateien
        data_dict = {}
        for file in selected_files:
            filepath = os.path.join(self.folder_path, file)
            df = self.import_data(filepath)
            if df is not None:
                time, speed = self.extract_data(df)  # Jetzt wird die Methode innerhalb der Klasse aufgerufen
                if time is not None and speed is not None:
                    data_dict[file] = (time, speed)

        if not data_dict:
            messagebox.showwarning("Fehler", "Keine gültigen Daten zum Plotten gefunden!")
            return

        # Bestimme die Datei mit den meisten Zeitpunkten als Referenz
        reference_file = max(data_dict.keys(), key=lambda k: len(data_dict[k][0]))
        reference_time = data_dict[reference_file][0]

        print(f"Referenz-Zeitachse: {reference_file} mit {len(reference_time)} Einträgen.")

        # Plotte die Daten mit interpolierter Zeitachse
        plt.figure(figsize=(10, 5))

        for file, (time, speed) in data_dict.items():
            if file != reference_file:
                # Interpolierte Geschwindigkeitswerte auf die Referenz-Zeitachse umrechnen
                speed = np.interp(reference_time, time, speed)

            plt.plot(reference_time, speed, label=file)

        # Plot konfigurieren
        plt.xlabel("Time (s) - Normalisiert")
        plt.ylabel("Speed (m/s)")
        plt.title("Vergleich der GPS-Daten mit gemeinsamer Zeitachse")
        plt.legend()
        plt.grid()
        plt.show()

    def import_data(self, filepath):
        """Lädt eine CSV-Datei ein und gibt sie als DataFrame zurück."""
        try:
            df = pd.read_csv(filepath, delimiter=";", skiprows=2, header=0)
            df.columns = df.columns.str.strip()  # Spaltennamen bereinigen
            return df
        except Exception as e:
            print(f"Fehler beim Einlesen von {filepath}: {e}")
            return None

    def extract_data(self, df):
        """Extrahiert Zeit- und Geschwindigkeitswerte und konvertiert sie zu numerischen Typen."""
        try:
            df['Time'] = pd.to_numeric(df['Time'], errors='coerce')  # Konvertiere Time zu float
            df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce')  # Konvertiere Speed zu float
            df['Speed'] = df['Speed'].interpolate(method='polynomial', order=2)  # Interpoliert NaN-Werte

            # Entferne Zeilen mit NaN-Werten nach der Umwandlung
            df = df.dropna(subset=['Time', 'Speed'])

            time = df['Time'].to_numpy()
            speed = df['Speed'].to_numpy()
            return time, speed
        except KeyError as e:
            print(f"Fehlende Spalte: {e}")
            return None, None

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSAnalyzerApp(root)
    root.mainloop()
