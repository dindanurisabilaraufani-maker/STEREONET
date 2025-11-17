import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import mplstereonet
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GeoPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plot Strike–Dip (2D & 3D)")

        input_frame = ttk.LabelFrame(root, text="Input Data Geologi", padding=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Strike (°):").grid(row=0, column=0, sticky="w")
        self.strike_entry = ttk.Entry(input_frame, width=10)
        self.strike_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Dip (°):").grid(row=1, column=0, sticky="w")
        self.dip_entry = ttk.Entry(input_frame, width=10)
        self.dip_entry.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Mode Plot:").grid(row=2, column=0, sticky="w")
        self.mode_var = tk.StringVar()
        self.mode_var.set("2D Stereonet")
        mode_menu = ttk.OptionMenu(input_frame, self.mode_var, "2D Stereonet", "2D Stereonet", "3D Globe")
        mode_menu.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(input_frame, text="Plot", command=self.plot_data).grid(row=0, column=2, rowspan=3, padx=10)

        self.fig = None
        self.canvas = None

    def clear_plot(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None

    def plot_data(self):
        try:
            strike = float(self.strike_entry.get())
            dip = float(self.dip_entry.get())
        except ValueError:
            print("Masukkan angka valid!")
            return

        self.clear_plot()

        mode = self.mode_var.get()

        if mode == "2D Stereonet":
            self.plot_2d(strike, dip)
        else:
            self.plot_3d(strike, dip)

    def plot_2d(self, strike, dip):
        self.fig, self.ax = mplstereonet.subplots(figsize=(6, 6))

        self.ax.set_longitude_grid(10)
        self.ax.set_latitude_grid(10)
        self.ax.grid(linewidth=0.6, color='gray', linestyle='--')

        for label in self.ax.get_yticklabels():
            label.set_visible(False)

        # ==============================
        # FIX: Jarak teks kompas diperjauh (2.2)
        # ==============================
        compass = {0: 'N', 90: 'E', 180: 'S', 270: 'W'}
        radius_label = 2.2   # <--- nilai baru agar tidak mepet

        for az, lab in compass.items():
            ang = np.radians(az)
            x = np.sin(ang)
            y = np.cos(ang)
            self.ax.text(x * radius_label, y * radius_label, lab,
                         ha='center', va='center',
                         fontsize=11, fontweight='bold')

        self.ax.plane(strike, dip, color='red', linewidth=2)
        self.ax.pole(strike, dip, marker='o', color='blue', markersize=6)

        self.ax.set_title(f"Stereonet Strike={strike}°, Dip={dip}°",
                          y=1.05, fontsize=11, fontweight='bold')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10)

    def plot_3d(self, strike, dip):
        from mpl_toolkits.mplot3d import Axes3D

        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.ax.set_box_aspect([1, 1, 1])
        self.ax.set_axis_off()

        u = np.linspace(0, 2*np.pi, 72)
        v = np.linspace(0, np.pi, 36)

        for i in range(0, len(u), 6):
            self.ax.plot(np.cos(u[i]) * np.sin(v),
                         np.sin(u[i]) * np.sin(v),
                         np.cos(v),
                         color='gray', lw=0.6)

        for j in range(1, len(v)-1, 4):
            self.ax.plot(np.cos(u) * np.sin(v[j]),
                         np.sin(u) * np.sin(v[j]),
                         np.ones_like(u) * np.cos(v[j]),
                         color='gray', lw=0.6)

        compass_labels = {'N': (0, 1.25, 0), 'S': (0, -1.25, 0),
                          'E': (1.25, 0, 0), 'W': (-1.25, 0, 0)}
        for lab, (x, y, z) in compass_labels.items():
            self.ax.text(x, y, z, lab, color='red',
                         fontsize=12, fontweight='bold',
                         ha='center', va='center')

        for az in np.arange(0, 360, 10):
            ang = np.radians(az)
            x = 1.15 * np.sin(ang)
            y = 1.15 * np.cos(ang)
            self.ax.text(x, y, 0, f"{az}°", fontsize=7, ha='center')

        strike_rad = np.radians(strike)
        dip_rad = np.radians(dip)
        nx = np.sin(dip_rad) * np.sin(strike_rad)
        ny = np.sin(dip_rad) * np.cos(strike_rad)
        nz = np.cos(dip_rad)

        phi = np.linspace(0, 2*np.pi, 200)
        plane_x = np.cos(phi)
        plane_y = np.sin(phi)
        plane_z = (-nx * plane_x - ny * plane_y) / nz
        r = np.sqrt(plane_x**2 + plane_y**2 + plane_z**2)
        plane_x /= r
        plane_y /= r
        plane_z /= r

        self.ax.plot(plane_x, plane_y, plane_z, color='blue', lw=2)
        self.ax.quiver(0, 0, 0, nx, ny, nz, color='green', length=1.0)

        self.ax.set_title(f"Globe 3D Strike={strike}°, Dip={dip}°",
                          fontsize=12, fontweight='bold', y=1.05)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = GeoPlotApp(root)
    root.mainloop()
