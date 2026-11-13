"""Grupo 03 - tipo básico CON sincronización."""
import threading
import time

# Capacidad de PRUEBA: no es la capacidad definitiva del proyecto.
CAPACIDAD = 1
NUMERO_VEHICULOS = 2


class EstacionamientoBasico:
    def __init__(self, capacidad):
        self.capacidad_maxima = capacidad
        self.espacios_disponibles = capacidad  # Recurso compartido: int
        self.lock = threading.Lock()  # Mutex: solo un hilo modifica el contador.
        self.semaforo = threading.BoundedSemaphore(capacidad)  # Permisos de cupos.

    def ingresar(self, vehiculo_id):
        # El semáforo controla los cupos; NO reemplaza el mutex.
        if not self.semaforo.acquire(blocking=False):
            print(f"[{vehiculo_id}] Estacionamiento lleno.")
            return False

        #  INICIO DE LA SECCIÓN CRÍTICA PROTEGIDA 
        with self.lock:  
            if self.espacios_disponibles > 0:
                self.espacios_disponibles -= 1
                print(f"[{vehiculo_id}] Ingreso exitoso. "
                      f"Libres: {self.espacios_disponibles}")
                return True
        #  FIN DE LA SECCIÓN CRÍTICA 
        self.semaforo.release()
        return False

    def salir(self, vehiculo_id):
        #  SECCIÓN CRÍTICA PROTEGIDA: VALIDAR y ACTUALIZAR 
        with self.lock:
            if self.espacios_disponibles >= self.capacidad_maxima:
                return False  # Evita incrementar por encima de la capacidad.
            self.espacios_disponibles += 1
            print(f"[{vehiculo_id}] Salida registrada. "
                  f"Libres: {self.espacios_disponibles}")
        #  FIN DE LA SECCIÓN CRÍTICA; MUTEX LIBERADO 
        self.semaforo.release() 
        return True


class Vehiculo(threading.Thread):
    def __init__(self, vehiculo_id, estacionamiento_compartido):
        super().__init__()
        self.vehiculo_id = vehiculo_id
        self.estacionamiento = estacionamiento_compartido  # MISMA instancia para todos.
        self.ingreso_exitoso = False

    def run(self):
        self.ingreso_exitoso = self.estacionamiento.ingresar(self.vehiculo_id)
        if self.ingreso_exitoso:
            time.sleep(0.35)
            self.estacionamiento.salir(self.vehiculo_id)


class Simulador:
    def __init__(self, capacidad, numero_vehiculos):
        self.estacionamiento = EstacionamientoBasico(capacidad)
        self.vehiculos = [Vehiculo(f"V{i}", self.estacionamiento)
                          for i in range(1, numero_vehiculos + 1)]

    def iniciar_simulacion(self):
        for vehiculo in self.vehiculos:
            vehiculo.start()
        for vehiculo in self.vehiculos:
            vehiculo.join()
        self.reportar_resultados()

    def reportar_resultados(self):
        aceptados = sum(v.ingreso_exitoso for v in self.vehiculos)
        print(f"\nRESUMEN: capacidad={self.estacionamiento.capacidad_maxima}; "
              f"ingresos aceptados={aceptados}.")
        print("CORRECTO: la capacidad máxima no se excedió."
              if aceptados <= self.estacionamiento.capacidad_maxima
              else "ERROR: se excedió la capacidad.")


if __name__ == "__main__":
    Simulador(CAPACIDAD, NUMERO_VEHICULOS).iniciar_simulacion()
