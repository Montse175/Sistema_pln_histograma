import tkinter as tk
from tkinter import ttk
import random

class AlgoritmoGeneticoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmo Genético")

        # Variables
        self.modo = tk.StringVar(value="manual")
        self.tamano_poblacion = tk.StringVar()
        self.longitud_cromosoma = tk.StringVar(value="16")
        self.num_generaciones = tk.StringVar()
        self.num_cruces = tk.StringVar()
        self.punto_cruce = tk.StringVar()
        self.funcion_objetivo = tk.StringVar()
        self.criterio_exito = tk.StringVar()
        self.valor_maximo = tk.StringVar()
        self.valor_minimo = tk.StringVar()
        self.punto_cruce_fijo = None  # para guardar el punto de corte aleatorio único

        # UI
        self.crear_widgets()
        self.actualizar_visibilidad_campos()

    def crear_widgets(self):
        # Modo
        ttk.Label(self.root, text="Modo:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(self.root, text="Manual", variable=self.modo, value="manual",
                        command=self.actualizar_visibilidad_campos).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(self.root, text="Aleatorio", variable=self.modo, value="aleatorio",
                        command=self.actualizar_visibilidad_campos).grid(row=0, column=2, sticky="w")

        # Campos principales
        ttk.Label(self.root, text="Tamaño de Población:").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.tamano_poblacion).grid(row=1, column=1)

        ttk.Label(self.root, text="Longitud de Cromosoma:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.longitud_cromosoma, state="disabled").grid(row=2, column=1)

        ttk.Label(self.root, text="Número de Generaciones:").grid(row=3, column=0, sticky="w")
        self.entry_num_gen = ttk.Entry(self.root, textvariable=self.num_generaciones)
        self.entry_num_gen.grid(row=3, column=1)

        ttk.Label(self.root, text="Número de Cruces por Generación:").grid(row=4, column=0, sticky="w")
        self.entry_num_cruces = ttk.Entry(self.root, textvariable=self.num_cruces)
        self.entry_num_cruces.grid(row=4, column=1)

        ttk.Label(self.root, text="Punto de Cruce:").grid(row=5, column=0, sticky="w")
        self.entry_punto_cruce = ttk.Entry(self.root, textvariable=self.punto_cruce)
        self.entry_punto_cruce.grid(row=5, column=1)

        ttk.Label(self.root, text="Función de Objetivo:").grid(row=6, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.funcion_objetivo).grid(row=6, column=1)

        ttk.Label(self.root, text="Criterio de Éxito:").grid(row=7, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.criterio_exito).grid(row=7, column=1)

        ttk.Label(self.root, text="Valor Máximo:").grid(row=8, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.valor_maximo).grid(row=8, column=1)

        ttk.Label(self.root, text="Valor Mínimo:").grid(row=9, column=0, sticky="w")
        ttk.Entry(self.root, textvariable=self.valor_minimo).grid(row=9, column=1)

        # Botón iniciar
        ttk.Button(self.root, text="Iniciar", command=self.iniciar).grid(row=10, column=0, columnspan=2, pady=10)

    def actualizar_visibilidad_campos(self):
        modo = self.modo.get()
        if modo == "aleatorio":
            # Ocultar los campos que no se usan en aleatorio
            self.entry_num_gen.config(state="disabled")
            self.entry_num_cruces.config(state="disabled")
            self.entry_punto_cruce.config(state="disabled")
            self.num_generaciones.set("")
            self.num_cruces.set("")
            self.punto_cruce.set("")
        else:
            # Habilitar en modo manual
            self.entry_num_gen.config(state="normal")
            self.entry_num_cruces.config(state="normal")
            self.entry_punto_cruce.config(state="normal")

    def iniciar(self):
        longitud = 16  # fijo de 1 a 15
        if self.modo.get() == "aleatorio":
            # Generar un solo punto de cruce aleatorio que será fijo para todas las generaciones
            if self.punto_cruce_fijo is None:
                self.punto_cruce_fijo = random.randint(1, longitud - 1)
            print(f"Punto de cruce fijo generado: {self.punto_cruce_fijo}")
        else:
            # Modo manual usa el que se ingrese
            self.punto_cruce_fijo = int(self.punto_cruce.get()) if self.punto_cruce.get().isdigit() else None
            print(f"Punto de cruce manual: {self.punto_cruce_fijo}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgoritmoGeneticoGUI(root)
    root.mainloop()
