# Dataset description — Données Simulées de Ruche IoT

> ⚠️ **Nature des données** : Ce jeu de données est entièrement **simulé** par le modèle biophysique `random_data_publisher.py`. Il ne provient pas de capteurs physiques réels. Cette simulation est le cœur de l'expérimentation : elle permet de contrôler précisément les variables (PDR, scénario d'essaimage) pour valider les hypothèses H1 et H2 dans des conditions reproductibles. Voir `docs/cahier_des_charges.md` § 3.2 pour la justification de ce choix.

## 1) Objectif

Documenter le jeu de données utilisé pour l'évaluation du Jumeau Numérique d'une ruche connectée. Les données simulent le comportement biophysique d'une colonie d'abeilles (thermorégulation, cycle de butinage, événement d'essaimage) transmis via le protocole MQTT avec simulation des pertes radio LoRaWAN (PDR configurable).

## 2) Source et collecte

- **Source** : application de simulation biophysique (`model/random_data_publisher.py`) — données entièrement générées par le modèle, transmises via MQTT.
- **Fréquence d'acquisition** : 1 message toutes les 5 secondes (dataset H1) ou toutes les 60 secondes (dataset H2 — intervalle réaliste LoRaWAN).
- **Pertes radio simulées** : PDR = 0,90 pour H1 (nominal) ; PDR = 0,65 pour H2 (dégradé).
- **Timezone** : UTC.

## 3) Format

- Format de travail : InfluxDB (séries temporelles).
- Format d'analyse : CSV exporté vers `data/processed/hive_timeseries.csv`.

## 4) Schéma de données (CSV)

| Colonne | Type | Unité | Obligatoire | Description |
|---|---|---|---|---|
| timestamp | datetime ISO-8601 | UTC | oui | Horodatage de la mesure |
| temperature_real | float | °C | oui | Température mesurée dans la ruche |
| masse_real | float | kg | oui | Masse mesurée de la ruche |

## 5) Correspondance MQTT → CSV

| Champ MQTT | Champ CSV |
|---|---|
| temperature | temperature_real |
| mass | masse_real |
| timestamp | timestamp |

Si `timestamp` absent dans le message MQTT, le timestamp de réception UTC est utilisé.

## 6) Règles qualité appliquées

- Suppression des doublons stricts (timestamp + valeurs identiques).
- Vérification de l'ordre chronologique.
- Bornes physiques :
	- `temperature_real` : entre 10 et 50 °C
	- `masse_real` : entre 0 et 200 kg
- Traitement des valeurs manquantes :
	- gap ≤ 20 min : interpolation linéaire
	- gap > 20 min : exclusion des points des métriques

## 7) Statistiques

- **Nombre total de points** : 5 216
- **Période couverte** : 2026-04-02T10:49:09 UTC → 2026-04-02T18:47:39 UTC (~8h)
- **Taux de paquets perdus (PDR=0.90)** : ~10 % (perte simulée côté publisher)
- **Nombre de points exclus (outliers)** : 0 (toutes les valeurs dans les bornes physiques)
- **Nombre de points interpolés** : estimé à ~521 (10 % × 5 216), gaps ≤ 20 min → interpolation linéaire appliquée par `train_eval.py`
- **Répartition par régime** :
  - Nominal : 4 560 points (~87 %)
  - Extrême (essaimage) : 656 points (~13 %)