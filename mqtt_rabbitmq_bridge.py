import json

import pika
import paho.mqtt.client as mqtt


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
RABBITMQ_HOST = "localhost"


COLA_GPS = "cola.gps.telemetria"
COLA_TEMP = "cola.alertas.temperatura"
COLA_FUEL = "cola.combustible.nivel"


def configurar_rabbitmq():
    credenciales = pika.PlainCredentials("admin", "admin123")

    conexion = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=5672,
            credentials=credenciales
        )
    )

    canal = conexion.channel()

    canal.queue_declare(queue=COLA_GPS, durable=True)
    canal.queue_declare(queue=COLA_TEMP, durable=True)
    canal.queue_declare(queue=COLA_FUEL, durable=True)

    print("Colas de RabbitMQ creadas.")

    return conexion, canal


def publicar_rabbitmq(canal, cola, mensaje):
    canal.basic_publish(
        exchange="",
        routing_key=cola,
        body=json.dumps(mensaje),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    print(f"Enviado a RabbitMQ -> {cola}: {mensaje}")


def on_connect(cliente, userdata, flags, rc):
    print(f"Bridge conectado a Mosquitto. Codigo: {rc}")
    cliente.subscribe("flota/#")
    print("Bridge suscrito a flota/#")


def on_message(cliente, userdata, mensaje):
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode())

    canal = userdata["canal_rabbit"]

    if "/gps" in topic:
        publicar_rabbitmq(canal, COLA_GPS, payload)

    elif "/temperatura" in topic:
        if payload["temperature"] > 4:
            alerta = {
                "type": "TEMP_ALERT",
                "message": "Temperatura excedida",
                **payload
            }

            publicar_rabbitmq(canal, COLA_TEMP, alerta)

    elif "/combustible" in topic:
        if payload["fuel_level"] < 20:
            alerta = {
                "type": "FUEL_LOW",
                "message": "Combustible bajo",
                **payload
            }

            publicar_rabbitmq(canal, COLA_FUEL, alerta)


def principal():
    conexion_rabbit, canal_rabbit = configurar_rabbitmq()

    cliente = mqtt.Client(userdata={"canal_rabbit": canal_rabbit})
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    cliente.connect(MQTT_BROKER, MQTT_PORT, 60)

    print("Bridge MQTT-RabbitMQ iniciado...")

    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("Bridge detenido.")
        cliente.disconnect()
        conexion_rabbit.close()


if __name__ == "__main__":
    principal()