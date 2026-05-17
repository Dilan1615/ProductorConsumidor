import json
import time
import random
from datetime import datetime

import paho.mqtt.client as mqtt


BROKER = "localhost"
PUERTO = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]


def on_connect(cliente, userdata, flags, rc):
    print(f"Conectado a Mosquitto. Codigo: {rc}")


def simular_gps():
    return {
        "lat": round(-2.1709 + random.uniform(-0.01, 0.01), 6),
        "lng": round(-79.9224 + random.uniform(-0.01, 0.01), 6),
        "speed": round(random.uniform(20, 80), 1)
    }


def simular_temperatura():
    return {
        "temperature": round(random.uniform(-5, 8), 1),
        "unit": "celsius"
    }


def simular_combustible():
    return {
        "fuel_level": round(random.uniform(10, 100), 1),
        "unit": "percent"
    }


def publicar(cliente, vehiculo, tipo, datos):
    timestamp = datetime.now().isoformat()

    mensaje = {
        "vehicle_id": vehiculo,
        "timestamp": timestamp,
        **datos
    }

    topic = f"flota/{vehiculo}/{tipo}"

    cliente.publish(topic, json.dumps(mensaje))
    print(f"Publicado en {topic}: {mensaje}")


def principal():
    cliente = mqtt.Client()
    cliente.on_connect = on_connect

    cliente.connect(BROKER, PUERTO, 60)
    cliente.loop_start()

    print("Simulador iniciado...")

    try:
        while True:
            for vehiculo in VEHICULOS:
                publicar(cliente, vehiculo, "gps", simular_gps())
                publicar(cliente, vehiculo, "temperatura", simular_temperatura())
                publicar(cliente, vehiculo, "combustible", simular_combustible())

            time.sleep(5)

    except KeyboardInterrupt:
        print("Simulador detenido.")
        cliente.loop_stop()
        cliente.disconnect()


if __name__ == "__main__":
    principal()