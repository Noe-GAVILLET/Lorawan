# Projet ETRS012 - Jumeau Numerique de Ruche IoT (LoRaWAN)

## 1) Vision du projet

Ce projet vise a construire un **MVP** (Minimum Viable Prototype) de jumeau numerique pour une ruche connectee.
L'idee est de comparer un etat **mesure** (capteurs) et un etat **preduit** (modele simple), puis de quantifier l'erreur.

Architecture cible retenue: **LoRaWAN -> MQTT -> Base de donnees temporelle -> Grafana -> Modele**.

Contrainte principale: projet de cours avec **20 heures** de travail effectif.

## 2) Question scientifique

Dans quelle mesure un jumeau numerique base sur des donnees capteurs peut-il predire l'evolution d'une ruche reelle a court terme ?

Hypothese de travail:
- Un modele simple base sur l'historique recent peut fournir une prediction utile a court terme.
- Les erreurs augmentent en conditions atypiques (variation rapide de temperature, variation brusque de masse).

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
- Application serveur LoRaWAN retenue: **The Things Network (TTN)**.
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
[Ruche + Capteurs]
[Noeud LoRaWAN]
    | uplink
    v
[Reseau LoRaWAN / TTN]
    | integration MQTT
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

- **LoRaWAN**: communication bas debit, basse conso, longue portee.
- **Application serveur LoRaWAN: The Things Network (TTN)**.
- **TTN MQTT Integration**: publication des uplinks en MQTT.
- **Broker MQTT**: transport des mesures (TTN ou Mosquitto selon setup).
- **InfluxDB**: stockage series temporelles.
- **Grafana**: visualisation des mesures en quasi temps reel.
- **Python 3.10+**: langage principal pour traitement et modelisation rapide.
- **paho-mqtt**: client MQTT Python pour ingestion/bridge si necessaire.
- **influxdb-client**: ecriture/lecture InfluxDB depuis Python.
- **Pandas / NumPy**: manipulation des series temporelles et calcul numerique.
- **CSV**: format d'export simple pour l'evaluation du modele.

## 7) Plan de mise en place (20h)

| Bloc | Objectif | Duree cible |
|---|---|---:|
| 1. Cadrage + protocole | Hypothese, variables, protocole de collecte | 2h |
| 2. Flux LoRaWAN vers MQTT | Publication des mesures et test topics | 4h |
| 3. MQTT vers base de donnees | Ecriture InfluxDB + verification | 4h |
| 4. Dashboard Grafana | Panels temperature/masse + verification | 3h |
| 5. Modele baseline | Export CSV, prediction naive, MAE/RMSE | 4h |
| 6. Analyse + dossier final | Resultats, ethique, revue, mise en forme | 3h |
| **Total** |  | **20h** |

## 8) Arborescence du projet

```text
Lorawan/
|- Base.html
|- README.md
|- Subject.txt
|- firmware/
|  \- node_lorawan/
|- data/
|  |- raw/
|  \- processed/
|     \- hive_timeseries.csv
|- model/
|  |- train_eval.py
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

- `firmware/node_lorawan/`: code embarque de collecte/transmission (si materiel utilise).
- `data/raw/`: donnees brutes non modifiees.
- `data/processed/`: exports nettoyes prets pour analyse modele.
- `model/`: scripts de prediction et metriques.
- `dashboard/grafana/`: dashboard principal du MVP (obligatoire dans cette version).
- `docs/`: documents methodologiques et ethiques.
- `livrables/`: resultats finaux a rendre.

## 10) Etat actuel du code

- `model/metrics.py`: fonctions `mae` et `rmse`.
- `model/train_eval.py`: baseline de prediction par decalage temporel.
- `model/mqtt_to_influx.py`: ingestion MQTT vers InfluxDB (compatible payload direct ou TTN).
- `data/processed/hive_timeseries.csv`: echantillon de donnees de depart.

## 11) Comment executer localement

### Prerequis
- Python 3.10+

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

### Lancer l'evaluation
```bash
python model/train_eval.py
```

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
    "mass": 42.08,
    "battery": 3.79
}
```

Champs minimaux obligatoires:
- `temperature`
- `mass`

Le champ `timestamp` est recommande. Si absent, l'heure de reception est utilisee.

### Configuration TTN (rappel)

- Application serveur utilisee: **The Things Network (TTN)**.
- Source MQTT typique: `eu1.cloud.thethings.network:1883` (ou endpoint de votre region TTN).
- Topic TTN brut possible:

```text
v3/<app-id>@ttn/devices/<device-id>/up
```

Dans ce projet, un topic simplifie `hive/<device_id>/telemetry` est recommande apres normalisation.

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

---

### Note de pilotage

Regle de priorite pour tenir 20h:
1. Flux LoRaWAN -> MQTT stable
2. Ingestion base de donnees + dashboard Grafana
3. Export CSV + baseline qui tourne
4. Metriques interpretees
5. Documentation solide
