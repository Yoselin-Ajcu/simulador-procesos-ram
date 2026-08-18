import time
import threading
from collections import deque

class Proceso:
    _pid_counter = 1

    def __init__(self, nombre="", ram=128, duracion=5):
        self.pid = Proceso._pid_counter
        Proceso._pid_counter += 1
        self.nombre = nombre if nombre.strip() else f"Proceso_{self.pid}"
        self.ram = ram  # En MB
        self.duracion = duracion  # En segundos

class SimuladorRAM:
    def __init__(self, ram_total_mb=1024):
        self.ram_total = ram_total_mb
        self.ram_disponible = ram_total_mb
        self.ejecucion = []
        self.cola_espera = deque()
        self.lock = threading.Lock()
        self.running = True

    def agregar_proceso(self, nombre, ram, duracion):
        p = Proceso(nombre, ram, duracion)
        with self.lock:
            if p.ram <= self.ram_disponible:
                self.ram_disponible -= p.ram
                self.ejecucion.append(p)
                print(f"\n[+] {p.nombre} (PID {p.pid}) -> EN EJECUCIÓN | Requería: {p.ram} MB | RAM Libre: {self.ram_disponible} MB")
            else:
                self.cola_espera.append(p)
                print(f"\n[!] {p.nombre} (PID {p.pid}) -> EN COLA DE ESPERA | Requería: {p.ram} MB | RAM Libre insufic.: {self.ram_disponible} MB")

    def mostrar_estado(self):
        with self.lock:
            ram_usada = self.ram_total - self.ram_disponible
            porcentaje = (ram_usada / self.ram_total) * 100
            
            print("\n=================== ESTADO DE LA MEMORIA ===================")
            print(f"RAM Total: {self.ram_total} MB | Usada: {ram_usada} MB | Libre: {self.ram_disponible} MB ({100 - porcentaje:.1f}%)")
            
            print("\n--- Procesos en Ejecución ---")
            if not self.ejecucion:
                print("  (Ninguno)")
            for p in self.ejecucion:
                print(f"  • PID {p.pid} | {p.nombre} | RAM: {p.ram} MB | Tiempo restante: {p.duracion}s")
                
            print("\n--- Cola de Espera ---")
            if not self.cola_espera:
                print("  (Vacía)")
            for p in self.cola_espera:
                print(f"  • PID {p.pid} | {p.nombre} | RAM requerida: {p.ram} MB | Duración: {p.duracion}s")
            print("============================================================\n")

    def tick_simulacion(self):
        """Disminuye el tiempo de los procesos cada segundo."""
        while self.running:
            time.sleep(1)
            with self.lock:
                # 1. Reducir tiempo de ejecución
                finalizados = []
                for p in self.ejecucion:
                    p.duracion -= 1
                    if p.duracion <= 0:
                        finalizados.append(p)

                # 2. Liberar memoria de procesos finalizados
                for p in finalizados:
                    self.ejecucion.remove(p)
                    self.ram_disponible += p.ram
                    print(f"\n[-] {p.nombre} (PID {p.pid}) FINALIZÓ. Se liberaron {p.ram} MB. RAM Libre: {self.ram_disponible} MB")

                # 3. Intentar pasar procesos de la cola a ejecución
                nuevos_en_cola = deque()
                while len(self.cola_espera) > 0:
                    p_espera = self.cola_espera.popleft()
                    if p_espera.ram <= self.ram_disponible:
                        self.ram_disponible -= p_espera.ram
                        self.ejecucion.append(p_espera)
                        print(f"\n[→] {p_espera.nombre} (PID {p_espera.pid}) Salió de la cola -> EN EJECUCIÓN.")
                    else:
                        nuevos_en_cola.append(p_espera)
                self.cola_espera = nuevos_en_cola

def menu():
    sim = SimuladorRAM(1024)
    hilo = threading.Thread(target=sim.tick_simulacion, daemon=True)
    hilo.start()

    print("=== SIMULADOR DE GESTIÓN DE PROCESOS EN MEMORIA (1024 MB) ===")

    while True:
        print("\nOpciones:")
        print("1. Crear nuevo proceso")
        print("2. Ver estado de memoria y procesos")
        print("3. Salir")
        
        opcion = input("Seleccione una opción (1-3): ").strip()

        if opcion == "1":
            nombre = input("Nombre del proceso (vacío para automático): ").strip()
            try:
                ram = int(input("Memoria requerida en MB (ej. 256): "))
                
                # Validación de memoria máxima
                if ram > sim.ram_total:
                    print(f"\n Error: El proceso requiere ({ram} MB), que supera la RAM total del sistema ({sim.ram_total} MB).")
                    continue

                duracion = int(input("Duración en segundos (ej. 10): "))
                sim.agregar_proceso(nombre, ram, duracion)
            except ValueError:
                print(" Error: Ingrese valores numéricos válidos para la RAM y la duración.")
        elif opcion == "2":
            sim.mostrar_estado()
        elif opcion == "3":
            sim.running = False
            print("Saliendo del simulador...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    menu()