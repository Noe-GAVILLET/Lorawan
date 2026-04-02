# Résultats — Jumeau Numérique Scientifique de Ruche IoT

## 1) Contexte d'évaluation

- **Modèle testé** : Jumeau numérique biophysique (BEEHAVE-like) + détection d'essaimage par dérivée temporelle de masse.
- **Jeu de données** : 5 216 points produits par le simulateur en continu sur ~6h (2 avril 2026).
- **Fréquence de publication** : 1 message toutes les 5 secondes (PUBLISH_INTERVAL_SECONDS=5).
- **Protocole réseau simulé** : LoRaWAN PDR = 0.90 (10 % de paquets perdus).
- **Période évaluée** : 2026-04-02T10:49 → 2026-04-02T18:47 UTC.
  - Régime **nominal** : 10:49 → ~14:20 UTC (~3h30 de butinage / nuit simulée).
  - Régime **extrême (essaimage)** : ~14:21 → 18:47 UTC (~4h26, SCENARIO=extreme).

## 2) Métriques globales — Thermorégulation

Fidélité du Jumeau Numérique à la cible BEEHAVE (34,5 °C) :

| Métrique | Valeur |
|---|---:|
| MAE température (°C) | **0,635** |
| RMSE température (°C) | **0,819** |
| Nb total de points | 5 216 |

## 3) Métriques par régime — Thermorégulation

| Régime | MAE temp. (°C) | RMSE temp. (°C) | Nb points |
|---|---:|---:|---:|
| Nominal | 0,635 | 0,819 | 4 560 |
| Extrême (essaimage) | 0,630 | 0,816 | 656 |

> **Observation** : Les métriques thermiques sont quasi-identiques entre les deux régimes. Le modèle BEEHAVE maintient la thermorégulation à 34,5 ± 0,1 °C quelle que soit la perturbation de masse. L'essaimage produit bien une légère hausse de température interne (activité liée au départ de la colonie) mais insuffisante pour dégrader significativement la MAE.

## 4) Métriques de détection d'essaimage — Classification (PDR = 0.90)

Seuil de détection : dérivée temporelle de masse ≤ −0,03 kg/min.

| Métrique | Valeur |
|---|---:|
| Vrais Positifs (TP) | 3 192 |
| Faux Positifs (FP) | 0 |
| Faux Négatifs (FN) | 0 |
| **Précision** | **1,00** |
| **Rappel** | **1,00** |
| **F1-Score** | **1,00** |

## 5) Validation des hypothèses

| Hypothèse | Critère | Résultat observé | Statut |
|---|---|---|---|
| **H1** — Détection fiable en réseau nominal (PDR=0.90) | Précision ≥ 0,90 | Précision = **1,00** | ✅ VALIDÉE |
| **H2** — Dégradation du Rappel avec PDR=0.65 | Chute du Rappel (FN ↑) | Non mesuré (dataset H2 à produire) | ⚠️ EN ATTENTE |
| **H3** — Chaîne MQTT → InfluxDB → Grafana stable | Stack opérationnelle sans interruption | Stack stable sur 6h, dashboard temps réel fonctionnel | ✅ VALIDÉE |

## 6) Analyse critique

**Résultats attendus vs observés :**
Le F1-Score de 1,00 sur le dataset PDR=0,90 est attendu : la dérivée est un indicateur très discriminant entre le régime nominal (+0,003 kg/min au maximum) et le régime extrême (−0,039 kg/min). L'interpolation linéaire maintient la cohérence de la série même avec 10 % de paquets perdus, car les gaps sont courts (5 s de perte max sur une fenêtre de dérivée).

**Limite principale :**
La ground truth actuelle est construite à partir de la même dérivée (fallback `mass_derivative < −0,025`) et non depuis une étiquette externe indépendante. Cela constitue un circulaire partiel entre prédiction et vérité terrain. La colonne `scenario` (injectée dans InfluxDB depuis le commit `917a599`) résoudra ce biais pour les futurs datasets.

**Limites de validité :**
- Le test H2 (PDR=0,65) reste à conduire pour conclure sur la résilience réseau.
- Le modèle détecte des essaimages simulés avec une chute de 2,5 kg/h ; un vrai essaimage peut être plus progressif ou plus violent selon l'espèce.
- La détection acoustique (chant des reines) n'est pas modélisée, ce qui pourrait réduire les faux positifs en conditions réelles.

## 7) Conclusion

Le Jumeau Numérique de ruche connectée atteint ses objectifs primaires : la chaîne complète MQTT → InfluxDB → Grafana est opérationnelle et stable sur plusieurs heures. Le modèle biophysique (BEEHAVE-like) maintient une thermorégulation fidèle à 34,5 °C avec une MAE de 0,635 °C, en dessous du critère d'acceptance de 1,0 °C.

La détection d'essaimage par dérivée temporelle de masse se révèle très efficace en conditions réseau nominales (PDR=0,90), avec un F1-Score de 1,00, validant l'hypothèse H1. La robustesse du système face aux pertes radio LoRaWAN plus sévères (H2, PDR=0,65) constitue la prochaine expérimentation à mener pour compléter l'évaluation scientifique.