# Cahier des Charges — Jumeau Numérique Scientifique de Ruche IoT

**Module** : ETRS012 — Intelligence Ambiante  
**Filière** : M2 Réseaux & Télécommunications — Université Savoie Mont Blanc  
**Date** : Avril 2026  

---

## Table des matières

1. [Contexte et motivation](#1-contexte-et-motivation)
2. [Objectifs du projet](#2-objectifs-du-projet)
3. [Périmètre fonctionnel](#3-périmètre-fonctionnel)
4. [Contraintes techniques](#4-contraintes-techniques)
5. [Question scientifique et hypothèses](#5-question-scientifique-et-hypothèses)
6. [Architecture cible](#6-architecture-cible)
7. [Livrables attendus](#7-livrables-attendus)
8. [Critères d'acceptance](#8-critères-dacceptance)

---

## 1. Contexte et motivation

L'apiculture de précision (*Precision Apiculture*) est un domaine émergent qui vise à outiller l'apiculteur de capteurs bas-coût et de modèles prédictifs afin de réduire les interventions physiques sur la ruche. L'ouverture manuelle d'une ruche en période hivernale, par exemple, rompt brutalement l'équilibre thermodynamique de la grappe (chute de 35 °C à la température extérieure en quelques secondes), imposant à la colonie un coût énergétique élevé (métabolisation du miel stocké).

Ce projet s'inscrit dans la continuité des travaux du projet européen **BEEHAVE** et du simulateur **HONEYBEE-pDT**, et explore comment un Jumeau Numérique alimenté par des données IoT peut remplacer partiellement l'inspection visuelle tout en détectant des événements critiques tels que l'essaimage.

---

## 2. Objectifs du projet

| Priorité | Objectif |
|----------|----------|
| **O1 - Primaire** | Construire un simulateur biophysique de ruche connectée transmettant des données via MQTT à l'image d'un vrai capteur LoRaWAN. |
| **O2 - Primaire** | Persister les séries temporelles dans une base de données time-series (InfluxDB) et les visualiser en temps réel (Grafana). |
| **O3 - Primaire** | Implémenter un algorithme de détection d'essaimage par dérivée temporelle de la masse et mesurer ses performances (F1-Score). |
| **O4 - Secondaire** | Modéliser les pertes radio LoRaWAN (PDR) et évaluer leur impact sur la fiabilité de la détection. |
| **O5 - Secondaire** | Produire un jeu de données documenté et réutilisable issu de l'expérimentation. |

---

## 3. Périmètre fonctionnel

### 3.1 Inclus dans le périmètre

- Simulation du comportement thermodynamique et massique d'une ruche (bilan énergétique, cycle de butinage, essaimage).
- Transmission des données simulées via le protocole MQTT (broker Mosquitto).
- Simulation de la couche radio LoRaWAN : perte de paquets stochastique (PDR configurable), RSSI et SNR synthétiques.
- Ingestion des données dans InfluxDB et visualisation dans Grafana.
- Exportation du dataset au format CSV pour analyse.
- Détection d'essaimage par dérivée temporelle avec calcul des métriques de classification (Précision, Rappel, F1-Score).
- Documentation éthique sur les enjeux du numérique responsable et de la protection animale.
- Revue de littérature positionnant le projet dans l'état de l'art.

### 3.2 Hors périmètre

- Déploiement sur un vrai réseau LoRaWAN (The Things Network ou réseau privé).
- Capteurs physiques réels (ruche hardware).
- Modélisation acoustique (chant des reines) pour la détection d'essaimage.
- Interface utilisateur web dédiée (Grafana est suffisant).

> **Justification du choix MQTT + PDR simulé** : L'absence de matériel LoRaWAN physique est un choix délibéré qui garantit la **reproductibilité expérimentale** (toute la stack démarrant via `docker compose up -d`) et permet de faire varier le PDR de façon contrôlée pour tester H1 et H2. Cette approche est académiquement recevable et explicitement documentée dans la littérature de simulation de réseaux LPWAN (Bor et al., 2016 — LoRaSim). En production réelle, le publisher MQTT serait remplacé par un dispositif LoRa + gateway TTN, sans modification du reste de la pipeline (InfluxDB, Grafana, train_eval.py).

---

## 4. Contraintes techniques

| Contrainte | Exigence |
|------------|----------|
| **Déploiement** | Entièrement conteneurisé via Docker Compose. Aucune dépendance système hors Docker. |
| **Protocole IoT** | MQTT (QoS 0, broker Mosquitto 2.x). Le PDR LoRaWAN est simulé côté publisher. |
| **Base de données** | InfluxDB 2.7 (Time-Series). Requêtes Flux uniquement. |
| **Langage** | Python 3.x pour toute la logique applicative. |
| **Reproductibilité** | La stack doit démarrer avec `docker compose up -d` sans configuration manuelle au-delà d'un fichier `.env`. |
| **Sécurité** | Les credentials (tokens InfluxDB, mots de passe Grafana) sont externalisés dans `.env`, jamais committés. |
| **Portabilité** | La simulation doit pouvoir tourner sans accès Internet après le pull initial des images Docker. |

---

## 5. Question scientifique et hypothèses

> **Question principale** : Notre algorithme fondé sur une logique différentielle peut-il repérer de manière fiable un essaimage destructeur, et quelle est l'influence des conditions de transmission LoRaWAN sur ces performances ?

> **Question secondaire** (issue du sujet) : Les erreurs de prédiction du Jumeau Numérique augmentent-elles fortement en conditions extrêmes ? — Cette question est répondue à deux niveaux distincts : **(i)** stabilité des erreurs thermiques (modèle biophysique) et **(ii)** dégradation de la détection d'événements discrets (classification) sous contrainte réseau.

| ID | Énoncé | Critère de validation |
|----|--------|-----------------------|
| **H1** | En condition réseau nominale (PDR = 0.90), le Jumeau Numérique détecte un essaimage avec une très forte fiabilité. | Précision **≥ 0.90** (peu de fausses alertes). |
| **H2** | L'augmentation des pertes réseau (PDR = 0.65) dégrade l'interpolation temporelle et empêche le jumeau de déclencher l'alerte. | Chute significative du **Rappel** (augmentation des Faux Négatifs). |
| **H3** | La chaîne d'intégration MQTT → InfluxDB → Grafana est stable en conditions opérationnelles. | Stack opérationnelle sans interruption sur ≥ 6 h. |

---

## 6. Architecture cible

```
┌─────────────────────────────────────────────────────────────────────┐
│                         docker-compose stack                          │
│                                                                       │
│  ┌────────────────────────┐   JSON/MQTT    ┌────────────────────────┐  │
│  │ random_data_publisher.py ─────────────► │ Mosquitto :1883        │  │
│  │ (Modèle Bio + PDR LoRa)  │                │ (Broker local)         │  │
│  └────────────────────────┘                └────────┬───────────────┘  │
│                                                     │                  │
│                                                     ▼                  │
│  ┌────────────────────────┐                ┌────────────────────────┐  │
│  │ Grafana :3000          │◄───────────────│ InfluxDB 2.7 :8086     │◄─┤
│  │ (Dashboard Temps Réel) │   Flux query   │ (Time-Series DB)       │  │
│  └────────────────────────┘                └────────────────────────┘  │
│                                                     │ export CSV       │
│                                                     ▼                  │
│                                            ┌────────────────────────┐  │
│                                            │ train_eval.py          │  │
│                                            │ (Interpolation &       │  │
│                                            │  Métriques)            │  │
│                                            └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

**Flux de données** :
1. `random_data_publisher.py` génère la télémétrie biophysique et simule les pertes LoRa (PDR).
2. Mosquitto relaie les paquets survivants vers `mqtt_to_influx.py`.
3. `mqtt_to_influx.py` écrit les points dans InfluxDB.
4. Grafana interroge InfluxDB via requêtes Flux pour la visualisation temps réel.
5. `export_csv.py` exporte les données vers `data/processed/hive_timeseries.csv`.
6. `train_eval.py` charge le CSV, applique l'interpolation, calcule la dérivée et évalue les métriques.

---

## 7. Livrables attendus

| # | Livrable | Fichier(s) | Critère de complétude |
|---|----------|------------|-----------------------|
| L1 | Prototype fonctionnel (code + infra) | `model/`, `infra/`, `docker-compose.yml` | Stack démarre, données publiées et ingérées. |
| L2 | Jeu de données documenté | `data/processed/hive_timeseries.csv`, `livrables/dataset_description.md` | CSV non vide, stats section 7 remplies. |
| L3 | Analyse quantitative et résultats | `livrables/resultats.md`, `model/train_eval.py` | Tableaux de métriques remplis, H1/H2 statuées. |
| L4 | Document éthique | `docs/ethique.md` | Aborde données, bien-être animal, ACV. |
| L5 | Revue de littérature | `docs/revue_litterature.md` | ≥ 3 articles cités, positionnement justifié. |
| L6 | Protocole expérimental | `docs/protocole_experimental.md` | Variables, plan d'échantillonnage, menaces à la validité. |
| L7 | Cahier des charges | `docs/cahier_des_charges.md` | Ce document. |

---

## 8. Critères d'acceptance

| Critère | Mesure |
|---------|--------|
| La stack démarre sans erreur | `docker compose up -d` → tous les services `healthy` ou `running`. |
| Des données sont produites | InfluxDB contient ≥ 100 points de mesure sur au moins 1 heure simulée. |
| Le CSV export fonctionne | `python model/export_csv.py` génère `data/processed/hive_timeseries.csv` non vide. |
| H1 peut être évaluée | `python model/train_eval.py` s'exécute sans erreur et affiche Précision, Rappel, F1. |
| La documentation est complète | Tous les champs "À remplir" de `resultats.md` et `dataset_description.md` sont renseignés. |
