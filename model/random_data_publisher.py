import json
import os
import random
import time
import math
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

SCENARIO = env("SCENARIO", "normal") # normal | extreme
LORAWAN_PDR = float(env("LORAWAN_PDR", "0.9")) # 90% Packet Delivery Rate

def connect_with_retry(client: mqtt.Client) -> None:
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            return
        except Exception as exc:
            print(f"MQTT connection failed ({exc}). Retrying in {MQTT_CONNECT_RETRY_SECONDS}s...")
            time.sleep(MQTT_CONNECT_RETRY_SECONDS)

def get_ambient_temperature(t_hours: float) -> float:
    # Cycle sinusoidal : max à 15h, min à 03h
    # Moyenne 18 C, Amplitude 8 C => min 10, max 26
    rad = 2 * math.pi * (t_hours - 9) / 24.0
    return 18.0 + 8.0 * math.sin(rad)

def main() -> None:
    client = mqtt.Client()

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    connect_with_retry(client)
    client.loop_start()

    topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/telemetry"

    print(f"Publishing BIOLOGICAL telemetry to topic: {topic}  [SCENARIO={SCENARIO}, PDR={LORAWAN_PDR}]")
    print("Press Ctrl+C to stop.")
    
    current_mass = 45.0 # kg
    honey_consumed_per_hour_base = 0.005 # kg/h
    
    try:
        while True:
            # Pour accelerer la simulation temporelle si PUBLISH_INTERVAL_SECONDS est faible
            # => on accélère le temps simulé (ex: 5s réel = 10 minutes simulées)
            # Sinon, en conditions réelles, utiliser le vrai timestamp.
            # Ici pour faciliter vos tests on utilise le vrai temps de la machine
            now_utc = datetime.now(timezone.utc)
            t_hours = now_utc.hour + now_utc.minute / 60.0 + now_utc.second / 3600.0
            
            amb_temp = get_ambient_temperature(t_hours)
            
            # Thermorégulation (Biologique calcul : BEEHAVE-like)
            internal_temp = 34.5 + random.uniform(-0.1, 0.1)
            
            # Budget énergétique
            temp_diff = max(0, 34.5 - amb_temp)
            honey_consumed = honey_consumed_per_hour_base + (temp_diff * 0.001)
            
            # Cycle de butinage
            time_step_hours = PUBLISH_INTERVAL_SECONDS / 3600.0
            mass_delta = - (honey_consumed * time_step_hours)
            
            if 8.0 <= t_hours < 11.0:
                mass_delta -= 0.15 * time_step_hours # Les butineuses partent (- poids)
            elif 11.0 <= t_hours < 18.0:
                mass_delta += 0.20 * time_step_hours # Retour avec nectar (+ poids)
                
            current_mass += mass_delta
            
            # Stress thermique extrême
            if amb_temp < 12.0:
                internal_temp -= 0.5 * (12.0 - amb_temp) / 12.0
                
            # Mode "extreme" -> ESSAIMAGE brutal entre 13:30 et 14:30
            if SCENARIO == "extreme" and 13.5 <= t_hours <= 14.5:
                # Perte de 2.5 kg sur cette période
                current_mass -= 2.5 * time_step_hours
                internal_temp += random.uniform(0.5, 1.5) # Activité due au départ

            # On empêche des valeurs négatives irréalistes
            current_mass = max(current_mass, 0.0)

            payload = {
                "timestamp": now_utc.isoformat().replace("+00:00", "Z"),
                "temperature": round(internal_temp, 2),
                "mass": round(current_mass, 2),
                "ambient_temp": round(amb_temp, 2)
            }

            # LoRaWAN Simulateur MAC layer (Packet loss)
            if random.random() <= LORAWAN_PDR:
                client.publish(topic, json.dumps(payload), qos=0, retain=False)
                print(f"Sent: {payload}")
            else:
                print(f"[LoRaSim] Packet Dropped (Collision/PathLoss). PDR={LORAWAN_PDR}")

            time.sleep(PUBLISH_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
