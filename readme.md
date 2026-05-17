Descripción General

Este proyecto implementa un sistema distribuido para monitoreo de flotas vehiculares utilizando:

MQTT para comunicación IoT
RabbitMQ como broker empresarial
Python para simulación y procesamiento
Spring Boot para microservicios y API REST

El sistema simula sensores de vehículos que generan telemetría en tiempo real, la transmiten mediante MQTT y posteriormente son procesadas y consumidas por microservicios Spring Boot utilizando RabbitMQ.

Arquitectura del Sistema
[Sensores Python]
        |
        | MQTT
        v
[ Mosquitto Broker ]
        |
        | Bridge Python MQTT → RabbitMQ
        v
[ RabbitMQ ]
        |
        | AMQP
        v
[ Spring Boot Microservices ]
        |
        | REST API
        v
[ Cliente / Postman ]
Tecnologías Utilizadas
Backend y Mensajería
Python 3
Java 17
Spring Boot
RabbitMQ
Mosquitto MQTT
Librerías Python
paho-mqtt
pika
sqlite3
Dependencias Spring Boot
Spring Web
Spring AMQP
Spring Data JPA
H2 Database
Infraestructura
Docker
Docker Compose
Estructura del Proyecto
practica-distribuidos/
│
├── bridge/
│   └── mqtt_rabbitmq_bridge.py
│
├── database/
│   └── telemetria.db
│
├── mosquitto/
│
├── sensor_simulador/
│   └── sensorsimulador.py
│
├── suscriber/
│   └── suscriber.py
│
├── docker-compose.yml
├── requirements.txt
│
└── fleet-monitor/
    │
    ├── src/main/java/com/fleet/monitor/
    │
    ├── config/
    │   └── RabbitMQConfig.java
    │
    ├── consumer/
    │   ├── GpsConsumer.java
    │   └── AlertConsumer.java
    │
    ├── controller/
    │   └── FleetController.java
    │
    └── resources/
        └── application.properties
Parte 1 - MQTT + RabbitMQ + Python
Objetivo

Implementar un sistema de telemetría IoT utilizando MQTT y RabbitMQ.

Componentes
1. Sensor Simulator

Archivo:

sensor_simulador/sensorsimulador.py

Simula sensores vehiculares enviando:

GPS
Temperatura
Combustible
Velocidad

mediante MQTT.

2. Mosquitto MQTT Broker

Gestiona la comunicación MQTT entre sensores y consumidores.

Se ejecuta mediante Docker Compose.

3. MQTT-RabbitMQ Bridge

Archivo:

bridge/mqtt_rabbitmq_bridge.py

Responsabilidades:

Suscribirse a topics MQTT
Recibir telemetría
Enviar mensajes a RabbitMQ

Actúa como puente entre IoT y procesamiento empresarial.

4. RabbitMQ

Broker AMQP encargado de:

colas
persistencia
distribución empresarial

Colas utilizadas:

cola.gps.telemetria
cola.alertas.temperatura
cola.combustible.nivel
cola.notificaciones
5. Subscriber

Archivo:

suscriber/suscriber.py

Consume mensajes y almacena telemetría en SQLite.

Docker Compose

Levantar infraestructura:

docker compose up -d

Servicios:

Mosquitto
RabbitMQ
Instalación Python
Crear entorno virtual
python3 -m venv venv
Activar entorno
source venv/bin/activate
Instalar dependencias
pip install -r requirements.txt
Ejecución Parte 1
1. Levantar Docker
docker compose up -d
2. Ejecutar simulador
python sensor_simulador/sensorsimulador.py
3. Ejecutar bridge MQTT → RabbitMQ
python bridge/mqtt_rabbitmq_bridge.py
4. Ejecutar subscriber
python suscriber/suscriber.py
Parte 2 - Spring Boot + RabbitMQ
Objetivo

Implementar microservicios Spring Boot que consuman RabbitMQ y expongan una API REST.

Componentes Spring Boot
1. RabbitMQConfig

Configura las colas RabbitMQ.

Archivo:

RabbitMQConfig.java
2. GpsConsumer

Consume mensajes GPS desde RabbitMQ.

Archivo:

GpsConsumer.java
3. AlertConsumer

Consume alertas de:

temperatura
combustible

Archivo:

AlertConsumer.java
4. FleetController

Expone API REST.

Endpoints:

GET /api/fleet/status
GET /api/fleet/vehicle/{id}/telemetria
Configuración Spring Boot

Archivo:

application.properties

Configuración RabbitMQ:

spring.rabbitmq.host=localhost
spring.rabbitmq.port=5672
spring.rabbitmq.username=guest
spring.rabbitmq.password=guest
Ejecución Spring Boot

Entrar al proyecto:

cd fleet-monitor

Ejecutar:

mvn spring-boot:run
Verificación API REST
Estado general
curl http://localhost:8080/api/fleet/status
Telemetría por vehículo
curl http://localhost:8080/api/fleet/vehicle/VH-001/telemetria
RabbitMQ Management

Panel administrativo:

http://localhost:15672

Credenciales:

guest / guest
Flujo Completo del Sistema
Sensores Python generan telemetría
Mosquitto recibe mensajes MQTT
Bridge Python consume MQTT
Bridge publica en RabbitMQ
Spring Boot consume colas RabbitMQ
API REST expone información procesada
Conceptos Clave
MQTT

Protocolo liviano orientado a IoT.

Características:

bajo consumo
comunicación publish/subscribe
eficiente para sensores
RabbitMQ

Broker empresarial basado en AMQP.

Características:

colas persistentes
alta confiabilidad
procesamiento empresarial
Bridge MQTT → RabbitMQ

Permite integrar:

dispositivos IoT
sistemas empresariales

convirtiendo mensajes MQTT en eventos RabbitMQ.

Base de Datos

Se utilizan dos bases de datos:

SQLite

Utilizada por Python para almacenamiento local.

H2 Database

Utilizada por Spring Boot en memoria.

Puertos Utilizados
Servicio	Puerto
Mosquitto MQTT	1883
RabbitMQ AMQP	5672
RabbitMQ Management	15672
Spring Boot API	8080