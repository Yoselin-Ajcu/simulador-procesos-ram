import tkinter as tk
from tkinter import ttk, messagebox
import threading

from main import SimuladorRAM


# ============================================================
# CONFIGURACIÓN
# ============================================================

RAM_TOTAL = 1024

simulador = SimuladorRAM(RAM_TOTAL)

hilo = threading.Thread(
    target=simulador.tick_simulacion,
    daemon=True
)
hilo.start()


# ============================================================
# FUNCIONES
# ============================================================

def centrar_ventana(ventana, ancho, alto, x_extra=0):
    """Centra una ventana en la pantalla."""

    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho - ancho) // 2 + x_extra
    y = (pantalla_alto - alto) // 2

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def actualizar():
    """Actualiza RAM y procesos."""

    with simulador.lock:
        usada = RAM_TOTAL - simulador.ram_disponible

        ram_total.config(text=f"{RAM_TOTAL} MB")
        ram_usada.config(text=f"{usada} MB")
        ram_libre.config(text=f"{simulador.ram_disponible} MB")

        porcentaje = usada / RAM_TOTAL * 100
        barra_ram["value"] = porcentaje
        porcentaje_label.config(text=f"{porcentaje:.1f}% utilizada")

        # Procesos en ejecución
        lista_ejecucion.delete(0, tk.END)

        for p in simulador.ejecucion:
            lista_ejecucion.insert(
                tk.END,
                f"PID {p.pid}   |   {p.nombre}   |   "
                f"{p.ram} MB   |   {p.duracion}s"
            )

        # Procesos en cola
        lista_cola.delete(0, tk.END)

        for p in simulador.cola_espera:
            lista_cola.insert(
                tk.END,
                f"PID {p.pid}   |   {p.nombre}   |   "
                f"{p.ram} MB   |   {p.duracion}s"
            )

    ventana.after(500, actualizar)


def crear_proceso():
    """Abre la ventana para crear un proceso."""

    if ventana_proceso_abierta():
        return

    crear_ventana()


def ventana_proceso_abierta():
    """Evita abrir varias ventanas de creación."""

    for ventana_hija in ventana.winfo_children():

        if getattr(ventana_hija, "es_ventana_proceso", False):
            ventana_hija.lift()
            return True

    return False


def crear_ventana():
    """Construye la ventana de creación de procesos."""

    nueva = tk.Toplevel(ventana)

    nueva.es_ventana_proceso = True

    nueva.title("Crear proceso")
    nueva.resizable(False, False)

    centrar_ventana(nueva, 350, 330, 500)

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    ttk.Label(
        nueva,
        text="CREAR PROCESO",
        style="Titulo.TLabel"
    ).pack(pady=(20, 15))

    # --------------------------------------------------------
    # CAMPOS
    # --------------------------------------------------------

    marco = ttk.Frame(nueva, padding=20)
    marco.pack(fill="both")

    ttk.Label(
        marco,
        text="Nombre:"
    ).pack(anchor="w")

    nombre = ttk.Entry(marco)
    nombre.pack(fill="x", pady=(3, 12))

    ttk.Label(
        marco,
        text="Memoria requerida (MB):"
    ).pack(anchor="w")

    memoria = ttk.Entry(marco)
    memoria.pack(fill="x", pady=(3, 12))

    ttk.Label(
        marco,
        text="Duración (segundos):"
    ).pack(anchor="w")

    duracion = ttk.Entry(marco)
    duracion.pack(fill="x", pady=(3, 15))

    # --------------------------------------------------------
    # CREAR
    # --------------------------------------------------------

    def guardar():

        try:
            ram = int(memoria.get())
            tiempo = int(duracion.get())

        except ValueError:
            messagebox.showerror(
                "Error",
                "La memoria y la duración deben ser números.",
                parent=nueva
            )
            return

        if ram <= 0 or ram > RAM_TOTAL:

            messagebox.showerror(
                "Error",
                f"La memoria debe estar entre 1 y {RAM_TOTAL} MB.",
                parent=nueva
            )
            return

        if tiempo <= 0:

            messagebox.showerror(
                "Error",
                "La duración debe ser mayor que 0 segundos.",
                parent=nueva
            )
            return

        simulador.agregar_proceso(
            nombre.get(),
            ram,
            tiempo
        )

        nueva.destroy()

    ttk.Button(
        nueva,
        text="CREAR PROCESO",
        command=guardar
    ).pack(pady=5)


def salir():
    """Cierra el simulador."""

    if messagebox.askyesno(
        "Salir",
        "¿Desea salir del simulador?"
    ):
        simulador.running = False
        ventana.destroy()


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

ventana = tk.Tk()

ventana.title(
    "Simulador de Gestión de Procesos y Memoria RAM"
)

ventana.resizable(False, False)

centrar_ventana(ventana, 900, 620)


# ============================================================
# ESTILOS
# ============================================================

estilo = ttk.Style()

estilo.configure(
    "Titulo.TLabel",
    font=("Arial", 18, "bold")
)

estilo.configure(
    "Encabezado.TLabel",
    font=("Arial", 11, "bold")
)

estilo.configure(
    "Info.TLabel",
    font=("Arial", 14, "bold")
)

estilo.configure(
    "Boton.TButton",
    font=("Arial", 11, "bold"),
    padding=10
)


# ============================================================
# ENCABEZADO
# ============================================================

encabezado = tk.Frame(
    ventana,
    bg="#163A5F",
    height=90
)

encabezado.pack(
    fill="x"
)

tk.Label(
    encabezado,
    text="SIMULADOR DE GESTIÓN DE PROCESOS",
    bg="#163A5F",
    fg="white",
    font=("Arial", 20, "bold")
).pack(pady=(18, 2))

tk.Label(
    encabezado,
    text="Gestión de memoria RAM",
    bg="#163A5F",
    fg="#D7E8F7",
    font=("Arial", 11)
).pack()


# ============================================================
# INFORMACIÓN DE RAM
# ============================================================

ram_frame = ttk.LabelFrame(
    ventana,
    text=" Estado de la memoria RAM ",
    padding=15
)

ram_frame.pack(
    fill="x",
    padx=25,
    pady=20
)

# Total
tk.Label(
    ram_frame,
    text="RAM TOTAL",
    font=("Arial", 9, "bold")
).grid(row=0, column=0, padx=25)

ram_total = ttk.Label(
    ram_frame,
    text="1024 MB",
    style="Info.TLabel"
)

ram_total.grid(row=1, column=0, padx=25)


# Usada
tk.Label(
    ram_frame,
    text="RAM USADA",
    font=("Arial", 9, "bold")
).grid(row=0, column=1, padx=25)

ram_usada = ttk.Label(
    ram_frame,
    text="0 MB",
    style="Info.TLabel"
)

ram_usada.grid(row=1, column=1, padx=25)


# Disponible
tk.Label(
    ram_frame,
    text="RAM DISPONIBLE",
    font=("Arial", 9, "bold")
).grid(row=0, column=2, padx=25)

ram_libre = ttk.Label(
    ram_frame,
    text="1024 MB",
    style="Info.TLabel"
)

ram_libre.grid(row=1, column=2, padx=25)


# Barra
barra_ram = ttk.Progressbar(
    ram_frame,
    maximum=100,
    length=230
)

barra_ram.grid(
    row=1,
    column=3,
    padx=20
)

porcentaje_label = ttk.Label(
    ram_frame,
    text="0.0%"
)

porcentaje_label.grid(
    row=1,
    column=4,
    padx=5
)


# ============================================================
# PROCESOS
# ============================================================

procesos_frame = tk.Frame(
    ventana
)

procesos_frame.pack(
    fill="both",
    expand=True,
    padx=25
)


# ------------------------------------------------------------
# EJECUCIÓN
# ------------------------------------------------------------

ejecucion_frame = ttk.LabelFrame(
    procesos_frame,
    text=" ▶ Procesos en ejecución ",
    padding=10
)

ejecucion_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)

lista_ejecucion = tk.Listbox(
    ejecucion_frame,
    font=("Arial", 10),
    height=10,
    borderwidth=0
)

lista_ejecucion.pack(
    fill="both",
    expand=True
)


# ------------------------------------------------------------
# COLA
# ------------------------------------------------------------

cola_frame = ttk.LabelFrame(
    procesos_frame,
    text=" ⏳ Cola de espera ",
    padding=10
)

cola_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)

lista_cola = tk.Listbox(
    cola_frame,
    font=("Arial", 10),
    height=10,
    borderwidth=0
)

lista_cola.pack(
    fill="both",
    expand=True
)


# ============================================================
# BOTONES
# ============================================================

botones = tk.Frame(
    ventana
)

botones.pack(
    pady=20
)


ttk.Button(
    botones,
    text="+  CREAR PROCESO",
    style="Boton.TButton",
    command=crear_proceso
).pack(
    side="left",
    padx=10
)


ttk.Button(
    botones,
    text="SALIR",
    style="Boton.TButton",
    command=salir
).pack(
    side="left",
    padx=10
)


# ============================================================
# INICIAR ACTUALIZACIÓN
# ============================================================

actualizar()

ventana.mainloop()