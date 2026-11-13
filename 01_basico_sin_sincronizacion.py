"""Grupo 03 - tipo básico SIN sincronización."""
import threading
import time

# Capacidad de PRUEBA: no es la capacidad definitiva del proyecto.
CAPACIDAD = 1
NUMERO_VEHICULOS = 2


class EstacionamientoBasico:
    def __init__(self, capacidad):
        self.capacidad_maxima = capacidad
        self.espacios_disponibles = capacidad  # Recurso compartido: int
        # Esta versión NO usa Lock ni Semaphore.

    def ingresar(self, vehiculo_id):
        # INICIO DE LA SECCIÓN CRÍTICA SIN PROTEGER 
        # 1. CONSULTAR y VALIDAR disponibilidad.
        if self.espacios_disponibles > 0:
            print(f"[{vehiculo_id}] Ve un espacio disponible.")
            time.sleep(0.20)  # Simula un retraso entre consultar y actualizar.
            # 2. ACTUALIZAR: otro hilo pudo ingresar durante la pausa.
            self.espacios_disponibles -= 1
            print(f"[{vehiculo_id}] Ingreso exitoso. Libres: {self.espacios_disponibles}")
            return True
        # FIN DE LA SECCIÓN CRÍTICA 
        print(f"[{vehiculo_id}] Estacionamiento lleno.")
        return False

    def salir(self, vehiculo_id):
        #  SECCIÓN CRÍTICA SIN PROTEGER: ACTUALIZAR DISPONIBILIDAD 
        self.espacios_disponibles += 1
        print(f"[{vehiculo_id}] Salida registrada. Libres: {self.espacios_disponibles}")
        #  FIN DE LA SECCIÓN CRÍTICA 


class Vehiculo(threading.Thread):
    def __init__(self, vehiculo_id, estacionamiento_compartido):
        super().__init__()
        self.vehiculo_id = vehiculo_id
        self.estacionamiento = estacionamiento_compartido  
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
        if aceptados > self.estacionamiento.capacidad_maxima:
            print("ERROR DE CONCURRENCIA: se admitieron más vehículos que espacios.")
        else:
            print("No se observó sobrecupo en esta ejecución.")


if __name__ == "__main__":
    Simulador(CAPACIDAD, NUMERO_VEHICULOS).iniciar_simulacion()
