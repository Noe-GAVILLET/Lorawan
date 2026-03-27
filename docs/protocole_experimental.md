# Protocole experimental

## 1) Objectif

Evaluer si un jumeau numerique simple de ruche peut produire une prediction court terme utile, et mesurer la degradation en conditions extremes.

## 2) Hypotheses testees

- H1: en conditions nominales, la baseline atteint une erreur acceptable.
- H2: en conditions extremes, l'erreur augmente significativement.
- H3: la chaine simulation -> MQTT -> InfluxDB -> Grafana est exploitable pour le suivi en quasi temps reel.

## 2.1) Seuils et criteres verrouilles

- Frequence retenue: 10 minutes.
- Duree cible: 48h.
- Duree minimale acceptable (si contrainte materielle): 12h.
- Seuil H1 (nominal):
	- MAE temperature <= 1.0 C
	- RMSE temperature <= 1.3 C
- Seuil H2:
	- MAE extreme > MAE nominale
- Seuil H3:
	- flux complet sans perte bloquante sur la fenetre de test
	- mise a jour dashboard dans un delai compatible demo (ordre de quelques secondes)

## 3) Variables et mesures

### Variables observees
- temperature_real (C)
- masse_real (kg)
- timestamp (ISO-8601)

### Variables derivees
- temperature_pred (C)
- erreur_abs_temp = |temperature_real - temperature_pred|
- erreur_quad_temp = (temperature_real - temperature_pred)^2

## 4) Instrumentation

- Application Python de simulation aleatoire (temperature, masse).
- Transport MQTT vers pipeline d'ingestion Python.
- Stockage InfluxDB.
- Visualisation Grafana.
- Export CSV pour evaluation modelee.

## 5) Plan d'echantillonnage

- Frequence cible: 1 mesure toutes les 10 minutes.
- Duree minimale recommandee: 48 heures (12h minimum en mode degrade).
- Decoupage des donnees (fenetre glissante de 30 minutes):
  - Nominal: |delta temperature| <= 1.5 C ET |delta masse| <= 0.20 kg.
  - Extreme: |delta temperature| > 1.5 C OU |delta masse| > 0.20 kg.

Si la duree terrain est insuffisante, completer par des donnees simulees documentees.

## 6) Nettoyage et qualite des donnees

1. Verifier unicite et ordre des timestamps.
2. Supprimer doublons stricts.
3. Convertir toutes les dates en UTC ISO-8601.
4. Traiter valeurs manquantes:
	- gap <= 20 min: interpolation lineaire autorisee.
	- gap > 20 min: conserver vide et exclure du calcul metriques.
5. Identifier outliers par bornes physiques:
	- temperature: [10 C, 50 C]
	- masse: [0 kg, 200 kg]
6. Marquer les points exclus dans un journal de nettoyage.
5. Tracer les decisions de nettoyage dans le rapport final.

## 7) Modele et evaluation

### Baseline retenue

Prediction naive par persistence:
- temperature_pred(t) = temperature_real(t-1)

### Metriques

- MAE
- RMSE

### Comparaisons

- Resultats globaux.
- Resultats segmentes (nominal vs extreme).

### Decoupage evaluation

- Train: 70% chronologique.
- Test: 30% chronologique.
- Les metriques finales sont calculees sur le jeu test.

## 8) Critere de validation des hypotheses

- H1 validee si MAE nominale respecte le seuil fixe en amont.
- H2 validee si MAE extreme est superieure a MAE nominale.
- H3 validee si la chaine complete fonctionne sans rupture bloquante pendant la fenetre de test.

## 9) Menaces a la validite

- Taille d'echantillon limitee (20h de projet).
- Effet des capteurs (calibration, bruit, derive).
- Conditions externes non controlees.
- Biais de selection si donnees extremes peu representees.

## 10) Reproductibilite

- Conserver configuration simulation/MQTT/InfluxDB.
- Versionner scripts et exports CSV utilises.
- Rapporter clairement les parametres et seuils choisis.

## 11) Checklist execution (avant partie technique)

- Hypotheses H1/H2/H3 et seuils valides.
- Mapping des champs MQTT vers dataset valide.
- Fenetre nominal/extreme definie (30 min).
- Regles de nettoyage figees.
- Table de resultats prete a remplir dans `livrables/resultats.md`.