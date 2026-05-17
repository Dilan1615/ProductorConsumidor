
import json
import time
import random
import math
from datetime import datetime
import paho.mqtt.client as mqtt

# ─── Configuración MQTT ───────────────────────────────────────
BROKER = "localhost"
PUERTO = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]
INTERVALO_SEGUNDOS = 5


# ─── Callbacks ────────────────────────────────────────────────
def on_connect(cliente, datos_usuario, flags, codigo_respuesta):
    if codigo_respuesta == 0:
        print(f"[{datetime.now().isoformat()}] Conectado al broker MQTT (rc={codigo_respuesta})")
    else:
        print(f"[{datetime.now().isoformat()}]  Error de conexión (rc={codigo_respuesta})")


# ─── Simuladores de sensores ──────────────────────────────────
def simular_gps(id_vehiculo):
    """Simula coordenadas GPS alrededor de Guayaquil, Ecuador."""
    base_lat = -2.1709
    base_lng = -79.9224
    latitud   = base_lat + random.uniform(-0.01, 0.01)
    longitud  = base_lng + random.uniform(-0.01, 0.01)
    velocidad = random.uniform(20, 80)
    return {
        "lat":   round(latitud,   6),
        "lng":   round(longitud,  6),
        "speed": round(velocidad, 1),
    }


def simular_temperatura(id_vehiculo):
    """Simula temperatura del compartimento de carga (cadena de frío)."""
    temperatura = random.uniform(-5, 8)
    return {
        "temperature": round(temperatura, 1),
        "unit": "celsius",
    }


def simular_combustible(id_vehiculo):
    """Simula nivel de combustible del vehículo."""
    combustible = random.uniform(10, 100)
    return {
        "fuel_level": round(combustible, 1),
        "unit": "percent",
    }


# ─── Función principal ────────────────────────────────────────
def principal():
    cliente = mqtt.Client(client_id="sensor_simulador")
    cliente.on_connect = on_connect
    cliente.connect(BROKER, PUERTO, keepalive=60)
    cliente.loop_start()

    print("Iniciando simulador de sensores IoT...")
    print(f"   Vehículos: {VEHICULOS}")
    print(f"   Intervalo: {INTERVALO_SEGUNDOS}s\n")

    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.now().isoformat()

                # ── GPS ──────────────────────────────────────
                gps = simular_gps(vehiculo)
                datos_gps = {"vehicle_id": vehiculo, "timestamp": timestamp, **gps}
                cliente.publish(
                    f"flota/{vehiculo}/gps",
                    json.dumps(datos_gps),
                    qos=1,
                )

                # ── Temperatura ───────────────────────────────
                temp = simular_temperatura(vehiculo)
                datos_temp = {"vehicle_id": vehiculo, "timestamp": timestamp, **temp}
                cliente.publish(
                    f"flota/{vehiculo}/temperatura",
                    json.dumps(datos_temp),
                    qos=1,
                )

                # ── Combustible ───────────────────────────────
                fuel = simular_combustible(vehiculo)
                datos_fuel = {"vehicle_id": vehiculo, "timestamp": timestamp, **fuel}
                cliente.publish(
                    f"flota/{vehiculo}/combustible",
                    json.dumps(datos_fuel),
                    qos=1,
                )

                print(
                    f"[{timestamp}] {vehiculo} → "
                    f"GPS({datos_gps['lat']}, {datos_gps['lng']}) | "
                    f"Temp: {datos_temp['temperature']}°C | "
                    f"Fuel: {datos_fuel['fuel_level']}%"
                )

            time.sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\n Deteniendo simulador...")
        cliente.loop_stop()
        cliente.disconnect()


if __name__ == "__main__":
    principal()