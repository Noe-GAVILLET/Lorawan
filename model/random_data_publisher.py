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


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def main() -> None:
    client = mqtt.Client()

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/telemetry"

    temperature = 34.5
    mass = 42.0
    battery = 4.0

    print(f"Publishing random telemetry to topic: {topic}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Random walk to keep values realistic across time.
            temperature += random.uniform(-0.2, 0.2)
            mass += random.uniform(-0.03, 0.03)
            battery += random.uniform(-0.002, 0.0)

            temperature = clamp(temperature, 20.0, 45.0)
            mass = clamp(mass, 30.0, 60.0)
            battery = clamp(battery, 3.2, 4.2)

            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "temperature": round(temperature, 2),
                "mass": round(mass, 2),
                "battery": round(battery, 2),
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
