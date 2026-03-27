# Projet ETRS012 — Jumeau Numérique de Ruche IoT (Mode Simulation MQTT)

> Cours Intelligence Ambiante — M2 Réseaux & Télécommunications  
> Contrainte : **20 heures** de travail effectif — MVP reproductible

---

## Table des matières

1. [Vision du projet](#1-vision-du-projet)
2. [Question scientifique & Hypothèses](#2-question-scientifique)
3. [Périmètre MVP](#3-périmètre-mvp)
4. [Cahier des charges](#4-cahier-des-charges)
5. [Architecture & Schéma logique](#5-architecture--schéma-logique)
6. [Technologies retenues](#6-technologies-retenues)
7. [Structure du projet](#7-structure-du-projet)
8. [Installation & Démarrage rapide](#8-installation--démarrage-rapide)
9. [Plan de mise en place (20h)](#9-plan-de-mise-en-place-20h)
10. [Livrables attendus](#10-livrables-attendus)

---

## 1) Vision du projet

Ce projet construit un **MVP** (Minimum Viable Prototype) de jumeau numérique pour une ruche connectée.  
L'objectif est de **comparer un état simulé** (capteurs virtuels) et un **état prédit** (modèle de persistance), puis de **quantifier l'erreur** selon le régime de fonctionnement (nominal vs extrême).

Le projet répond à la contrainte d'Intelligence Ambiante en dépassant une vision purement technique : il intègre dès la conception des dimensions éthiques (souveraineté des données, impact environnemental) et une démarche scientifique structurée (hypothèses, protocole, métriques verrouillées *a priori*).

**Note sur LoRaWAN** : faute de matériel physique disponible, la chaîne LoRaWAN est simulée par un publisher MQTT Python. L'architecture est conçue pour être branchée sur un vrai réseau LoRaWAN (TTN / ChirpStack) en remplaçant uniquement le publisher — le reste de la stack est identique.

---

## 2) Question scientifique

> Dans quelle mesure un jumeau numérique basé sur des données capteurs peut-il prédire l'évolution d'une ruche réelle à court terme ?  
> Est-ce que les erreurs augmentent fortement en conditions extrêmes ?

### 2.1) Hypothèses de recherche

| ID | Énoncé | Critère de validation | Seuil verrouillé |
|----|--------|-----------------------|------------------|
| **H1** | En conditions nominales, le modèle de persistance fournit une erreur acceptable | MAE ≤ 1.0 °C **ET** RMSE ≤ 1.3 °C sur le segment nominal du jeu de test | Verrouillé avant collecte |
| **H2** | En conditions extrêmes, l'erreur augmente significativement | MAE_extrême > MAE_nominale | Verrouillé avant collecte |
| **H3** | La chaîne complète simulateur → MQTT → InfluxDB → Grafana est exploitable en quasi temps-réel | Flux sans perte bloquante sur la fenêtre de test, Grafana mis à jour en quelques secondes | Verrouillé avant collecte |

**Définition opérationnelle des régimes** (cf. `docs/protocole_experimental.md`) :
- **Nominal** : |Δtempérature entre deux mesures consécutives| ≤ 1.5 °C **ET** |Δmasse| ≤ 0.20 kg
- **Extrême** : |Δtempérature| > 1.5 °C **OU** |Δmasse| > 0.20 kg

### 2.2) Démarche de recherche

Démarche inspirée de la recherche appliquée :
1. Formuler les hypothèses et verrouiller les critères de succès **avant** la collecte.
2. Définir un protocole de mesure reproductible (variables, fréquence, durée).
3. Collecter et qualifier les données (doublons, outliers, gaps > 20 min exclus).
4. Évaluer une **baseline explicable** — modèle de persistance `temp(t) = temp(t-1)`.
5. Comparer conditions nominales vs extrêmes sur les métriques verrouillées.
6. Discuter validité, limites et biais (cf. `docs/protocole_experimental.md` §9).

Détail complet du protocole → [`docs/protocole_experimental.md`](docs/protocole_experimental.md)

---

## 3) Périmètre MVP

### Dans le périmètre ✅

| Composant | Description |
|-----------|-------------|
| Simulateur capteurs | Publisher Python MQTT — marche aléatoire + mode extrême injectable (`SCENARIO=extreme`) |
| Broker MQTT | Eclipse Mosquitto 2 — transport des télémesures JSON |
| Ingestion | Script Python MQTT → InfluxDB |
| Stockage | InfluxDB 2.7 — base de données temporelle |
| Visualisation | Dashboard Grafana (température, masse, écart prédit/réel) |
| Modèle baseline | Persistance : `temp_pred(t) = temp_real(t-1)` |
| Évaluation | MAE et RMSE segmentés nominal / extrême + validation H1/H2 |
| Export données | Script Python InfluxDB → CSV |
| Documentation | Protocole, éthique, revue de littérature, description dataset, résultats |

### Hors périmètre MVP ❌

- Vrai capteur matériel / gateway LoRaWAN physique (dette matérielle documentée)
- Modèle ML avancé (LSTM, XGBoost, ARIMA...)
- Alertes automatisées Grafana
- Authentification MQTT / TLS (dette sécurité documentée — `allow_anonymous true` acceptable en local uniquement)
- Interface utilisateur dédiée pour les apiculteurs

---

## 4) Cahier des charges

### 4.1 Exigences fonctionnelles

- Le système reçoit des messages MQTT au format JSON sur le topic `hive/<device_id>/telemetry`.
- Le système persiste les mesures `timestamp`, `temperature_real`, `masse_real` dans InfluxDB.
- Le système affiche un dashboard Grafana (température + masse + écart prédit/réel).
- Le système produit une prédiction court terme par persistance et calcule MAE / RMSE.
- Les métriques sont segmentées sur les régimes nominal et extrême.
- Le système exporte les données InfluxDB vers CSV pour l'analyse hors ligne.
- La synthèse des résultats est produite dans `livrables/resultats.md`.

### 4.2 Exigences techniques

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Langage principal | Python | 3.11 |
| Orchestration | Docker Compose | v2 |
| Broker MQTT | Eclipse Mosquitto | 2 |
| Time-series DB | InfluxDB | 2.7 |
| Visualisation | Grafana | 11.1.0 |
| Client MQTT Python | paho-mqtt | 1.6.1 |
| Client InfluxDB Python | influxdb-client | 1.46.0 |
| Traitement données | pandas / numpy | 2.2.2 / 2.1.1 |

Toutes les dépendances sont déclarées dans `model/requirements.txt` et les services dans `docker-compose.yml`.

### 4.3 Exigences qualité

- **Reproductibilité** : relancer l'évaluation complète avec `docker compose up` + `python model/train_eval.py`.
- **Traçabilité** : hypothèses, seuils et décisions de nettoyage documentés *avant* la collecte.
- **Lisibilité** : structure de fichiers claire, documents courts mais rigoureux.
- **Honnêteté scientifique** : les seuils H1/H2 sont verrouillés *a priori* — aucune modification après observation des résultats.

### 4.4 Exigences éthiques

- Minimisation des données : seules température et masse sont collectées, sans géolocalisation.
- Documentation de la finalité dans `docs/ethique.md`.
- Dette sécurité documentée : MQTT `allow_anonymous true` — acceptable en local, **interdit en production**.
- Impact environnemental : usage de LoRaWAN (faible consommation) justifié dans la revue de littérature.

Réflexion complète → [`docs/ethique.md`](docs/ethique.md)

---

## 5) Architecture & Schéma logique

```
┌─────────────────────────────────────────────────────────────────────┐
│                         docker-compose stack                          │
│                                                                       │
│  ┌─────────────────┐   JSON/MQTT    ┌─────────────────────────────┐  │
│  │  publisher.py   │ ─────────────► │  Mosquitto :1883            │  │
│  │  SCENARIO=      │                │  (MQTT broker)              │  │
│  │  normal|extreme │                └─────────────┬───────────────┘  │
│  └─────────────────┘                              │ subscribe         │
│                                                   ▼                   │
│                                    ┌─────────────────────────────┐   │
│                                    │  mqtt_to_influx.py          │   │
│                                    │  (ingestion bridge)         │   │
│                                    └─────────────┬───────────────┘   │
│                                                   │ write API         │
│                                                   ▼                   │
│                                    ┌─────────────────────────────┐   │
│             Flux query             │  InfluxDB 2.7 :8086          │   │
│         ┌─────────────────────────►│  bucket: hive               │   │
│         │                          └─────────────────────────────┘   │
│         │                                                              │
│  ┌──────┴──────────┐              ┌─────────────────────────────┐    │
│  │  Grafana :3000  │              │  export_csv.py              │    │
│  │  (dashboard)    │              │  → data/processed/*.csv     │    │
│  └─────────────────┘              └─────────────┬───────────────┘    │
└──────────────────────────────────────────────────┼────────────────────┘
                                                   │ pandas
                                                   ▼
                                    ┌─────────────────────────────┐
                                    │  train_eval.py              │
                                    │  baseline persistance       │
                                    │  MAE / RMSE                 │
                                    │  segmentation nom/extrême   │
                                    └─────────────┬───────────────┘
                                                   │
                                                   ▼
                                      livrables/resultats.md
```

**Format du message MQTT** (topic `hive/<device_id>/telemetry`) :
```json
{
  "timestamp": "2026-03-27T14:00:00Z",
  "temperature": 34.52,
  "mass": 42.07
}
```

---

## 6) Technologies retenues

| Technologie | Rôle | Justification |
|-------------|------|---------------|
| **Python 3.11** | Simulation, ingestion, évaluation | Écosystème data science complet, rapide à prototyper |
| **Eclipse Mosquitto 2** | Broker MQTT | Standard de référence, image Docker officielle légère |
| **MQTT (paho)** | Transport télémesures | Simule le comportement LoRaWAN (faible débit, JSON) |
| **InfluxDB 2.7** | Stockage séries temporelles | Optimisé time-series, API Flux puissante, UI intégrée |
| **Grafana 11.1.0** | Visualisation temps réel | Connecteur InfluxDB natif, dashboards configurables |
| **Docker Compose** | Orchestration locale | Reproductibilité garantie, zéro installation manuelle |
| **pandas / numpy** | Analyse & métriques | Standard scientifique Python |

---

## 7) Structure du projet

```
Lorawan/
├── docker-compose.yml              # Stack complète (5 services)
├── .env.example                    # Variables d'environnement (copier → .env)
├── README.md                       # Ce fichier — plan & documentation centrale
│
├── data/
│   └── processed/
│       └── hive_timeseries.csv     # Dataset exporté depuis InfluxDB (généré)
│
├── docs/
│   ├── protocole_experimental.md   # Hypothèses, seuils, plan d'échantillonnage
│   ├── revue_litterature.md        # 4 références justifiant les choix
│   └── ethique.md                  # Réflexion numérique responsable
│
├── infra/
│   ├── docker/
│   │   └── python-app.Dockerfile   # Image Python pour publisher + ingestion
│   └── mosquitto/
│       └── mosquitto.conf          # Configuration broker MQTT
│
├── livrables/
│   ├── dataset_description.md      # Documentation du jeu de données
│   └── resultats.md                # Résultats + validation des hypothèses (à compléter)
│
└── model/
    ├── requirements.txt            # Dépendances Python
    ├── metrics.py                  # Fonctions MAE et RMSE
    ├── random_data_publisher.py    # Simulateur capteurs (SCENARIO=normal|extreme)
    ├── mqtt_to_influx.py           # Bridge MQTT → InfluxDB
    ├── export_csv.py               # Export InfluxDB → CSV
    └── train_eval.py               # Évaluation baseline, segmentation, H1/H2
```

---

## 8) Installation & Démarrage rapide

### Prérequis

- Docker + Docker Compose v2
- Python 3.11 (pour les scripts d'analyse en local, optionnel)

### Étape 1 — Configurer l'environnement

```bash
cp .env.example .env
# Éditer .env : changer les mots de passe et le token InfluxDB
```

### Étape 2 — Démarrer la stack

```bash
docker compose up -d
docker compose ps   # vérifier que les 5 services sont "running"
```

### Étape 3 — Vérifier la réception de données

```bash
docker compose logs -f ingestion
# Doit afficher : Written device=ruche-01 temp=34.xx mass=42.xx
```

### Étape 4 — Accéder au dashboard Grafana

Ouvrir [http://localhost:3000](http://localhost:3000) — login `admin` / valeur de `GRAFANA_ADMIN_PASSWORD`.

Configurer la datasource InfluxDB :
- URL : `http://influxdb:8086`
- Organisation, bucket et token depuis `.env`
- Langage de requête : **Flux**

### Étape 5 — Générer des conditions extrêmes (pour H2)

```bash
# Relancer le publisher en mode extrême
docker compose stop publisher
SCENARIO=extreme docker compose up -d publisher
```

### Étape 6 — Exporter les données et évaluer

```bash
# Après au moins quelques heures de collecte
export INFLUX_TOKEN=<valeur depuis .env>
export INFLUX_ORG=<valeur depuis .env>
python model/export_csv.py

# Lancer l'évaluation (segmentation nominal/extrême + validation H1/H2)
python model/train_eval.py
```

---

## 9) Plan de mise en place (20h)

> Suivi d'avancement — mettre à jour les statuts au fur et à mesure.

### Phase 1 — Infrastructure & Validation de la chaîne (~4h) — ✅ Quasi-terminée

| # | Tâche | Durée | Statut |
|---|-------|-------|--------|
| 1.1 | `docker-compose.yml` (5 services : Mosquitto, InfluxDB, Grafana, publisher, ingestion) | 1h | ✅ |
| 1.2 | `random_data_publisher.py` (marche aléatoire température + masse) | 0.5h | ✅ |
| 1.3 | `mqtt_to_influx.py` (bridge MQTT → InfluxDB avec retry) | 1h | ✅ |
| 1.4 | `metrics.py` (MAE, RMSE) + `train_eval.py` initial | 0.5h | ✅ |
| 1.5 | `protocole_experimental.md`, `revue_litterature.md`, `ethique.md` | 1h | ✅ |
| **1.6** | **Créer `.env` depuis `.env.example`, tester `docker compose up` de bout en bout** | **0.5h** | **⬜ PRIORITAIRE** |

> ⚠️ **Point bloquant** : sans `.env`, `docker compose up` échoue sur les variables d'environnement InfluxDB. C'est la **première action à faire**.

---

### Phase 2 — Collecte & Qualité des données (~4h) — ⬜ À faire

| # | Tâche | Durée | Statut |
|---|-------|-------|--------|
| 2.1 | Lancer la stack **mode normal** et collecter ≥ 48h équivalent (voir astuce ci-dessous) | 1h | ⬜ |
| 2.2 | Ajouter `SCENARIO=extreme` dans `random_data_publisher.py` (injection de spikes) | 0.5h | ✅ |
| 2.3 | Relancer en mode **extrême** pour alimenter le segment H2 (≥ 20% de points extrêmes) | 0.5h | ⬜ |
| 2.4 | `model/export_csv.py` : export InfluxDB → `data/processed/hive_timeseries.csv` | 0.5h | ✅ |
| 2.5 | Vérifier qualité CSV : doublons, gaps, bornes physiques, journal de nettoyage | 0.5h | ⬜ |
| 2.6 | Compléter `livrables/dataset_description.md` §7 avec les statistiques réelles | 0.5h | ⬜ |
| 2.7 | Compléter `docs/protocole_experimental.md` §9 (menaces à la validité) | 0.5h | ⬜ |

> 💡 **Astuce accélération** : utiliser `PUBLISH_INTERVAL_SECONDS=1` pour générer ~290 points en 5 minutes (équivalent 48h à 10 min/mesure). Retravailler les timestamps avec un script si besoin.

---

### Phase 3 — Modélisation & Évaluation (~3h) — ⬜ À faire

| # | Tâche | Durée | Statut |
|---|-------|-------|--------|
| 3.1 | Enrichir `train_eval.py` : segmentation nominal/extrême, métriques par segment, validation H1/H2 | 1h | ✅ |
| 3.2 | Lancer l'évaluation sur le CSV complet, noter les sorties console | 0.3h | ⬜ |
| 3.3 | Remplir les tableaux de `livrables/resultats.md` (métriques, statut H1/H2/H3) | 0.5h | ⬜ |
| 3.4 | Rédiger l'analyse critique §5 de `resultats.md` : attendu vs observé, limites | 1h | ⬜ |
| 3.5 | Vérifier la cohérence avec les seuils verrouillés dans le protocole | 0.2h | ⬜ |

---

### Phase 4 — Dashboard Grafana (~2h) — ⬜ À faire

| # | Tâche | Durée | Statut |
|---|-------|-------|--------|
| 4.1 | Configurer la datasource InfluxDB dans Grafana | 0.2h | ⬜ |
| 4.2 | Panel **température_real** (time series, requête Flux) | 0.3h | ⬜ |
| 4.3 | Panel **masse_real** (time series) | 0.2h | ⬜ |
| 4.4 | Panel **écart** `\|temp_real - temp_pred\|` (temp_pred = valeur précédente via `timeShift`) | 0.8h | ⬜ |
| 4.5 | Exporter le dashboard JSON → `infra/grafana/dashboard.json` (reproductibilité) | 0.2h | ⬜ |
| 4.6 | Captures d'écran pour `livrables/resultats.md` §6 | 0.3h | ⬜ |

---

### Phase 5 — Documentation finale & Revue (~4h) — 🔄 Partiellement réalisée

| # | Tâche | Durée | Statut |
|---|-------|-------|--------|
| 5.1 | Finaliser `docs/ethique.md` (ajouter dette MQTT anonyme, ACV matérielle) | 0.3h | 🔄 |
| 5.2 | Relire `docs/revue_litterature.md` — cohérence avec résultats obtenus | 0.2h | ✅ |
| 5.3 | Relecture globale : sujet → hypothèses → protocole → résultats → cohérence | 1h | ⬜ |
| 5.4 | Mettre à jour les statuts du plan dans ce README | 0.3h | ⬜ |
| 5.5 | Préparer la démonstration live (`docker compose up` + logs + Grafana + `train_eval.py`) | 1h | ⬜ |
| 5.6 | Vérifier que le dépôt est propre (pas de `.env`, pas de tokens en clair dans le code) | 0.2h | ⬜ |

---

### Bilan budgétaire

| Phase | Budget | Réalisé | Restant estimé |
|-------|--------|---------|----------------|
| Phase 1 — Infrastructure | 4h | ~3.5h | ~0.5h |
| Phase 2 — Données | 4h | ~1h | ~3h |
| Phase 3 — Modélisation | 3h | ~1h | ~2h |
| Phase 4 — Grafana | 2h | 0h | ~2h |
| Phase 5 — Documentation | 4h | ~2h | ~2h |
| **Total** | **17h** | **~7.5h** | **~9.5h** |

> Le budget disponible est confortable. Privilégier la qualité de l'analyse critique (§5 de `resultats.md`) — c'est ce que les correcteurs valorisent le plus en M2.

---

### Chemin critique (ordre à respecter)

```
1.6 (créer .env + tester stack)
  └─► 2.1 (lancer collecte normale)
        └─► 2.3 (collecte extrême)
              └─► 2.4 (export CSV)
                    ├─► 3.2-3.5 (évaluation + résultats)
                    └─► 4.1-4.6 (Grafana) ─► 4.6 (captures)
                                              └─► 5.x (revue finale)
```

---

## 10) Livrables attendus

Correspondance avec les exigences du sujet (`Subject.txt`) :

| Livrable | Fichier(s) dans le dépôt | Statut |
|----------|--------------------------|--------|
| ✅ Prototype fonctionnel (chaîne MQTT → InfluxDB → Grafana) | `docker-compose.yml`, `model/` | ✅ Implémenté — ⬜ à valider live |
| ✅ Jeu de données exploitable et documenté | `data/processed/hive_timeseries.csv`, `livrables/dataset_description.md` | ⬜ À générer |
| ✅ Analyse quantitative (métriques, test des hypothèses) | `livrables/resultats.md`, `model/train_eval.py` | ⬜ À remplir |
| ✅ Document éthique argumenté | `docs/ethique.md` | ✅ Rédigé |
| ✅ Revue de littérature (3–5 articles) | `docs/revue_litterature.md` | ✅ 4 articles |
| ✅ Protocole expérimental reproductible | `docs/protocole_experimental.md` | ✅ Rédigé |
