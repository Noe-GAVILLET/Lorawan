import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


MQTT_HOST = env("MQTT_HOST", "localhost")
MQTT_PORT = int(env("MQTT_PORT", "1883"))
MQTT_TOPIC_BASE = env("MQTT_TOPIC_BASE", "hive")
DEVICE_ID = env("DEVICE_ID", "ruche-01")
MQTT_USERNAME = env("MQTT_USERNAME", "")
MQTT_PASSWORD = env("MQTT_PASSWORD", "")
PUBLISH_INTERVAL_SECONDS = float(env("PUBLISH_INTERVAL_SECONDS", "5"))
MQTT_CONNECT_RETRY_SECONDS = float(env("MQTT_CONNECT_RETRY_SECONDS", "5"))

# Mode de simulation :
#   normal  — marche aléatoire dans les limites physiques
#   extreme — injecte périodiquement des sauts brusques (pour tester H2)
SCENARIO = env("SCENARIO", "normal")

# Probabilité d'injecter un spike à chaque mesure en mode extreme
SPIKE_PROBABILITY = float(env("SPIKE_PROBABILITY", "0.08"))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def connect_with_retry(client: mqtt.Client) -> None:
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            return
        except Exception as exc:
            print(
                f"MQTT connection failed ({exc}). Retrying in {MQTT_CONNECT_RETRY_SECONDS}s..."
            )
            time.sleep(MQTT_CONNECT_RETRY_SECONDS)


def main() -> None:
    client = mqtt.Client()

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    connect_with_retry(client)
    client.loop_start()

    topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/telemetry"

    temperature = 34.5
    mass = 42.0

    print(f"Publishing telemetry to topic: {topic}  [SCENARIO={SCENARIO}]")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Marche aléatoire de base
            temperature += random.uniform(-0.2, 0.2)
            mass += random.uniform(-0.03, 0.03)

            # Mode extrême : injection périodique de spikes
            if SCENARIO == "extreme" and random.random() < SPIKE_PROBABILITY:
                direction_t = random.choice([-1, 1])
                direction_m = random.choice([-1, 1])
                temperature += direction_t * random.uniform(2.0, 5.0)
                mass += direction_m * random.uniform(0.3, 0.8)

            temperature = clamp(temperature, 20.0, 45.0)
            mass = clamp(mass, 30.0, 60.0)

            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "temperature": round(temperature, 2),
                "mass": round(mass, 2),
            }

            client.publish(topic, json.dumps(payload), qos=0, retain=False)
            print(payload)
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
