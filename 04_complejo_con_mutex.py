"""Grupo 03 - tipo complejo CON sincronización."""
import threading
import time

# Capacidad de PRUEBA: no es la capacidad definitiva del proyecto.
CAPACIDAD = 1
NUMERO_VEHICULOS = 2


class EstacionamientoComplejo:
    def __init__(self, capacidad):
        self.capacidad_maxima = capacidad
        # Recurso compartido
        self.puestos = {i: {"ocupado": False, "vehiculo": None}
                        for i in range(1, capacidad + 1)}
        self.lock = threading.Lock()  # Mutex para el diccionario.
        self.semaforo = threading.BoundedSemaphore(capacidad)  # Cupos disponibles.

    def ingresar(self, vehiculo_id):
        # El semáforo controla cupos; con blocking=False se rechaza si está lleno.
        if not self.semaforo.acquire(blocking=False):
            print(f"[{vehiculo_id}] Estacionamiento lleno.")
            return None

        #  INICIO DE LA SECCIÓN CRÍTICA PROTEGIDA 
        with self.lock:  
            for puesto_id, datos in self.puestos.items():
                if not datos["ocupado"]:
                    datos["ocupado"] = True
                    datos["vehiculo"] = vehiculo_id
                    print(f"[{vehiculo_id}] Puesto #{puesto_id} asignado.")
                    return puesto_id
        #  FIN DE LA SECCIÓN CRÍTICA 
        self.semaforo.release()
        return None

    def salir(self, puesto_id, vehiculo_id):
        #  INICIO DE LA SECCIÓN CRÍTICA PROTEGIDA 
        with self.lock:
            if puesto_id not in self.puestos:
                return False
            datos = self.puestos[puesto_id]
            if datos["vehiculo"] != vehiculo_id or not datos["ocupado"]:
                return False
            datos["ocupado"] = False
            datos["vehiculo"] = None
            print(f"[{vehiculo_id}] Liberó el puesto #{puesto_id}.")
        #  FIN DE LA SECCIÓN CRÍTICA; MUTEX LIBERADO 
        self.semaforo.release()  
        return True


class Vehiculo(threading.Thread):
    def __init__(self, vehiculo_id, estacionamiento_compartido):
        super().__init__()
        self.vehiculo_id = vehiculo_id
        self.estacionamiento = estacionamiento_compartido  
        self.puesto_asignado = None

    def run(self):
        self.puesto_asignado = self.estacionamiento.ingresar(self.vehiculo_id)
        if self.puesto_asignado is not None:
            time.sleep(0.35)
            self.estacionamiento.salir(self.puesto_asignado, self.vehiculo_id)


class Simulador:
    def __init__(self, capacidad, numero_vehiculos):
        self.estacionamiento = EstacionamientoComplejo(capacidad)
        self.vehiculos = [Vehiculo(f"V{i}", self.estacionamiento)
                          for i in range(1, numero_vehiculos + 1)]

    def iniciar_simulacion(self):
        for vehiculo in self.vehiculos:
            vehiculo.start()
        for vehiculo in self.vehiculos:
            vehiculo.join()
        self.reportar_resultados()

    def reportar_resultados(self):
        asignaciones = [v.puesto_asignado for v in self.vehiculos
                        if v.puesto_asignado is not None]
        print(f"\nRESUMEN: asignaciones entregadas={asignaciones}.")
        if len(asignaciones) == len(set(asignaciones)):
            print("CORRECTO: ningún puesto fue asignado a dos vehículos.")
        else:
            print("ERROR: existe doble asignación.")


if __name__ == "__main__":
    Simulador(CAPACIDAD, NUMERO_VEHICULOS).iniciar_simulacion()
