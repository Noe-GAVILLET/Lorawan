# Resultats

## 1) Contexte d'evaluation

- Modele teste: baseline par persistence.
- Jeu de test: 30% chronologique de la serie.
- Frequence: 10 minutes.
- Periode evaluee:

## 2) Metriques globales

| Metrique | Valeur |
|---|---:|
| MAE temperature (C) | |
| RMSE temperature (C) | |

## 3) Metriques par regime

| Regime | MAE temperature (C) | RMSE temperature (C) | Nb points |
|---|---:|---:|---:|
| Nominal | | | |
| Extreme | | | |

## 4) Validation des hypotheses

| Hypothese | Critere | Resultat observe | Statut |
|---|---|---|---|
| H1 | MAE nominale <= 1.0 C et RMSE nominale <= 1.3 C | | A valider |
| H2 | MAE extreme > MAE nominale | | A valider |
| H3 | Chaine simulation -> MQTT -> InfluxDB -> Grafana stable | | A valider |

## 5) Analyse critique

- Resultats attendus vs observes:
- Conditions de test (nominal/extreme):
- Principales causes d'erreur probables:
- Limites de validite:

## 6) Captures et preuves

- Capture dashboard Grafana:
- Extrait brut MQTT:
- Extrait CSV exporte:

## 7) Conclusion

Conclusion synthese (5-10 lignes) sur:
- la performance reelle du MVP,
- la validite des hypotheses,
- les ameliorations prioritaires si temps supplementaire.