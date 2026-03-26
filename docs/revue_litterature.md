# Revue de litterature

## 1) Objectif de la revue

Soutenir les choix methodologiques du projet (architecture simulation/MQTT/InfluxDB/Grafana, protocoles de mesure, metriques d'evaluation) avec des sources techniques et scientifiques.

## 2) Sources de reference (base minimale)

1. Eclipse Paho MQTT Python Client Documentation
	- URL: https://eclipse.dev/paho/index.php?page=clients/python/docs/index.php
	- Apport: publication MQTT fiable depuis une application Python de simulation.

2. InfluxDB Documentation
	- URL: https://docs.influxdata.com/
	- Apport: modelisation de series temporelles, ecriture de points, bonnes pratiques de schema.

3. Grafana Documentation
	- URL: https://grafana.com/docs/
	- Apport: construction de dashboards, panels temporels, alerting de base.

4. IEEE IoT Journal / Sensors (revues sur apiculture de precision et IoT agricole)
	- Requete type: "precision beekeeping iot mqtt temperature hive weight"
	- Apport: variables pertinentes (temperature interne, masse), contraintes de terrain, interpretation metier.

5. Travaux sur qualite des donnees IoT et detection d'anomalies
	- Requete type: "IoT data quality missing values outlier detection time series"
	- Apport: nettoyage de donnees, gestion du bruit et des manquants, limites de validite.

## 2.1) Bibliographie a renseigner (format rendu)

Completer 3 a 5 references scientifiques avec le format suivant:

1. Titre:
	- Auteurs:
	- Annee:
	- Venue (journal/conference):
	- DOI/URL:
	- Apport pour le projet (2 lignes):

2. Titre:
	- Auteurs:
	- Annee:
	- Venue (journal/conference):
	- DOI/URL:
	- Apport pour le projet (2 lignes):

3. Titre:
	- Auteurs:
	- Annee:
	- Venue (journal/conference):
	- DOI/URL:
	- Apport pour le projet (2 lignes):

4. Titre:
	- Auteurs:
	- Annee:
	- Venue (journal/conference):
	- DOI/URL:
	- Apport pour le projet (2 lignes):

5. Titre:
	- Auteurs:
	- Annee:
	- Venue (journal/conference):
	- DOI/URL:
	- Apport pour le projet (2 lignes):

## 3) Comment ces sources soutiennent les hypotheses

- H1 (prediction court terme): appui sur methodes baseline de series temporelles et metriques MAE/RMSE.
- H2 (degradation extreme): appui sur litterature data quality/anomaly pour segmenter nominal vs extreme.
- H3 (faisabilite operationnelle): appui sur documentation MQTT/InfluxDB/Grafana pour une chaine reproductible.

## 4) Critere de selection des articles scientifiques

- Publication recente (priorite 2019+).
- Donnees terrain reelles preferees.
- Presence d'une methode d'evaluation claire.
- Pertinence directe pour capteurs ruche, IoT faible conso, ou jumeau numerique simplifie.

## 5) Limites de la revue (MVP 20h)

- Revue ciblee et non exhaustive.
- Priorite a 3-5 references robustes pour soutenir les choix concrets du prototype.

## 6) Strategie de recherche rapide (30-45 min)

1. Interroger IEEE Xplore et MDPI Sensors avec 2 requetes ciblees.
2. Filtrer 2019+ et langue anglaise.
3. Garder uniquement les papiers avec methode + metriques explicites.
4. Extraire pour chaque papier: variable mesuree, frequence, metrique, limite.
5. Reporter ces elements dans la trame ci-dessus.