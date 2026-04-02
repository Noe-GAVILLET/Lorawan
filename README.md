# Projet ETRS012 — Jumeau Numérique Scientifique de Ruche IoT

> Cours Intelligence Ambiante — M2 Réseaux & Télécommunications  
> **Branche de travail actuelle (`lab`)** : Refonte scientifique selon l'état de l'art (BEEHAVE, apprentissage sur séries temporelles, LoRaSim).

---

## Table des matières

- [1. Vue d'ensemble du projet](#1-vue-densemble-du-projet)
- [2. Structure du dépôt](#2-structure-du-dépôt)
- [3. Documentation](#3-documentation)
- [4. Installation & Démarrage Rapide](#4-installation--démarrage-rapide)
- [5. Livrables & Avancement](#5-livrables--avancement-branche-lab)

---

## 1. Vue d'ensemble du projet

L'objectif est de créer un **Jumeau Numérique** (Digital Twin) de ruche connectée. Au lieu d'un simple capteur relayant des chiffres aléatoires, ce projet implémente un véritable comportement biophysique :

1. **Bilan Énergétique (Inspiré de BEEHAVE)** : La colonie régule son couvain à ~34.5 °C et consomme du miel la nuit pour chauffer. Le butinage augmente la masse en journée.
2. **Contrainte LoRaWAN** : Simulation du *Packet Delivery Rate* (PDR) pour mimer les pertes inhérentes aux réseaux LPWAN en forêt.
3. **Détection d'Essaimage (Time-Series AI)** : Le jumeau calcule la dérivée temporelle de la masse pour alerter l'apiculteur d'un essaimage imminent ou en cours.

> Pour le détail complet des objectifs, contraintes et critères d'acceptance, voir **[docs/cahier_des_charges.md](docs/cahier_des_charges.md)**.

---

## 2. Structure du dépôt

```
.
├── docker-compose.yml          # Orchestration des services (MQTT, InfluxDB, Grafana, Python)
├── .env.example                # Variables d'environnement à copier vers .env
│
├── docs/
│   ├── cahier_des_charges.md   # Objectifs, contraintes, hypothèses, critères d'acceptance
│   ├── protocole_experimental.md
│   ├── revue_litterature.md
│   └── ethique.md
│
├── model/
│   ├── random_data_publisher.py  # Simulateur biophysique + PDR LoRaWAN
│   ├── mqtt_to_influx.py         # Ingestion MQTT → InfluxDB
│   ├── export_csv.py             # Export InfluxDB → CSV
│   ├── train_eval.py             # Détection d'essaimage + métriques F1
│   └── metrics.py                # Fonctions MAE / RMSE
│
├── infra/
│   ├── docker/python-app.Dockerfile
│   └── mosquitto/mosquitto.conf
│
├── data/
│   └── processed/
│       └── hive_timeseries.csv   # Généré par export_csv.py
│
└── livrables/
    ├── dataset_description.md
    └── resultats.md
```

---

## 3. Documentation

| Document | Lien | Contenu |
|----------|------|---------|
| Cahier des charges | [docs/cahier_des_charges.md](docs/cahier_des_charges.md) | Objectifs, périmètre, contraintes, hypothèses, livrables, critères d'acceptance |
| Protocole expérimental | [docs/protocole_experimental.md](docs/protocole_experimental.md) | Variables, plan d'échantillonnage, pipeline de traitement, menaces à la validité |
| Revue de littérature | [docs/revue_litterature.md](docs/revue_litterature.md) | BEEHAVE, détection d'anomalie sur séries temporelles, simulation LoRaWAN |
| Éthique & numérique responsable | [docs/ethique.md](docs/ethique.md) | Bien-être animal, ACV, gouvernance des données agricoles |
| Description du dataset | [livrables/dataset_description.md](livrables/dataset_description.md) | Schéma CSV, règles qualité, statistiques |
| Résultats & métriques | [livrables/resultats.md](livrables/resultats.md) | Tableaux MAE/RMSE/F1, validation H1/H2, analyse critique |

---

## 4. Installation & Démarrage Rapide

### Étape 1 : Préparer l'environnement
Copiez simplement le fichier environnement :
```bash
cp .env.example .env
```
*(Éditez éventuellement `.env` si vous souhaitez changer les mots de passe de Grafana/Influx)*

### Étape 2 : Lancer le Simulateur et la DB
```bash
docker compose up -d
```
Attendez 1 minute pour vérifier sur Grafana (localhost:3000) que la ruche suit son rythme *Nominal* biophysique (jour, nuit, perte et apport modéré de masse).

### Étape 3 : Déclencher un Essaimage (Mode Extrême)
Pour valider le jumeau, on force un départ massif des abeilles via la variable d'environnement :
```bash
docker compose stop publisher
SCENARIO=extreme docker compose up -d publisher
```
*(Vous verrez une brutale descente de la masse dans InfluxDB / Grafana).*

### Étape 4 : Détection via le Jumeau
Exportez la bdd depuis InfluxDB vers CSV (via `model/export_csv.py`, ou l'UI), puis lancez :
```bash
python model/train_eval.py
```
Le script sortira les Vrais Positifs, Faux Positifs, la **Précision**, le **Rappel** et le **F1-Score**.

---

## 5. Livrables & Avancement (Branche lab)

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Cahier des charges | [docs/cahier_des_charges.md](docs/cahier_des_charges.md) | ✅ Créé |
| Modèle Biologique & LPWAN | `model/random_data_publisher.py` | ✅ Remanié (Precision Apiculture) |
| Algorithme AI d'Essaimage | `model/train_eval.py` | ✅ Remanié (Dérivée & Interpolation) |
| Protocole expérimental | [docs/protocole_experimental.md](docs/protocole_experimental.md) | ✅ Mis à jour (Hypothèses IA) |
| Document éthique | [docs/ethique.md](docs/ethique.md) | ✅ Mis à jour (Respect animal) |
| Revue de Littérature | [docs/revue_litterature.md](docs/revue_litterature.md) | ✅ Publiée (3 concepts fusionnés) |
| Description du dataset | [livrables/dataset_description.md](livrables/dataset_description.md) | ⚠️ Stats section 7 à remplir |
| Résultats & métriques | [livrables/resultats.md](livrables/resultats.md) | ⚠️ Tableaux à remplir après expérimentation |
| Dashboard & Dataset finaux | `Grafana` | ✅ Opérationnel (détecteur d'essaimage Flux intégré) |

---
*Ce projet démontre l'intégration bout-en-bout d'une philosophie IoT, de la modélisation embarquée (Edge) à l'analyse analytique prédictive globale (Jumeau Numérique) par Intelligence Artificielle.*
