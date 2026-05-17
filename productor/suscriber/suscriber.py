from datetime import datetime
import json
import sqlite3
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

DB_PATH = "../database/telemetria.db"


# Umbrales de alerta
UMBRAL_TEMPERATURA = 4.0   # °C  — cadena de frío
UMBRAL_COMBUSTIBLE = 20.0  # %   — nivel mínimo


# ─── Base de datos ────────────────────────────────────────────
def inicializar_base_datos():
    """Crea las tablas de telemetría si no existen."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gps_data (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT    NOT NULL,
            lat        REAL    NOT NULL,
            lng        REAL    NOT NULL,
            speed      REAL    NOT NULL,
            timestamp  TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS temp_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id  TEXT    NOT NULL,
            temperature REAL    NOT NULL,
            unit        TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fuel_data (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT    NOT NULL,
            fuel_level REAL    NOT NULL,
            unit       TEXT    NOT NULL,
            timestamp  TEXT    NOT NULL
        )
    """)

    con.commit()
    con.close()
    print(" Base de datos inicializada →", DB_PATH)

# ─── Callback de mensajes ─────────────────────────────────────
def al_recibir_mensaje(cliente, datos_usuario, mensaje):
    topic   = mensaje.topic
    payload = json.loads(mensaje.payload.decode("utf-8"))

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
 
    if "/gps" in topic:
        cur.execute(
            "INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp) VALUES (?,?,?,?,?)",
            (payload["vehicle_id"], payload["lat"], payload["lng"],
             payload["speed"], payload["timestamp"]),
        )
        print(f"   GPS  | {payload['vehicle_id']} | "
              f"({payload['lat']}, {payload['lng']}) | {payload['speed']} km/h")
 
    elif "/temperatura" in topic:
        temperatura = payload["temperature"]
        if temperatura > UMBRAL_TEMPERATURA:
            print(f"   ALERTA TEMPERATURA | {payload['vehicle_id']} | "
                  f"{temperatura}°C > {UMBRAL_TEMPERATURA}°C")
        cur.execute(
            "INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp) VALUES (?,?,?,?)",
            (payload["vehicle_id"], temperatura, payload["unit"], payload["timestamp"]),
        )
        print(f"    TEMP | {payload['vehicle_id']} | {temperatura}°C")
 
    elif "/combustible" in topic:
        fuel_level = payload["fuel_level"]
        if fuel_level < UMBRAL_COMBUSTIBLE:
            print(f"   ALERTA COMBUSTIBLE | {payload['vehicle_id']} | "
                  f"{fuel_level}% < {UMBRAL_COMBUSTIBLE}%")
        cur.execute(
            "INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp) VALUES (?,?,?,?)",
            (payload["vehicle_id"], fuel_level, payload["unit"], payload["timestamp"]),
        )
        print(f"   FUEL | {payload['vehicle_id']} | {fuel_level}%")
 
    con.commit()
    con.close()
 
 
def on_connect(cliente, datos_usuario, flags, rc):
    if rc == 0:
        print(f"[{datetime.now().isoformat()}]  Conectado al broker MQTT")
        # Suscribirse a todos los topics de la flota
        for topic in ["flota/+/gps", "flota/+/temperatura", "flota/+/combustible"]:
            cliente.subscribe(topic, qos=1)
            print(f"    Suscrito a: {topic}")
    else:
        print(f" Error de conexión (rc={rc})")
 
 
# ─── Principal ────────────────────────────────────────────────
def principal():
    inicializar_base_datos()
 
    cliente = mqtt.Client(client_id="suscriptor_telemetria")
    cliente.on_connect  = on_connect
    cliente.on_message  = al_recibir_mensaje
 
    cliente.connect(BROKER, PORT, keepalive=60)
 
    print("\n Suscriptor activo. Escuchando topics flota/+/...\n")
    cliente.loop_forever()
 
 
if __name__ == "__main__":
    principal()