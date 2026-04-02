import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


MQTT_HOST = env("MQTT_HOST", "localhost")
MQTT_PORT = int(env("MQTT_PORT", "1883"))
MQTT_TOPIC = env("MQTT_TOPIC", "hive/+/telemetry")
MQTT_USERNAME = env("MQTT_USERNAME", "")
MQTT_PASSWORD = env("MQTT_PASSWORD", "")
MQTT_CONNECT_RETRY_SECONDS = float(env("MQTT_CONNECT_RETRY_SECONDS", "5"))

INFLUX_URL = env("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = env("INFLUX_TOKEN", "")
INFLUX_ORG = env("INFLUX_ORG", "")
INFLUX_BUCKET = env("INFLUX_BUCKET", "hive")
INFLUX_MEASUREMENT = env("INFLUX_MEASUREMENT", "hive_telemetry")


if not INFLUX_TOKEN or not INFLUX_ORG:
    raise RuntimeError(
        "Missing INFLUX_TOKEN or INFLUX_ORG. Set environment variables before running."
    )


influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def parse_timestamp(payload: Dict[str, Any]) -> datetime:
    raw_ts = payload.get("timestamp")
    if isinstance(raw_ts, str):
        try:
            # Accept ISO-8601 forms including trailing Z.
            return datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(
                timezone.utc
            )
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def coerce_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def extract_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Supports direct payloads and optional nested wrapper under uplink_message.decoded_payload.
    if "uplink_message" in payload and isinstance(payload["uplink_message"], dict):
        uplink = payload["uplink_message"]
        decoded = uplink.get("decoded_payload")
        if isinstance(decoded, dict):
            payload = decoded

    temperature = coerce_float(payload.get("temperature") or payload.get("temp"))
    mass = coerce_float(payload.get("mass") or payload.get("weight"))
    ambient_temp = coerce_float(payload.get("ambient_temp") or payload.get("ambient"))

    ambient_humidity = coerce_float(payload.get("ambient_humidity"))
    battery_v = coerce_float(payload.get("battery_v"))
    lora_rssi = coerce_float(payload.get("lora_rssi"))
    lora_snr = coerce_float(payload.get("lora_snr"))

    if temperature is None or mass is None:
        raise ValueError("Payload missing required fields: temperature and mass")

    result: Dict[str, Any] = {
        "temperature": temperature,
        "mass": mass,
        "timestamp": parse_timestamp(payload),
    }
    if ambient_temp is not None:
        result["ambient_temp"] = ambient_temp
    if ambient_humidity is not None:
        result["ambient_humidity"] = ambient_humidity
    if battery_v is not None:
        result["battery_v"] = battery_v
    if lora_rssi is not None:
        result["lora_rssi"] = lora_rssi
    if lora_snr is not None:
        result["lora_snr"] = lora_snr
    return result


def on_connect(client: mqtt.Client, userdata: Any, flags: Dict[str, Any], rc: int) -> None:
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed MQTT connection, code={rc}")


def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
    try:
        body = json.loads(msg.payload.decode("utf-8"))
        fields = extract_payload(body)

        topic_parts = msg.topic.split("/")
        device_id = topic_parts[1] if len(topic_parts) > 1 else "unknown"

        point = (
            Point(INFLUX_MEASUREMENT)
            .tag("device_id", device_id)
            .field("temperature", fields["temperature"])
            .field("mass", fields["mass"])
            .time(fields["timestamp"], WritePrecision.S)
        )
        if "ambient_temp" in fields:
            point = point.field("ambient_temp", fields["ambient_temp"])
        if "ambient_humidity" in fields:
            point = point.field("ambient_humidity", fields["ambient_humidity"])
        if "battery_v" in fields:
            point = point.field("battery_v", fields["battery_v"])
        if "lora_rssi" in fields:
            point = point.field("lora_rssi", fields["lora_rssi"])
        if "lora_snr" in fields:
            point = point.field("lora_snr", fields["lora_snr"])

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(
            f"Written device={device_id} temp={fields['temperature']} "
            f"mass={fields['mass']} ambient={fields.get('ambient_temp', 'N/A')}"
        )
    except Exception as exc:
        print(f"Message processing error on topic {msg.topic}: {exc}")


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
    mqtt_client = mqtt.Client()

    if MQTT_USERNAME:
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    connect_with_retry(mqtt_client)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    main()
