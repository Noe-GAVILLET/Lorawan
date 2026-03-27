# Dataset description

## 1) Objectif

Documenter le jeu de donnees utilise pour l'evaluation du jumeau numerique.

## 2) Source et collecte

- Source principale: application de simulation (temperature, masse) via MQTT.
- Source secondaire (si indisponibilite capteur): donnees simulees, clairement annotees.
- Frequence retenue: 1 mesure / 10 minutes.
- Timezone: UTC.

## 3) Format

- Format de travail: InfluxDB (series temporelles).
- Format d'analyse: CSV exporte vers `data/processed/hive_timeseries.csv`.

## 4) Schema de donnees (CSV)

| Colonne | Type | Unite | Obligatoire | Description |
|---|---|---|---|---|
| timestamp | datetime ISO-8601 | UTC | oui | horodatage de la mesure |
| temperature_real | float | C | oui | temperature mesuree dans la ruche |
| masse_real | float | kg | oui | masse mesuree |

## 5) Mapping MQTT -> CSV

| Champ MQTT | Champ CSV |
|---|---|
| temperature | temperature_real |
| mass | masse_real |
| timestamp | timestamp |

Si `timestamp` absent dans le message MQTT, le timestamp de reception UTC est utilise.

## 6) Regles qualite appliquees

- Suppression des doublons stricts (timestamp + valeurs identiques).
- Verification ordre chronologique.
- Bornes physiques:
	- temperature_real entre 10 et 50 C
	- masse_real entre 0 et 200 kg
- Traitement manquants:
	- gap <= 20 min: interpolation lineaire
	- gap > 20 min: exclusion des points des metriques

## 7) Statistiques a remplir avant rendu

- Nombre total de points:
- Periode couverte (debut/fin):
- Taux de valeurs manquantes:
- Nombre de points exclus (outliers):
- Nombre de points interpol es: