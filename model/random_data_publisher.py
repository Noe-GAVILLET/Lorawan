import json
import os
import random
import time
import math
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient

def get_last_state() -> tuple[float, float]:
    url = os.getenv("INFLUX_URL", "")
    token = os.getenv("INFLUX_TOKEN", "")
    org = os.getenv("INFLUX_ORG", "")
    bucket = os.getenv("INFLUX_BUCKET", "hive")
    
    mass, batt = 45.0, 4.2
    
    if not all([url, token, org]):
        print("WARN: Influx credentials missing, starting from default state.")
        return mass, batt
        
    try:
        client = InfluxDBClient(url=url, token=token, org=org, timeout=5000)
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r._measurement == "hive_telemetry")
          |> filter(fn: (r) => r._field == "mass" or r._field == "battery_v")
          |> last()
        '''
        tables = client.query_api().query(query)
        for table in tables:
            for record in table.records:
                if record.get_field() == "mass":
                    mass = record.get_value()
                if record.get_field() == "battery_v":
                    batt = record.get_value()
        print(f"INFO: Recovered state from DB: mass={mass}, battery={batt}")
    except Exception as e:
        print(f"WARN: Failed to query last state from InfluxDB: {e}")
        
    return mass, batt

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

SCENARIO = env("SCENARIO", "normal")          # normal | extreme
LORAWAN_PDR = float(env("LORAWAN_PDR", "0.9"))  # 90% Packet Delivery Rate

# Masse minimale : structure bois + cadres d'une ruche Langstroth vide (~5 kg)
MASS_FLOOR_KG = 5.0

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
    
    current_mass, battery_v = get_last_state()
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
                
            # Mode "extreme" -> ESSAIMAGE 
            if SCENARIO == "extreme":
                # Perte de 2.5 kg sur cette période
                current_mass -= 2.5 * time_step_hours
                internal_temp += random.uniform(0.5, 1.5) # Activité due au départ

            # Plancher physique : une ruche vide (bois + cadres) pèse ~5 kg
            current_mass = max(current_mass, MASS_FLOOR_KG)

            # Simulation Batterie, Humidité ambiante et Radio LoRa
            battery_v -= 0.01 * time_step_hours
            if battery_v < 3.3:
                battery_v = 4.2 # Recharge théorique (panneau solaire ou remplacement)

            # Humidité ambiante : corrélation inverse avec la température
            # (rosée nocturne, air chaud plus sec en journée)
            humidity_base = 75.0 - (amb_temp - 10.0) * (30.0 / 16.0)  # 75% à 10°C, ~45% à 26°C
            amb_humidity = round(humidity_base + random.uniform(-4.0, 4.0), 1)
            amb_humidity = max(30.0, min(95.0, amb_humidity))

            # RSSI puis SNR corrélé (signal fort => meilleur rapport signal/bruit)
            lora_rssi = random.uniform(-115.0, -90.0)
            # SNR varie entre -10 et +5 dB, lié au RSSI par régression linéaire + bruit
            snr_from_rssi = (lora_rssi + 115.0) / 25.0 * 15.0 - 10.0  # [-10, +5] pour RSSI [-115, -90]
            lora_snr = round(snr_from_rssi + random.uniform(-2.0, 2.0), 1)

            payload = {
                "timestamp": now_utc.isoformat().replace("+00:00", "Z"),
                "temperature": round(internal_temp, 2),
                "mass": round(current_mass, 4),
                "ambient_temp": round(amb_temp, 2),
                "ambient_humidity": amb_humidity,
                "battery_v": round(battery_v, 3),
                "lora_rssi": round(lora_rssi, 1),
                "lora_snr": lora_snr,
                # Métadonnées expérimentales — permettent à train_eval.py de distinguer H1 vs H2
                "scenario": SCENARIO,
                "lorawan_pdr": LORAWAN_PDR,
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
