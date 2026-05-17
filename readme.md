# 🚗 Fleet Monitor

> Sistema distribuido de telemetría vehicular en tiempo real

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-17-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=flat-square&logo=rabbitmq&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-3C5280?style=flat-square&logo=eclipsemosquitto&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

---

## Descripción General

Sistema que simula sensores de vehículos generando telemetría en tiempo real, transmitida mediante **MQTT** y procesada por microservicios **Spring Boot** a través de **RabbitMQ**.

---

## Arquitectura del Sistema

```
┌─────────────────────┐
│   Sensores Python   │  GPS · Temperatura · Combustible · Velocidad
└────────┬────────────┘
         │  MQTT publish
         ▼
┌─────────────────────┐
│  Mosquitto Broker   │  puerto 1883
└────────┬────────────┘
         │  MQTT subscribe
         ▼
┌─────────────────────┐
│  MQTT → RabbitMQ    │  mqtt_rabbitmq_bridge.py
│      Bridge         │
└────────┬────────────┘
         │  AMQP publish
         ▼
┌─────────────────────┐
│     RabbitMQ        │  colas · persistencia · distribución
└────────┬────────────┘
         │  AMQP consume
         ▼
┌─────────────────────┐
│  Spring Boot        │  GpsConsumer · AlertConsumer · FleetController
│  Microservices      │
└────────┬────────────┘
         │  REST API
         ▼
┌─────────────────────┐
│  Cliente / Postman  │  localhost:8080
└─────────────────────┘
```

---

## Estructura del Proyecto

```
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
    └── src/main/java/com/fleet/monitor/
        ├── config/
        │   └── RabbitMQConfig.java
        ├── consumer/
        │   ├── GpsConsumer.java
        │   └── AlertConsumer.java
        ├── controller/
        │   └── FleetController.java
        └── resources/
            └── application.properties
```

---

## Parte 1 — MQTT + RabbitMQ + Python

### Componentes

| Componente | Archivo | Descripción |
|---|---|---|
| Sensor Simulator | `sensor_simulador/sensorsimulador.py` | Simula sensores vehiculares (GPS, temperatura, combustible, velocidad) |
| Mosquitto Broker | Docker Compose | Gestiona comunicación MQTT entre sensores y consumidores |
| MQTT-RabbitMQ Bridge | `bridge/mqtt_rabbitmq_bridge.py` | Suscribe topics MQTT y publica en RabbitMQ |
| RabbitMQ | Docker Compose | Broker AMQP con colas persistentes |
| Subscriber | `suscriber/suscriber.py` | Consume mensajes y almacena telemetría en SQLite |

### Colas RabbitMQ

| Cola | Tipo |
|---|---|
| `cola.gps.telemetria` | GPS |
| `cola.alertas.temperatura` | Alerta |
| `cola.combustible.nivel` | Nivel |
| `cola.notificaciones` | Notificación |

### Instalación y Ejecución

```bash
# 1. Levantar infraestructura
docker compose up -d

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar simulador de sensores
python sensor_simulador/sensorsimulador.py

# 5. Ejecutar bridge MQTT → RabbitMQ
python bridge/mqtt_rabbitmq_bridge.py

# 6. Ejecutar subscriber
python suscriber/suscriber.py
```

---

## Parte 2 — Spring Boot + RabbitMQ

### Componentes

| Componente | Archivo | Descripción |
|---|---|---|
| RabbitMQConfig | `RabbitMQConfig.java` | Configura las colas RabbitMQ |
| GpsConsumer | `GpsConsumer.java` | Consume mensajes GPS desde RabbitMQ |
| AlertConsumer | `AlertConsumer.java` | Consume alertas de temperatura y combustible |
| FleetController | `FleetController.java` | Expone la API REST |

### Configuración (`application.properties`)

```properties
spring.rabbitmq.host=localhost
spring.rabbitmq.port=5672
spring.rabbitmq.username=guest
spring.rabbitmq.password=guest
```

### Ejecución

```bash
cd fleet-monitor
mvn spring-boot:run
```

### Endpoints REST

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/fleet/status` | Estado general de la flota |
| `GET` | `/api/fleet/vehicle/{id}/telemetria` | Telemetría por vehículo |

```bash
# Verificar estado general
curl http://localhost:8080/api/fleet/status

# Consultar vehículo específico
curl http://localhost:8080/api/fleet/vehicle/VH-001/telemetria
```

---

## Puertos del Sistema

| Servicio | Puerto |
|---|---|
| Mosquitto MQTT | `1883` |
| RabbitMQ AMQP | `5672` |
| RabbitMQ Management | `15672` |
| Spring Boot API | `8080` |

> Panel de administración RabbitMQ: [http://localhost:15672](http://localhost:15672) — credenciales: `guest / guest`

---

## Bases de Datos

| Base de datos | Uso |
|---|---|
| **SQLite** | Almacenamiento local Python (`database/telemetria.db`) |
| **H2** | Base de datos en memoria para Spring Boot |

---

## Tecnologías

**Backend y Mensajería:** Python 3 · Java 17 · Spring Boot · RabbitMQ · Mosquitto MQTT

**Librerías Python:** `paho-mqtt` · `pika` · `sqlite3`

**Dependencias Spring Boot:** Spring Web · Spring AMQP · Spring Data JPA · H2 Database

**Infraestructura:** Docker · Docker Compose