# Projet ETRS012 — Jumeau Numérique Scientifique de Ruche IoT

> Cours Intelligence Ambiante — M2 Réseaux & Télécommunications  
> **Branche de travail actuelle (`lab`)** : Refonte scientifique selon l'état de l'art (BEEHAVE, apprentissage sur séries temporelles, LoRaSim).

---

## 1. Vision du projet (Precision Apiculture)

L'objectif est de créer un **Jumeau Numérique** (Digital Twin) de ruche connectée. Au lieu d'un simple capteur relayant des chiffres aléatoires, ce projet implémente un véritable comportement biophysique :
1. **Bilan Énergétique (Inspiré de BEEHAVE)** : La colonie régule son couvain à ~34.5°C et consomme du miel la nuit pour chauffer. Le butinage augmente la masse en journée.
2. **Contrainte LoRaWAN** : Simulation du *Packet Delivery Rate* (PDR) pour mimer les pertes inhérentes aux réseaux LPWAN en forêt.
3. **Détection d'Essaimage (Time-Series AI)** : Le jumeau ne fait pas qu'afficher des données ; il calcule la dérivée temporelle de la masse pour alerter l'apiculteur d'un essaimage imminent ou en cours.

---

## 2. Question scientifique et Hypothèses

> Notre algorithme fondé sur une logique différentielle peut-il repérer de manière fiable un essaimage destructeur, et quelle est l'influence des conditions de transmission LoRaWAN sur ces performances ?

| ID | Énoncé | Critère de validation |
|----|--------|-----------------------|
| **H1** | En condition réseau nominale (LoRaWAN PDR=0.90), le jumeau détecte un essaimage avec une très forte fiabilité. | **Précision >= 0.90** sur l'alerte d'essaimage (F1-score). |
| **H2** | L'augmentation des erreurs de transmission réseau (PDR=0.65) "casse" l'interpolation temporelle et empêche le jumeau de déclencher l'alerte. | **Chute du Rappel** avec l'augmentation des gaps de données (Faux Négatifs). |

---

## 3. Architecture & Technologies

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
│                                            │ (Interpolation & AI)   │  │
│                                            └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

- **Moteur MQTT/Python** : Simulation biologique temps-réel incluant capteurs météo et matériel (Humidité ambiante, Batterie, LoRaWAN SNR/RSSI).
- **Persistance d'État (DB)** : Le simulateur Python (publisher) interroge `InfluxDB` à son lancement via `get_last_state()` pour reprendre l'historique là où il s'est arrêté (évite les pics de graphiques).
- **Time-Series Interpolation** : Le fichier d'évaluation IA recolle les morceaux perdus par le réseau MQTT via interpolation linéaire avant de dériver la masse.

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
| Modèle Biologique & LPWAN | `model/random_data_publisher.py` | ✅ Remanié (Precision Apiculture) |
| Algorithme AI d'Essaimage | `model/train_eval.py` | ✅ Remanié (Dérivée & Interpolation) |
| Protocole expérimental | `docs/protocole_experimental.md` | ✅ Mis à jour (Hypothèses IA) |
| Document éthique | `docs/ethique.md` | ✅ Mis à jour (Respect animal) |
| Revue de Littérature | `docs/revue_litterature.md` | ✅ Publiée (3 concepts fusionnés) |
| Dashboard & Dataset finaux | `Grafana` | ✅ Opérationnel (Suivi complet avec détecteur d'essaimage Flux intégré) |

---
*Ce projet démontre l'intégration bout-en-bout d'une philosophie IoT, de la modélisation embarquée (Edge) à l'analyse analytique prédictive globale (Jumeau Numérique) par Intelligence Artificielle.*
