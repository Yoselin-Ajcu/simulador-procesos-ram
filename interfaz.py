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
# COLORES
# ============================================================

FONDO = "#EAF4F8"
AZUL_OSCURO = "#163A5F"
AZUL = "#2878A8"
TURQUESA = "#3A9DAD"
BLANCO = "#FFFFFF"
TEXTO = "#263746"
VERDE = "#3C8D68"
ROJO = "#B85450"


# ============================================================
# FUNCIONES
# ============================================================

def centrar_ventana(ventana, ancho, alto, desplazamiento_x=0):
    """Centra una ventana en la pantalla."""

    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho - ancho) // 2 + desplazamiento_x
    y = (pantalla_alto - alto) // 2

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def actualizar():
    """Actualiza la información mostrada en la interfaz."""

    with simulador.lock:

        usada = RAM_TOTAL - simulador.ram_disponible
        porcentaje = usada / RAM_TOTAL * 100

        ram_total.config(text=f"{RAM_TOTAL} MB")
        ram_usada.config(text=f"{usada} MB")
        ram_libre.config(text=f"{simulador.ram_disponible} MB")

        barra_ram["value"] = porcentaje
        porcentaje_label.config(
            text=f"{porcentaje:.1f}% utilizada"
        )

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
    """Crea la ventana para introducir los datos del proceso."""

    nueva = tk.Toplevel(ventana)

    nueva.es_ventana_proceso = True

    nueva.title("Crear proceso")
    nueva.resizable(False, False)
    nueva.configure(bg=FONDO)

    centrar_ventana(
        nueva,
        350,
        330,
        500
    )

    # --------------------------------------------------------
    # ENCABEZADO
    # --------------------------------------------------------

    encabezado = tk.Frame(
        nueva,
        bg=AZUL_OSCURO,
        height=70
    )

    encabezado.pack(
        fill="x"
    )

    tk.Label(
        encabezado,
        text="CREAR PROCESO",
        bg=AZUL_OSCURO,
        fg=BLANCO,
        font=("Arial", 17, "bold")
    ).pack(pady=20)

    # --------------------------------------------------------
    # CAMPOS
    # --------------------------------------------------------

    marco = tk.Frame(
        nueva,
        bg=FONDO
    )

    marco.pack(
        fill="both",
        padx=25,
        pady=15
    )

    tk.Label(
        marco,
        text="Nombre del proceso",
        bg=FONDO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    nombre = ttk.Entry(marco)
    nombre.pack(
        fill="x",
        pady=(3, 12)
    )

    tk.Label(
        marco,
        text="Memoria requerida (MB)",
        bg=FONDO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    memoria = ttk.Entry(marco)
    memoria.pack(
        fill="x",
        pady=(3, 12)
    )

    tk.Label(
        marco,
        text="Duración (segundos)",
        bg=FONDO,
        fg=TEXTO,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    duracion = ttk.Entry(marco)
    duracion.pack(
        fill="x",
        pady=(3, 15)
    )

    # --------------------------------------------------------
    # GUARDAR
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
    ).pack(
        pady=5
    )


def salir():
    """Cierra el simulador."""

    confirmar = messagebox.askyesno(
        "Salir",
        "¿Desea salir del simulador?"
    )

    if confirmar:

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
ventana.configure(bg=FONDO)

centrar_ventana(
    ventana,
    900,
    620
)


# ============================================================
# ESTILOS
# ============================================================

estilo = ttk.Style()

estilo.configure(
    "TButton",
    font=("Arial", 10, "bold"),
    padding=9
)

estilo.configure(
    "Info.TLabel",
    font=("Arial", 15, "bold")
)


# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================

encabezado = tk.Frame(
    ventana,
    bg=AZUL_OSCURO,
    height=90
)

encabezado.pack(
    fill="x"
)

tk.Label(
    encabezado,
    text="SIMULADOR DE GESTIÓN DE PROCESOS",
    bg=AZUL_OSCURO,
    fg=BLANCO,
    font=("Arial", 20, "bold")
).pack(pady=(18, 2))

tk.Label(
    encabezado,
    text="Gestión de memoria RAM",
    bg=AZUL_OSCURO,
    fg="#D8EAF2",
    font=("Arial", 11)
).pack()


# ============================================================
# INFORMACIÓN DE RAM
# ============================================================

ram_frame = tk.Frame(
    ventana,
    bg=BLANCO,
    bd=1,
    relief="solid"
)

ram_frame.pack(
    fill="x",
    padx=25,
    pady=20
)

tk.Label(
    ram_frame,
    text="RAM TOTAL",
    bg=BLANCO,
    fg=TEXTO,
    font=("Arial", 9, "bold")
).grid(
    row=0,
    column=0,
    padx=25,
    pady=(12, 0)
)

ram_total = tk.Label(
    ram_frame,
    text="1024 MB",
    bg=BLANCO,
    fg=AZUL_OSCURO,
    font=("Arial", 15, "bold")
)

ram_total.grid(
    row=1,
    column=0,
    padx=25,
    pady=(2, 12)
)


tk.Label(
    ram_frame,
    text="RAM USADA",
    bg=BLANCO,
    fg=TEXTO,
    font=("Arial", 9, "bold")
).grid(
    row=0,
    column=1,
    padx=25,
    pady=(12, 0)
)

ram_usada = tk.Label(
    ram_frame,
    text="0 MB",
    bg=BLANCO,
    fg=AZUL,
    font=("Arial", 15, "bold")
)

ram_usada.grid(
    row=1,
    column=1,
    padx=25,
    pady=(2, 12)
)


tk.Label(
    ram_frame,
    text="RAM DISPONIBLE",
    bg=BLANCO,
    fg=TEXTO,
    font=("Arial", 9, "bold")
).grid(
    row=0,
    column=2,
    padx=25,
    pady=(12, 0)
)

ram_libre = tk.Label(
    ram_frame,
    text="1024 MB",
    bg=BLANCO,
    fg=VERDE,
    font=("Arial", 15, "bold")
)

ram_libre.grid(
    row=1,
    column=2,
    padx=25,
    pady=(2, 12)
)


# Barra de RAM

barra_ram = ttk.Progressbar(
    ram_frame,
    maximum=100,
    length=210
)

barra_ram.grid(
    row=1,
    column=3,
    padx=15
)

porcentaje_label = tk.Label(
    ram_frame,
    text="0.0% utilizada",
    bg=BLANCO,
    fg=TEXTO,
    font=("Arial", 9)
)

porcentaje_label.grid(
    row=1,
    column=4,
    padx=10
)


# ============================================================
# PROCESOS
# ============================================================

procesos_frame = tk.Frame(
    ventana,
    bg=FONDO
)

procesos_frame.pack(
    fill="both",
    expand=True,
    padx=25
)


# ------------------------------------------------------------
# PROCESOS EN EJECUCIÓN
# ------------------------------------------------------------

ejecucion_frame = tk.Frame(
    procesos_frame,
    bg=BLANCO,
    bd=1,
    relief="solid"
)

ejecucion_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 10)
)

tk.Label(
    ejecucion_frame,
    text="▶  PROCESOS EN EJECUCIÓN",
    bg=BLANCO,
    fg=AZUL_OSCURO,
    font=("Arial", 11, "bold")
).pack(
    anchor="w",
    padx=12,
    pady=(10, 5)
)

lista_ejecucion = tk.Listbox(
    ejecucion_frame,
    font=("Arial", 10),
    height=10,
    borderwidth=0,
    highlightthickness=0,
    bg=BLANCO,
    fg=TEXTO
)

lista_ejecucion.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)


# ------------------------------------------------------------
# COLA DE ESPERA
# ------------------------------------------------------------

cola_frame = tk.Frame(
    procesos_frame,
    bg=BLANCO,
    bd=1,
    relief="solid"
)

cola_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(10, 0)
)

tk.Label(
    cola_frame,
    text="⏳  COLA DE ESPERA",
    bg=BLANCO,
    fg=TURQUESA,
    font=("Arial", 11, "bold")
).pack(
    anchor="w",
    padx=12,
    pady=(10, 5)
)

lista_cola = tk.Listbox(
    cola_frame,
    font=("Arial", 10),
    height=10,
    borderwidth=0,
    highlightthickness=0,
    bg=BLANCO,
    fg=TEXTO
)

lista_cola.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)


# ============================================================
# BOTONES
# ============================================================

botones = tk.Frame(
    ventana,
    bg=FONDO
)

botones.pack(
    pady=18
)


ttk.Button(
    botones,
    text="+  CREAR PROCESO",
    command=crear_proceso
).pack(
    side="left",
    padx=8
)


ttk.Button(
    botones,
    text="SALIR",
    command=salir
).pack(
    side="left",
    padx=8
)


# ============================================================
# INICIAR ACTUALIZACIÓN
# ============================================================

actualizar()

ventana.mainloop()