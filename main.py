import time
import threading
from collections import deque

# ======== Definición de la clase Proceso ==================
class Proceso:
    _pid_counter = 1 # Contador de PID para asignar identificadores únicos a cada proceso

    def __init__(self, nombre="", ram=128, duracion=5): 
        self.pid = Proceso._pid_counter # Asignar PID único y luego incrementar el contador
        Proceso._pid_counter += 1 # Incrementar el contador de PID para el próximo proceso
        self.nombre = nombre if nombre.strip() else f"Proceso_{self.pid}" # Asignar nombre automático si no se proporciona uno
        self.ram = ram  # En MB 
        self.duracion = duracion  # En segundos

# ======== Definición de la clase SimuladorRAM ==================
# Esta clase simula la gestión de procesos en memoria RAM 
class SimuladorRAM:
    def __init__(self, ram_total_mb=1024): 
        self.ram_total = ram_total_mb # Capacidad total de RAM
        self.ram_disponible = ram_total_mb #Memoria actualmete disponible
        self.ejecucion = [] # Lista de procesos actualmente en ejecución
        self.cola_espera = deque() # Cola de procesos esperando a ser ejecutados FIFO
        self.lock = threading.Lock() # Lock para sincronizar el acceso a los recursos compartidos entre hilos
        self.running = True # Control para detner el hilo de simulación

    # Agrega un nuevo proceso al simulador
    def agregar_proceso(self, nombre, ram, duracion): 
        p = Proceso(nombre, ram, duracion) # Crear un nuevo proceso con los parámetros proporcionados
        with self.lock: # Bloquea el acceso a los recursos compartidos
              
            if p.ram <= self.ram_disponible: # Verifica si hay suficiente RAM disponible para ejecutar el proceso  
                self.ram_disponible -= p.ram
                self.ejecucion.append(p)
                print(f"\n[+] {p.nombre} (PID {p.pid}) -> EN EJECUCIÓN | Requería: {p.ram} MB | RAM Libre: {self.ram_disponible} MB")
            else:
                # Si no hay suficiente RAM, el proceso se coloca en la cola de espera
                self.cola_espera.append(p)
                print(f"\n[!] {p.nombre} (PID {p.pid}) -> EN COLA DE ESPERA | Requería: {p.ram} MB | RAM Libre insufic.: {self.ram_disponible} MB")

    # Muestra el estado actual de la memoria y los procesos
    def mostrar_estado(self):
        with self.lock:
            # Calcular la RAM usada y el porcentaje de uso
            ram_usada = self.ram_total - self.ram_disponible
            porcentaje = (ram_usada / self.ram_total) * 100

            #Encabezado de estado de memoria
            print("\n=================== ESTADO DE LA MEMORIA ===================")
            print(f"RAM Total: {self.ram_total} MB | Usada: {ram_usada} MB | Libre: {self.ram_disponible} MB ({100 - porcentaje:.1f}%)")

            # Mostrar los procesos en ejecución
            print("\n--- Procesos en Ejecución ---")
            if not self.ejecucion:
                print("  (Ninguno)")
            for p in self.ejecucion:
                print(f"  • PID {p.pid} | {p.nombre} | RAM: {p.ram} MB | Tiempo restante: {p.duracion}s")

            # Mostrar los procesos en cola de espera    
            print("\n--- Cola de Espera ---")
            if not self.cola_espera:
                print("  (Vacía)")
            for p in self.cola_espera:
                print(f"  • PID {p.pid} | {p.nombre} | RAM requerida: {p.ram} MB | Duración: {p.duracion}s")
            print("============================================================\n")

    # Simula el paso del tiempo y la ejecución de los procesos
    def tick_simulacion(self):
        """Disminuye el tiempo de los procesos cada segundo."""
        while self.running:
            time.sleep(1) # Espera 1 segundo antes de actualizar el estado de los procesos
            with self.lock:
                # 1 Reducir tiempo de ejecución
                finalizados = [] 
                for p in self.ejecucion:
                    p.duracion -= 1 # Reducir en 1 segundo
                    if p.duracion <= 0:
                        finalizados.append(p) # Marcar para la finalización si el tiempo llega a 0

                # 2 Liberar memoria de procesos finalizados
                for p in finalizados:
                    self.ejecucion.remove(p) # Eliminar de la lista de ejecución
                    self.ram_disponible += p.ram # Liberar la memoria ocupada por el proceso
                    print(f"\n[-] {p.nombre} (PID {p.pid}) FINALIZÓ. Se liberaron {p.ram} MB. RAM Libre: {self.ram_disponible} MB")

                # 3 Intentar pasar procesos de la cola a ejecución
                nuevos_en_cola = deque() # Cola para procesos que aún no pueden ejecutarse por falta de RAM
                while len(self.cola_espera) > 0:
                    p_espera = self.cola_espera.popleft() # Sacar el primer proceso de la cola de espera
                    if p_espera.ram <= self.ram_disponible: # Verificar si hay suficiente RAM disponible para ejecutar el proceso
                        self.ram_disponible -= p_espera.ram 
                        self.ejecucion.append(p_espera) # Agregar a la lista de ejecución
                        print(f"\n[→] {p_espera.nombre} (PID {p_espera.pid}) Salió de la cola -> EN EJECUCIÓN.")
                    else:
                        # Si no hay suficiente RAM el proceso permanece en la cola de espera
                        nuevos_en_cola.append(p_espera) 
                self.cola_espera = nuevos_en_cola # Actualizar la cola de espera

#============================================================
# Funcion menu en modo consola 
#============================================================
def menu():
    sim = SimuladorRAM(1024) # Crear una instancia del simulador con 1024 MB de RAM
    hilo = threading.Thread(target=sim.tick_simulacion, daemon=True) # Hilo de simulacion en segundo plano 
    hilo.start()

    print("=== SIMULADOR DE GESTIÓN DE PROCESOS EN MEMORIA (1024 MB) ===")

    # Blucle principal del menú 
    while True:
        # Mostrar opciones del menú
        print("\nOpciones:")
        print("1. Crear nuevo proceso")
        print("2. Ver estado de memoria y procesos")
        print("3. Salir")
        
        opcion = input("Seleccione una opción (1-3): ").strip()

        if opcion == "1":
            # Crear nuevo proceso 
            nombre = input("Nombre del proceso (vacío para automático): ").strip()
            try:
                ram = int(input("Memoria requerida en MB (ej. 256): "))
                
                # Validación de memoria máxima
                if ram > sim.ram_total:
                    print(f"\n Error: El proceso requiere ({ram} MB), que supera la RAM total del sistema ({sim.ram_total} MB).")
                    continue

                # Solicitar duración del proceso
                duracion = int(input("Duración en segundos (ej. 10): "))

                # Agregar el proceso al simulador
                sim.agregar_proceso(nombre, ram, duracion)

            # Manejo de errores de entrada
            except ValueError:
                print(" Error: Ingrese valores numéricos válidos para la RAM y la duración.")
        elif opcion == "2":
            # Mostrar estado de memoria y procesos
            sim.mostrar_estado()
        elif opcion == "3":
            # Salir del simulador
            sim.running = False # Detener el hilo de simulación
            print("Saliendo del simulador...")
            break # Fin del ciclo while
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    menu() # Inicio de la aplicación en modo consola