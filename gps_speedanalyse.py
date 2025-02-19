"""
GPS Speedanalyse mit interaktiver X-Achsen-Synchronisation
Autor: Michael Nöthen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.widgets import Slider, Button, TextBox

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
        self.sync_entries = {}  # Eingabefelder für Synchronisationszeiten
        self.sync_times = {}  # Speichert die Synchronisationszeiten

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
        """Liest ausgewählte Dateien ein und plottet sie mit interaktiver Synchronisation."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Keine Dateien ausgewählt!")
            return

        selected_files = [self.files[i] for i in selected_indices]
        self.data_dict.clear()
        self.offsets.clear()
        self.sync_times.clear()

        # Lade alle ausgewählten Dateien
        for file in selected_files:
            filepath = os.path.join(self.folder_path, file)
            df = self.import_data(filepath)
            if df is not None:
                time, speed = self.extract_data(df)
                if time is not None and speed is not None and len(time) > 0:
                    self.data_dict[file] = (time, speed)
                    self.offsets[file] = 0  # Initial kein Offset
                    self.sync_times[file] = time[0]  # Standardmäßig erste Zeit als Sync-Zeit

        if not self.data_dict:
            messagebox.showwarning("Fehler", "Keine gültigen Daten zum Plotten gefunden!")
            return

        # Initialisiere das interaktive Plot-Fenster mit Slidern & Eingabefeldern
        self.create_interactive_plot()

    def create_interactive_plot(self):
        """Erstellt das Matplotlib-Fenster mit Slidern zur Verschiebung der X-Achse und Synchronisationseingaben."""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.4)  # Platz für die Slider & Eingaben

        self.lines = {}  # Speichert die geplotteten Linien für spätere Updates
        self.sliders = {}  # Speichert die Slider für jede Datei
        self.sync_entries = {}  # Eingabefelder für die Synchronisationszeiten

        # Plotte initial die Daten
        for file, (time, speed) in self.data_dict.items():
            line, = self.ax.plot(time, speed, label=file)
            self.lines[file] = line

        self.ax.set_xlabel("Zeit (s)")
        self.ax.set_ylabel("Speed (km/h)")
        self.ax.set_title("Speedanalyse mit Synchronisation")
        self.ax.legend()
        self.ax.grid()

        # Erstelle Slider & Eingabefelder für jedes File
        slider_ax_start = 0.25
        entry_ax_start = 0.25

        for i, file in enumerate(self.data_dict.keys()):
            # Matplotlib-Achse für die Slider
            slider_ax = plt.axes([0.1, slider_ax_start - i * 0.05, 0.5, 0.03])
            slider = Slider(slider_ax, file, -5.0, 5.0, valinit=0, valstep=0.1)
            slider.on_changed(lambda val, f=file: self.update_plot(f, val))
            self.sliders[file] = slider

            # Matplotlib-Achse für die TextBox
            text_ax = plt.axes([0.7, slider_ax_start - i * 0.05, 0.1, 0.03])
            text_box = TextBox(text_ax, f"Sync {i+1}", initial=str(self.sync_times[file]))
            text_box.on_submit(lambda text, f=file: self.update_sync_time(f, text))
            self.sync_entries[file] = text_box

        # Synchronisierungs-Button im Plot
        sync_ax = plt.axes([0.8, 0.05, 0.15, 0.05])
        sync_button = Button(sync_ax, "Synchronisieren")
        sync_button.on_clicked(self.synchronize_plots)

        plt.show()

    def update_plot(self, file, offset):
        """Aktualisiert den Plot, wenn ein Slider bewegt wird."""
        if file not in self.data_dict:
            print(f"⚠️ Fehler: Datei {file} nicht in self.data_dict!")
            return

        self.offsets[file] = offset
        time, speed = self.data_dict[file]

        # Verschiebe die Zeitachse um den Offset
        new_time = time + offset
        self.lines[file].set_xdata(new_time)

        # Bestimme den Geschwindigkeitswert am neuen Synchronisationszeitpunkt
        sync_index = np.argmin(abs(new_time - new_time[0]))
        sync_speed = np.interp(new_time[0], new_time, speed)
        speed = speed - sync_speed

        # Plot neu skalieren und aktualisieren
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()


    def update_sync_time(self, file, text):
        """Aktualisiert die eingegebene Synchronisationszeit."""
        try:
            self.sync_times[file] = float(text)  # Konvertiere Eingabe zu float
        except ValueError:
            messagebox.showwarning("Fehler", f"Ungültige Eingabe für {file}. Bitte eine Zahl eingeben.")

    def synchronize_plots(self, event=None):
        """Synchronisiert die Datenreihen und setzt die Geschwindigkeiten auf Differenzen."""
        if not self.data_dict:
            messagebox.showwarning("Fehler", "Keine Daten zum Synchronisieren verfügbar!")
            return

        min_sync_time = min(self.sync_times.values())
        plt.figure(figsize=(10, 6))
        
        for file, (time, speed) in self.data_dict.items():
            offset = min_sync_time - self.sync_times[file]
            new_time = time + offset

            # Bestimme den Geschwindigkeitswert am Synchronisationszeitpunkt
            sync_index = np.argmin(abs(new_time - min_sync_time))
            sync_speed = np.interp(min_sync_time, new_time, speed)
            speed = speed - sync_speed

            plt.plot(new_time, speed, label=file)
        
        # Füge eine vertikale Linie am Synchronisationszeitpunkt hinzu
        plt.axvline(x=min_sync_time, color='red', linestyle='--', label='Synchronisationspunkt')

        # Plot-Konfiguration
        plt.xlabel("Zeit (s) - Normalisiert")
        plt.ylabel("Geschwindigkeitsdifferenz (m/s)")
        plt.title("Vergleich der GPS-Daten mit gemeinsamer Zeitachse")
        plt.legend()
        plt.grid()
        plt.show()

    def import_data(self, filepath):
        """Lädt eine CSV-Datei ein und gibt sie als DataFrame zurück."""
        try:
            df = pd.read_csv(filepath, delimiter=";", skiprows=2, header=0)
            df.columns = df.columns.str.strip()
            return df
        except Exception:
            return None

    def extract_data(self, df):
        """Extrahiert Zeit- und Geschwindigkeitswerte."""

        if 'Time' not in df.columns or 'Speed' not in df.columns:
            print("Fehler: 'Time' und/oder 'Speed' fehlen!")
            return np.array([]), np.array([])
        
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
        df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce').interpolate()

        #df.dropna(subset=['Time', 'Speed'], inplace=True) # entfernt NaN-Werte

        return df['Time'].to_numpy(), df['Speed'].to_numpy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSAnalyzerApp(root)
    root.mainloop()