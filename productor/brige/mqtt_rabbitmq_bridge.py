

import json
from datetime import datetime
import paho.mqtt.client as mqtt
import pika

# ─── Configuración ────────────────────────────────────────────
MQTT_BROKER    = "localhost"
MQTT_PORT      = 1883
RABBITMQ_HOST  = "localhost"


UMBRAL_TEMPERATURA = 4.0
UMBRAL_COMBUSTIBLE = 20.0

# Nombres de colas RabbitMQ
COLA_GPS         = "cola.gps.telemetria"
COLA_TEMPERATURA = "cola.alertas.temperatura"
COLA_COMBUSTIBLE = "cola.combustible.nivel"


# ─── RabbitMQ ────────────────────────────────────────────────
def configurar_rabbitmq():
    """Crea conexión, canal y declara las colas durables."""
    credenciales = pika.PlainCredentials("admin", "admin123")
    parametros   = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=credenciales,
        heartbeat=600,
        blocked_connection_timeout=300,
    )
    conexion = pika.BlockingConnection(parametros)
    canal    = conexion.channel()

    for cola in [COLA_GPS, COLA_TEMPERATURA, COLA_COMBUSTIBLE]:
        canal.queue_declare(queue=cola, durable=True)

    print("Colas RabbitMQ creadas exitosamente:")
    print(f"   · {COLA_GPS}")
    print(f"   · {COLA_TEMPERATURA}")
    print(f"   · {COLA_COMBUSTIBLE}")
    return conexion, canal


def publicar_rabbitmq(canal, cola, mensaje):
    """Publica un mensaje en RabbitMQ con persistencia."""
    canal.basic_publish(
        exchange="",
        routing_key=cola,
        body=json.dumps(mensaje).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),  # persistente
    )


# ─── Callback MQTT ───────────────────────────────────────────
def al_recibir_mensaje_mqtt(cliente, datos_usuario, mensaje):
    topic   = mensaje.topic
    payload = json.loads(mensaje.payload.decode("utf-8"))
    canal   = datos_usuario["rabbitmq_channel"]

    if "/gps" in topic:
        # Todos los datos GPS se envían a RabbitMQ
        publicar_rabbitmq(canal, COLA_GPS, payload)
        print(f"   GPS → {COLA_GPS} | {payload.get('vehicle_id')}")

    elif "/temperatura" in topic:
        temperatura = payload.get("temperature", 0)
        if temperatura > UMBRAL_TEMPERATURA:
            alerta = {
                "type":    "TEMP_ALERT",
                "message": "Temperatura de cadena de frío excedida",
                **payload,
            }
            publicar_rabbitmq(canal, COLA_TEMPERATURA, alerta)
            print(f"   TEMP_ALERT → {COLA_TEMPERATURA} | "
                  f"{payload.get('vehicle_id')} | {temperatura}°C")

    elif "/combustible" in topic:
        fuel_level = payload.get("fuel_level", 100)
        if fuel_level < UMBRAL_COMBUSTIBLE:
            alerta = {
                "type":    "FUEL_LOW",
                "message": "Nivel de combustible bajo",
                **payload,
            }
            publicar_rabbitmq(canal, COLA_COMBUSTIBLE, alerta)
            print(f"   FUEL_LOW → {COLA_COMBUSTIBLE} | "
                  f"{payload.get('vehicle_id')} | {fuel_level}%")


def on_connect(cliente, datos_usuario, flags, rc):
    if rc == 0:
        print(f"[{datetime.now().isoformat()}]  Bridge conectado al broker MQTT")
        cliente.subscribe("flota/#", qos=1)
        print("    Suscrito a: flota/#")
    else:
        print(f"Error de conexión MQTT (rc={rc})")


# ─── Principal ────────────────────────────────────────────────
def principal():
    print("Iniciando Bridge MQTT → RabbitMQ...\n")

    # 1. Configurar RabbitMQ
    conexion_rabbit, canal_rabbit = configurar_rabbitmq()

    # 2. Configurar cliente MQTT
    cliente = mqtt.Client(
        client_id="mqtt_rabbitmq_bridge",
        userdata={"rabbitmq_channel": canal_rabbit},
    )
    cliente.on_connect = on_connect
    cliente.on_message = al_recibir_mensaje_mqtt

    cliente.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    print("\n Bridge MQTT-RabbitMQ iniciado. Esperando mensajes...\n")

    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\n Deteniendo bridge...")
        cliente.disconnect()
        conexion_rabbit.close()
        print("   Conexiones cerradas.")


if __name__ == "__main__":
    principal()