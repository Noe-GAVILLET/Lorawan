"""
Export des données InfluxDB vers le fichier CSV d'analyse.

Usage :
    INFLUX_TOKEN=<token> INFLUX_ORG=<org> python model/export_csv.py

Variables d'environnement :
    INFLUX_URL      URL du serveur InfluxDB  (défaut : http://localhost:8086)
    INFLUX_TOKEN    Token d'authentification (obligatoire)
    INFLUX_ORG      Organisation InfluxDB    (obligatoire)
    INFLUX_BUCKET   Bucket                   (défaut : hive)
    INFLUX_MEASUREMENT  Measurement          (défaut : hive_telemetry)
    RANGE           Fenêtre temporelle Flux  (défaut : -7d ; ex. -48h, -30d)
    OUTPUT_PATH     Chemin CSV de sortie     (défaut : data/processed/hive_timeseries.csv)
"""
import os
import sys
from pathlib import Path

import pandas as pd
from influxdb_client import InfluxDBClient

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


INFLUX_URL = env("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = env("INFLUX_TOKEN")
INFLUX_ORG = env("INFLUX_ORG")
INFLUX_BUCKET = env("INFLUX_BUCKET", "hive")
INFLUX_MEASUREMENT = env("INFLUX_MEASUREMENT", "hive_telemetry")
RANGE = env("RANGE", "-7d")
OUTPUT_PATH = Path(env("OUTPUT_PATH", str(BASE_DIR / "data" / "processed" / "hive_timeseries.csv")))


def main() -> None:
    if not INFLUX_TOKEN or not INFLUX_ORG:
        print(
            "ERREUR : INFLUX_TOKEN et INFLUX_ORG doivent être définis.\n"
            "  Exemple : INFLUX_TOKEN=xxx INFLUX_ORG=hive-org python model/export_csv.py",
            file=sys.stderr,
        )
        sys.exit(1)

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()

    query = f"""
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: {RANGE})
  |> filter(fn: (r) => r["_measurement"] == "{INFLUX_MEASUREMENT}")
  |> filter(fn: (r) => r["_field"] == "temperature" or r["_field"] == "mass")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
  |> keep(columns: ["_time", "temperature", "mass"])
"""

    print(f"Interrogation InfluxDB ({INFLUX_URL}) bucket={INFLUX_BUCKET} range={RANGE} ...")
    df = query_api.query_data_frame(query)

    if df is None or (isinstance(df, list) and len(df) == 0):
        print("Aucune donnée retournée. Vérifier que le publisher envoie des données.")
        sys.exit(1)

    # query_data_frame peut retourner une liste de DataFrames si plusieurs tables
    if isinstance(df, list):
        df = pd.concat(df, ignore_index=True)

    if df.empty:
        print("Aucune donnée retournée. Vérifier que le publisher envoie des données.")
        sys.exit(1)

    # Nettoyage et renommage
    df = df.rename(
        columns={"_time": "timestamp", "temperature": "temperature_real", "mass": "masse_real"}
    )
    df = df[["timestamp", "temperature_real", "masse_real"]].copy()

    # Convertir le timestamp en ISO-8601 UTC sans fuseaux horaires dans la chaîne
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

    # Qualité minimale : doublons stricts et tri chronologique
    df = df.drop_duplicates().sort_values("timestamp").reset_index(drop=True)

    # Écriture
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Export terminé : {len(df)} lignes → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
