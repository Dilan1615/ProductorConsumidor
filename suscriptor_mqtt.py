import json
import sqlite3

import paho.mqtt.client as mqtt


BROKER = "localhost"
PUERTO = 1883
DB_NAME = "telemetria.db"


def inicializar_base_datos():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            lat REAL,
            lng REAL,
            speed REAL,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            temperature REAL,
            unit TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            fuel_level REAL,
            unit TEXT,
            timestamp TEXT
        )
    """)

    conexion.commit()
    conexion.close()

    print("Base de datos inicializada.")


def on_connect(cliente, userdata, flags, rc):
    print(f"Conectado a Mosquitto. Codigo: {rc}")

    cliente.subscribe("flota/+/gps")
    cliente.subscribe("flota/+/temperatura")
    cliente.subscribe("flota/+/combustible")

    print("Suscrito a topics de flota.")


def on_message(cliente, userdata, mensaje):
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode())

    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    if "/gps" in topic:
        cursor.execute("""
            INSERT INTO gps_data(vehicle_id, lat, lng, speed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            payload["vehicle_id"],
            payload["lat"],
            payload["lng"],
            payload["speed"],
            payload["timestamp"]
        ))

        print(f"GPS guardado: {payload}")

    elif "/temperatura" in topic:
        if payload["temperature"] > 4:
            print(f"ALERTA: temperatura alta en {payload['vehicle_id']}")

        cursor.execute("""
            INSERT INTO temp_data(vehicle_id, temperature, unit, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            payload["vehicle_id"],
            payload["temperature"],
            payload["unit"],
            payload["timestamp"]
        ))

        print(f"Temperatura guardada: {payload}")

    elif "/combustible" in topic:
        if payload["fuel_level"] < 20:
            print(f"ALERTA: combustible bajo en {payload['vehicle_id']}")

        cursor.execute("""
            INSERT INTO fuel_data(vehicle_id, fuel_level, unit, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            payload["vehicle_id"],
            payload["fuel_level"],
            payload["unit"],
            payload["timestamp"]
        ))

        print(f"Combustible guardado: {payload}")

    conexion.commit()
    conexion.close()


def principal():
    inicializar_base_datos()

    cliente = mqtt.Client()
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    cliente.connect(BROKER, PUERTO, 60)

    print("Suscriptor MQTT activo...")
    cliente.loop_forever()


if __name__ == "__main__":
    principal()