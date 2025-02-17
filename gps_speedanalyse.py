"""
GPS Speedanalyse 
Autor: Michael Nöthen
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.widgets import Slider

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
        self.data_dict = {}  # Speichert Daten der Athleten
        self.offsets = {}  # Speichert die aktuellen Verschiebungen

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
        self.data_dict.clear()
        self.offsets.clear()

        # Lade alle ausgewählten Dateien
        for file in selected_files:
            filepath = os.path.join(self.folder_path, file)
            df = self.import_data(filepath)
            if df is not None:
                time, speed = self.extract_data(df)
                if time is not None and speed is not None:
                    self.data_dict[file] = (time, speed)
                    self.offsets[file] = 0  # Initial kein Offset

        if not self.data_dict:
            messagebox.showwarning("Fehler", "Keine gültigen Daten zum Plotten gefunden!")
            return

        # Initialisiere das interaktive Plot-Fenster
        self.create_interactive_plot()

    def create_interactive_plot(self):
        """Erstellt das Matplotlib-Fenster mit Slidern zur Verschiebung der X-Achse."""
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        plt.subplots_adjust(bottom=0.3)  # Platz für die Slider

        self.lines = {}  # Speichert die geplotteten Linien für spätere Updates
        self.sliders = {}  # Speichert die Slider für jede Datei

        # Plotte initial die Daten
        for file, (time, speed) in self.data_dict.items():
            line, = self.ax.plot(time, speed, label=file)
            self.lines[file] = line

        self.ax.set_xlabel("Zeit (s)")
        self.ax.set_ylabel("Speed (km/h)")
        self.ax.set_title("Vergleich der GPS-Daten mit interaktiver Verschiebung")
        self.ax.legend()
        self.ax.grid()

        # Erstelle Slider für jedes File
        slider_ax_start = 0.15
        for i, file in enumerate(self.data_dict.keys()):
            slider_ax = plt.axes([0.1, slider_ax_start - i * 0.05, 0.65, 0.03])  # Position der Slider
            slider = Slider(slider_ax, file, -5.0, 5.0, valinit=0, valstep=0.1)
            slider.on_changed(lambda val, f=file: self.update_plot(f, val))
            self.sliders[file] = slider

        plt.show()

    def update_plot(self, file, offset):
        """Aktualisiert den Plot, wenn ein Slider bewegt wird."""
        self.offsets[file] = offset
        time, speed = self.data_dict[file]

        # Verschiebe die Zeitachse
        new_time = time + offset
        self.lines[file].set_xdata(new_time)

        # Neuzeichnen
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()

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
