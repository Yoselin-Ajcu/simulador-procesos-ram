# Simulador de Gestión de Procesos y Memoria RAM

Este proyecto es una simulación interactiva desarrollada en Python para el curso de Sistemas Operativos I. Modela la asignación de memoria RAM, la gestión de la cola de espera de procesos y la liberación dinámica de recursos mediante hilos de ejecución en tiempo real (*multithreading*).

---

## Entorno de Ejecución

El proyecto está diseñado y probado para ejecutarse en un entorno **Linux (Ubuntu / WSL)** bajo Windows.

### Verificación del Entorno Linux
Para verificar que el programa corre sobre el kernel de Linux, puedes ejecutar en la terminal:

```bash
uname -a
Salida esperada:

Plaintext
Linux HostName 5.15.x.x-microsoft-standard-WSL2 #1 SMP ... x86_64 x86_64 x86_64 GNU/Linux
```

#### Requisitos Previos
Sistema Operativo: Linux (Ubuntu / WSL)

Lenguaje: Python 3.x (python3)

Editor: Visual Studio Code


##### Características e Implementación
Memoria RAM Total: Configurada a 1024 MB.

Concurrencia (Multithreading): Se utiliza threading.Thread para un hilo en segundo plano que simula el tiempo en tiempo real (1 tick = 1 segundo).

Mecanismos de Control (Locks): Uso de threading.Lock() para garantizar exclusión mutua en las secciones críticas donde se modifica la RAM y las listas de procesos.

Cola de Espera (Scheduling): Uso de una estructura collections.deque (FIFO) para encolar los procesos que sobrepasan la RAM disponible.

Liberación Automática: Al concluir la duración del proceso, la RAM ocupada se libera automáticamente y los procesos en la cola intentan ingresar a ejecución.


###### Instrucciones de Ejecución
Clonar o ingresar a la carpeta del proyecto:

Bash
cd /mnt/c/Users/ynose/simulador-procesos-ram
Ejecutar el simulador:

Bash
python3 main.py
Uso del menú interactivo:

Opción 1: Crear un proceso especificando nombre, RAM requerida (≤1024 MB) y duración en segundos.

Opción 2: Ver la tabla de estado actual de la memoria, procesos en ejecución y en cola.

Opción 3: Salir.