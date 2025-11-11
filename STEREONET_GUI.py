import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Globe3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot Strike & Dip pada Globe 3D dengan Derajat")

        # Frame input
        input_frame = ttk.LabelFrame(root, text="Input Data Geologi", padding=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Strike (°):").grid(row=0, column=0, sticky="w")
        self.strike_entry = ttk.Entry(input_frame, width=10)
        self.strike_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Dip (°):").grid(row=1, column=0, sticky="w")
        self.dip_entry = ttk.Entry(input_frame, width=10)
        self.dip_entry.grid(row=1, column=1, padx=5)

        ttk.Button(input_frame, text="Plot", command=self.plot_data).grid(row=0, column=2, rowspan=2, padx=10)

        # Buat figure globe pertama
        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.create_globe()

        # Integrasi dengan Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10)

    def create_globe(self, title="Jaring Bola 3D"):
        """Buat jaring bola 3D dengan arah mata angin dan label derajat"""
        self.ax.clear()
        self.ax.set_box_aspect([1, 1, 1])
        self.ax.set_axis_off()

        # Grid bola
        u = np.linspace(0, 2 * np.pi, 72)
        v = np.linspace(0, np.pi, 36)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones_like(u), np.cos(v))

        # Garis bujur
        for i in range(0, len(u), 6):
            self.ax.plot(np.cos(u[i]) * np.sin(v),
                         np.sin(u[i]) * np.sin(v),
                         np.cos(v),
                         color='gray', lw=0.6)

        # Garis lintang
        for j in range(1, len(v) - 1, 4):
            self.ax.plot(np.cos(u) * np.sin(v[j]),
                         np.sin(u) * np.sin(v[j]),
                         np.ones_like(u) * np.cos(v[j]),
                         color='gray', lw=0.6)

        # Arah mata angin utama
        compass_labels = {'N': (0, 1.25, 0), 'S': (0, -1.25, 0),
                          'E': (1.25, 0, 0), 'W': (-1.25, 0, 0)}
        for label, (x, y, z) in compass_labels.items():
            self.ax.text(x, y, z, label, color='red', fontsize=12,
                         fontweight='bold', ha='center', va='center')

        # Label derajat keliling (setiap 10°)
        for az in np.arange(0, 360, 10):
            ang = np.radians(az)
            x = 1.15 * np.sin(ang)
            y = 1.15 * np.cos(ang)
            z = 0  # di ekuator
            self.ax.text(x, y, z, f"{az}°", color='black',
                         fontsize=7, ha='center', va='center')

        self.ax.set_title(title, fontsize=12, fontweight='bold', y=1.05)

    def plot_data(self):
        """Plot bidang strike & dip"""
        try:
            strike = float(self.strike_entry.get())
            dip = float(self.dip_entry.get())
        except ValueError:
            print("⚠️ Masukkan angka strike dan dip yang valid!")
            return

        # Gambar ulang globe dasar dulu
        self.create_globe(title=f"Globe 3D Strike={strike}°, Dip={dip}°")

        # --- Hitung bidang dari strike & dip ---
        strike_rad = np.radians(strike)
        dip_rad = np.radians(dip)

        # Normal bidang
        nx = np.sin(dip_rad) * np.sin(strike_rad)
        ny = np.sin(dip_rad) * np.cos(strike_rad)
        nz = np.cos(dip_rad)

        # Buat bidang (lingkaran besar)
        phi = np.linspace(0, 2*np.pi, 200)
        plane_x = np.cos(phi)
        plane_y = np.sin(phi)
        plane_z = (-nx * plane_x - ny * plane_y) / nz

        # Normalisasi biar tetap di permukaan bola
        r = np.sqrt(plane_x**2 + plane_y**2 + plane_z**2)
        plane_x, plane_y, plane_z = plane_x / r, plane_y / r, plane_z / r

        # Plot bidang dan vektor normal
        self.ax.plot(plane_x, plane_y, plane_z, color='blue', lw=2,
                     label=f"Strike={strike}°, Dip={dip}°")
        self.ax.quiver(0, 0, 0, nx, ny, nz, color='green', length=1.0,
                       arrow_length_ratio=0.1, label="Normal")

        self.ax.legend(loc='upper left', fontsize=8)
        self.canvas.draw_idle()  # redraw figure dalam Tkinter


# --- Jalankan program utama ---
if __name__ == "__main__":
    root = tk.Tk()
    app = Globe3DApp(root)
    root.mainloop()
