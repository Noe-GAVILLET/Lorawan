# Projet ETRS012 - Jumeau Numerique de Ruche IoT (Mode Simulation MQTT)

## 1) Vision du projet

Ce projet vise a construire un **MVP** (Minimum Viable Prototype) de jumeau numerique pour une ruche connectee.
L'idee est de comparer un etat **mesure** (capteurs) et un etat **preduit** (modele simple), puis de quantifier l'erreur.

Architecture cible retenue: **App de simulation -> MQTT -> Base de donnees temporelle -> Grafana -> Modele**.

Contrainte principale: projet de cours avec **20 heures** de travail effectif.

## 2) Question scientifique

Dans quelle mesure un jumeau numerique base sur des donnees capteurs peut-il predire l'evolution d'une ruche reelle a court terme ?

Hypothese de travail:
- Un modele simple base sur l'historique recent peut fournir une prediction utile a court terme.
- Les erreurs augmentent en conditions atypiques (variation rapide de temperature, variation brusque de masse).

## 2.1) Hypotheses de recherche explicites

- **H1 (prediction court terme)**: sur des conditions nominales, une baseline temporelle doit rester sous un seuil d'erreur defini en amont.
    - Cible initiale: MAE temperature <= 1.0 C.
- **H2 (degradation en conditions extremes)**: l'erreur augmente de facon significative lors de variations rapides (meteo, activite intense, rupture de mesure).
    - Cible initiale: MAE extreme > MAE nominale.
- **H3 (valeur operationnelle)**: la chaine simulation -> MQTT -> InfluxDB -> Grafana permet une supervision exploitable en quasi temps reel.
    - Cible initiale: latence de visualisation compatible demo (ordre de quelques secondes).

## 2.2) Demarche de recherche

Demarche inspiree de la recherche appliquee:
1. Formuler les hypotheses et les criteres de succes.
2. Definir un protocole de mesure reproductible (variables, frequence, duree).
3. Collecter et qualifier les donnees (qualite, manquants, valeurs aberrantes).
4. Evaluer une baseline explicable (pas de modele opaque dans le MVP).
5. Comparer conditions nominales vs extremes.
6. Discuter validite, limites et biais.

Le detail du protocole est dans `docs/protocole_experimental.md`.

## 2.3) Decisions scientifiques verrouillees (MVP)

- Frequence de mesure: 1 point / 10 minutes.
- Duree cible de collecte: 48h, minimum acceptable: 12h.
- Definition nominale:
    - |delta temperature| <= 1.5 C sur 30 minutes.
    - |delta masse| <= 0.20 kg sur 30 minutes.
- Definition extreme:
    - |delta temperature| > 1.5 C sur 30 minutes, ou
    - |delta masse| > 0.20 kg sur 30 minutes.
- Criteres d'acceptation H1:
    - MAE nominale temperature <= 1.0 C
    - RMSE nominale temperature <= 1.3 C

## 2.4) Contrat de donnees (mapping MQTT -> Dataset)

| Source MQTT | Champ dataset exporte | Unite | Obligatoire |
|---|---|---|---|
| `timestamp` | `timestamp` | ISO-8601 UTC | recommande |
| `temperature` | `temperature_real` | C | oui |
| `mass` | `masse_real` | kg | oui |

Regle si `timestamp` absent: utiliser l'heure de reception UTC cote ingestion.

## 3) Perimetre MVP

### Inclus
- Acquisition de donnees temperature + masse (ou donnees simulees si capteur indisponible).
- Ingestion des mesures via MQTT vers une base de donnees temporelle.
- Visualisation des mesures dans Grafana.
- Export de donnees vers CSV pour l'analyse modele.
- Pipeline de base: nettoyage simple, prediction baseline, calcul MAE/RMSE.
- Documentation scientifique et ethique concise.
- Presentation des resultats et limites.

### Exclu (hors MVP)
- Modeles IA complexes (LSTM, Transformers, etc.).
- Infrastructure cloud lourde en production.
- Interface web complete sur mesure.
- Deploiement terrain longue duree.

## 4) Cahier des charges

### 4.1 Exigences fonctionnelles
- Le systeme doit stocker des mesures temporelles: `timestamp`, `temperature_real`, `masse_real`.
- Le systeme doit recevoir des messages via MQTT (topics mesures ruche).
- Le systeme doit persister les mesures dans une base de donnees temporelle.
- Le systeme doit afficher au moins un dashboard Grafana (temperature, masse).
- Le systeme doit produire une prediction court terme pour la temperature (et ensuite la masse si temps disponible).
- Le systeme doit calculer au minimum MAE et RMSE.
- Le systeme doit fournir une synthese interpretable des ecarts reel vs predit.

### 4.2 Exigences techniques
- Source de donnees retenue: application Python de simulation aleatoire.
- Transport des donnees: MQTT.
- Stockage principal: base de donnees temporelle (InfluxDB recommande).
- Visualisation: Grafana.
- Format d'export pour analyse: CSV.
- Traitement et evaluation: Python.
- Code de metriques separable/reutilisable.
- Arborescence simple et lisible pour evaluation academique.

### 4.3 Exigences qualite
- Reproductibilite: un lecteur doit pouvoir relancer l'evaluation rapidement.
- Tracabilite: les hypotheses et choix doivent etre documentes.
- Lisibilite: structure claire et documents courts mais rigoureux.

### 4.4 Exigences ethiques
- Minimisation des donnees collectees.
- Documentation de la finalite des donnees.
- Vigilance securite/acces aux donnees.
- Prise en compte de l'impact environnemental de la solution.

## 5) Schema logique du fonctionnement

```text
[Application simulatrice]
    | publication MQTT
    v
[Broker MQTT]
    | abonnement ingestion
    v
[Base temporelle (InfluxDB)]
    | requetes
    +--> [Grafana: dashboard temperature + masse]
    |
    +--> [Export CSV -> data/processed/hive_timeseries.csv]
                |
                v
[Modele baseline - model/train_eval.py]
    | prediction T(t+1), calcul MAE/RMSE
    v
[Analyse - livrables/resultats.md]
    |
    v
[Conclusion: validite, limites, pistes]
```

## 6) Technologies retenues

- **Python simulation app**: generation de telemetry aleatoire temperature/masse.
- **Broker MQTT**: transport des mesures (Mosquitto ou broker local).
- **InfluxDB**: stockage series temporelles.
- **Grafana**: visualisation des mesures en quasi temps reel.
- **Python 3.10+**: langage principal pour traitement et modelisation rapide.
- **paho-mqtt**: client MQTT Python pour ingestion/bridge si necessaire.
- **influxdb-client**: ecriture/lecture InfluxDB depuis Python.
- **Pandas / NumPy**: manipulation des series temporelles et calcul numerique.
- **CSV**: format d'export simple pour l'evaluation du modele.
- **Docker Compose**: orchestration portable des services (simulateur, MQTT, InfluxDB, Grafana, ingestion).

## 7) Plan de mise en place (20h)

| Bloc | Objectif | Duree cible |
|---|---|---:|
| 1. Cadrage + protocole | Hypothese, variables, protocole de collecte | 2h |
| 2. App simulation vers MQTT | Publication des mesures et test topics | 4h |
| 3. MQTT vers base de donnees | Ecriture InfluxDB + verification | 4h |
| 4. Dashboard Grafana | Panels temperature/masse + verification | 3h |
| 5. Modele baseline | Export CSV, prediction naive, MAE/RMSE | 4h |
| 6. Analyse + dossier final | Resultats, ethique, revue, mise en forme | 3h |
| **Total** |  | **20h** |

### Points de controle scientifiques (jalons)

- **J1 (fin bloc 1)**: hypotheses valides, variables et seuils fixes.
- **J2 (fin bloc 3)**: flux de donnees stable, qualite minimale verifiee.
- **J3 (fin bloc 5)**: metriques calculees pour nominal/extreme.
- **J4 (fin bloc 6)**: interpretation critique + limites + perspectives.

## 8) Arborescence du projet

```text
Lorawan/
|- README.md
|- data/
|  |- raw/
|  \- processed/
|     \- hive_timeseries.csv
|- model/
|  |- train_eval.py
|  |- random_data_publisher.py
|  |- mqtt_to_influx.py
|  \- metrics.py
|- dashboard/
|  \- grafana/
|- docs/
|  |- protocole_experimental.md
|  |- ethique.md
|  \- revue_litterature.md
\- livrables/
	|- dataset_description.md
	\- resultats.md
```

## 9) Description des dossiers

- `data/raw/`: donnees brutes non modifiees.
- `data/processed/`: exports nettoyes prets pour analyse modele.
- `model/`: scripts de simulation, ingestion, prediction et metriques.
- `dashboard/grafana/`: dashboard principal du MVP (obligatoire dans cette version).
- `docs/`: documents methodologiques et ethiques.
- `livrables/`: resultats finaux a rendre.

## 10) Etat actuel du code

- `model/metrics.py`: fonctions `mae` et `rmse`.
- `model/train_eval.py`: baseline de prediction par decalage temporel.
- `model/random_data_publisher.py`: generation de donnees aleatoires vers MQTT.
- `model/mqtt_to_influx.py`: ingestion MQTT vers InfluxDB.
- `data/processed/hive_timeseries.csv`: echantillon de donnees de depart.

## 11) Comment executer localement

### Mode recommande: Docker Compose (portable)

1. Copier le fichier d'environnement:

```bash
copy .env.example .env
```

2. Lancer toute la stack:

```bash
docker compose up --build -d
```

3. Verifier les services:

```bash
docker compose ps
docker compose logs -f publisher ingestion
```

4. Acces interfaces:

- Grafana: http://localhost:3000
- InfluxDB: http://localhost:8086
- MQTT broker: localhost:1883

5. Arreter la stack:

```bash
docker compose down
```

6. Arreter et supprimer les volumes (reset complet):

```bash
docker compose down -v
```

### Prerequis
- Python 3.10+
- Docker Desktop (ou moteur Docker compatible Compose)

### Installation minimale
```bash
pip install pandas numpy paho-mqtt influxdb-client
```

### Variables d'environnement (ingestion MQTT -> InfluxDB)

```bash
# MQTT
set MQTT_HOST=localhost
set MQTT_PORT=1883
set MQTT_TOPIC=hive/+/telemetry
set MQTT_USERNAME=
set MQTT_PASSWORD=

# InfluxDB
set INFLUX_URL=http://localhost:8086
set INFLUX_TOKEN=your_token
set INFLUX_ORG=your_org
set INFLUX_BUCKET=hive
set INFLUX_MEASUREMENT=hive_telemetry
```

### Lancer l'ingestion MQTT vers InfluxDB
```bash
python model/mqtt_to_influx.py
```

### Lancer le generateur de donnees aleatoires
```bash
python model/random_data_publisher.py
```

### Lancer l'evaluation
```bash
python model/train_eval.py
```

### Fichiers Docker

- `docker-compose.yml`: orchestration complete de la stack.
- `infra/docker/python-app.Dockerfile`: image Python pour simulateur et ingestion.
- `infra/mosquitto/mosquitto.conf`: configuration du broker MQTT local.
- `.env.example`: variables a copier dans `.env`.

## 12) Convention MQTT recommandee

### Topic

```text
hive/<device_id>/telemetry
```

Exemple:

```text
hive/ruche-01/telemetry
```

### Payload JSON

```json
{
    "timestamp": "2026-03-26T08:10:00Z",
    "temperature": 34.6,
    "mass": 42.08
}
```

Champs minimaux obligatoires:
- `temperature`
- `mass`

Le champ `timestamp` est recommande. Si absent, l'heure de reception est utilisee.

## 13) Criteres de reussite

- Prototype de bout en bout demonstrable, meme sur petit jeu de donnees.
- Chaine MQTT -> base de donnees -> Grafana fonctionnelle.
- MAE/RMSE calcules et interpretes.
- Livrables documentaires complets et coherents.
- Limites du modele clairement explicitees.

## 14) Risques et mitigations

- **Risque capteurs indisponibles** -> Utiliser des donnees simulees mais documentees.
- **Risque integration MQTT/DB** -> Tester d'abord avec payload minimal puis enrichir.
- **Risque manque de temps** -> Prioriser flux MQTT + dashboard + baseline avant raffinement.
- **Risque qualite de donnees** -> Ajouter un nettoyage minimal (valeurs manquantes, outliers evidents).

## 15) Livrables finaux attendus

- Prototype fonctionnel (collecte + traitement + evaluation).
- Dataset documente.
- Analyse quantitative (MAE, RMSE).
- Document ethique argumente.
- Mini revue de litterature (3 a 5 articles).

Sources de reference utilisees pour cadrer la methode: voir `docs/revue_litterature.md`.

---

### Note de pilotage

Regle de priorite pour tenir 20h:
1. Flux simulation -> MQTT stable
2. Ingestion base de donnees + dashboard Grafana
3. Export CSV + baseline qui tourne
4. Metriques interpretees
5. Documentation solide
