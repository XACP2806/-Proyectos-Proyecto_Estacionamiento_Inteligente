"""Grupo 03 - tipo complejo SIN sincronización."""

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
        # Esta versión NO usa Lock ni Semaphore.

    def ingresar(self, vehiculo_id):
        #  INICIO DE LA SECCIÓN CRÍTICA SIN PROTEGER 
        for puesto_id, datos in self.puestos.items():
            if not datos["ocupado"]:
                print(f"[{vehiculo_id}] Ve libre el puesto #{puesto_id}.")
                time.sleep(0.20)  # Otro hilo puede ver este mismo puesto libre.
                datos["ocupado"] = True
                datos["vehiculo"] = vehiculo_id
                print(f"[{vehiculo_id}] Puesto #{puesto_id} asignado.")
                return puesto_id
        #  FIN DE LA SECCIÓN CRÍTICA 
        print(f"[{vehiculo_id}] Estacionamiento lleno.")
        return None

    def salir(self, puesto_id, vehiculo_id):
        #  SECCIÓN CRÍTICA SIN PROTEGER: VALIDAR y LIBERAR PUESTO 
        datos = self.puestos[puesto_id]
        if datos["vehiculo"] == vehiculo_id:
            datos["ocupado"] = False
            datos["vehiculo"] = None
            print(f"[{vehiculo_id}] Liberó el puesto #{puesto_id}.")
            return True
        # Otro vehículo pudo sobrescribir la asignación.
        print(f"[{vehiculo_id}] ERROR al salir: el puesto #{puesto_id} "
              f"figura a nombre de {datos['vehiculo']}.")
        return False
        #  FIN DE LA SECCIÓN CRÍTICA 


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
        if len(asignaciones) != len(set(asignaciones)):
            print("ERROR DE CONCURRENCIA: dos vehículos recibieron el mismo puesto.")
        else:
            print("No se observó doble asignación en esta ejecución.")


if __name__ == "__main__":
    Simulador(CAPACIDAD, NUMERO_VEHICULOS).iniciar_simulacion()
