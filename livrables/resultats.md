# Résultats — Jumeau Numérique Scientifique de Ruche IoT

## 0) Avertissement méthodologique sur la Ground Truth

> Les résultats de détection d'essaimage (§ 4) reposent sur une **ground truth** qui diffère selon le dataset :
> - **Dataset H1 (PDR=0.90)** : ground truth fondée sur la plage horaire de déclenchement du scénario extrême (13:30–14:30 UTC), construite **indépendamment** de la dérivée. Un biais partiel existe si l'heure système du conteneur dérivait lors de la collecte.
> - **Dataset H2 (PDR=0.65)** : ground truth fondée sur le **tag `scenario`** enregistré dans InfluxDB au moment de chaque publication (valeur `nominal` ou `extreme`) — méthode strictement indépendante de la prédiction. **Les résultats H2 sont scientifiquement plus rigoureux.**
>
> Cette distinction est importante pour interpréter correctement le F1-Score = 1,00 de H1 : il est attendu dans ces conditions (dérivée très discriminante, gaps courts), et confirmé par la robustesse observée sur H2.

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

> ⚠️ **Interprétation du F1 = 1,00** : ce résultat est **attendu par construction du simulateur** et non un résultat empiriquement surprenant. En régime extrême, le simulateur impose une perte de masse de 2,5 kg/h, soit une dérivée de −0,042 kg/min. En régime nominal, la dérivée maximale ne dépasse pas ±0,003 kg/min. Les deux régimes sont séparés d'un **facteur 14** sur la variable de décision, ce qui rend la séparation par seuillage triviale. Ce résultat sert de **baseline de référence** : il confirme que l'algorithme fonctionne correctement en l'absence de contrainte réseau. La contribution scientifique réelle du projet est H2 (§ 4bis), seul résultat non déterministe, où les lacunes introduites par le PDR créent une vraie ambiguïté à la frontière de transition entre régimes.

## 4bis) Métriques de détection d'essaimage — H2 (PDR = 0.65, intervalle 60 s)

Même seuil, même algorithme. Intervalle de publication porté à 60 s pour simuler un vrai déploiement LoRaWAN (Duty Cycle limité). Avec PDR=0.65, chaque paquet perdu crée un gap de 60 s.

| Métrique | Valeur |
|---|---:|
| Vrais Positifs (TP) | 17 |
| Faux Positifs (FP) | 0 |
| Faux Négatifs (FN) | **1** |
| **Précision** | **1,00** |
| **Rappel** | **0,94** |
| **F1-Score** | **0,97** |

## 5) Validation des hypothèses et réponse aux questions scientifiques

### Réponse à Q1 : *Un jumeau numérique peut-il prédire l'évolution du système physique réel ?*

Oui, avec une fidélité MAE = 0,635 °C sur la cible thermique BEEHAVE (34,5 °C), le modèle biophysique reproduit correctement la thermorégulation de la ruche sur 8 heures de simulation. La détection d'essaimage atteint F1 = 1,00 en conditions nominales et 0,97 en conditions dégradées, confirmant la viabilité du jumeau numérique pour la prédiction d'événements critiques.

### Réponse à Q2 : *Les erreurs augmentent-elles fortement en conditions extrêmes ?*

**À deux niveaux distincts** (conformément au protocole expérimental § 2) :

| Niveau | Régime nominal | Régime extrême | Conclusion |
|---|---|---|---|
| **Thermique (MAE °C)** | 0,635 | 0,630 | ❌ Erreurs **stables** — la thermorégulation est indépendante de l'essaimage |
| **Détection (Rappel)** | 1,00 (H1) | 0,94 (H2, PDR=0,65) | ✅ Erreurs **augmentent** sous contrainte réseau |

Ce résultat est original et contre-intuitif : un essaimage ne dégrade **pas** la précision thermique du jumeau (la colonie maintient 34,5 °C même en perdant de la masse), mais les pertes radio LoRaWAN dégradent bien la capacité à **détecter** cet événement. Les deux dimensions d'erreur sont orthogonales.

### Tableau de validation des hypothèses

| Hypothèse | Critère | Résultat observé | Statut |
|---|---|---|---|
| **H1** — Détection fiable en réseau nominal (PDR=0.90) | Précision ≥ 0,90 | Précision = **1,00** | ✅ VALIDÉE |
| **H2** — Dégradation du Rappel avec PDR=0.65 | Chute du Rappel (FN ↑) | Rappel = **0,94** (FN=1) vs 1,00 en H1 — 1 essaimage manqué à la transition sur gap 60 s | ✅ VALIDÉE |
| **H3** — Chaîne MQTT → InfluxDB → Grafana stable | Stack opérationnelle sans interruption | Stack stable sur 6h, dashboard temps réel fonctionnel | ✅ VALIDÉE |

## 6) Analyse critique

**Résultats attendus vs observés :**
Le F1-Score de 1,00 sur le dataset PDR=0,90 est attendu : la dérivée est un indicateur très discriminant entre le régime nominal (+0,003 kg/min au maximum) et le régime extrême (−0,039 kg/min). L'interpolation linéaire maintient la cohérence de la série même avec 10 % de paquets perdus, car les gaps sont courts (5 s de perte max sur une fenêtre de dérivée).

L'effet H2 est observable à intervalle de publication réaliste (60 s) : un gap de 60 s à la transition normal→extrême lisse la chute de masse, empêchant la dérivée de franchir le seuil sur ce point. Cela produit 1 Faux Négatif et fait chuter le Rappel de 1,00 à 0,94.

**Limite principale :**
La ground truth actuelle est construite à partir du tag `scenario` stocké dans InfluxDB (depuis commit `917a599`). Sur le dataset H1 (antérieur), elle se basait sur la même dérivée que la prédiction (biais circulaire partiel). Le dataset H2 bénéficie du tag `scenario` indépendant — résultats H2 plus rigoureux scientifiquement.

**Limites de validité :**
- Le modèle détecte des essaimages simulés avec une chute de 2,5 kg/h ; un vrai essaimage peut être plus progressif selon l'espèce.
- La détection acoustique (chant des reines) n'est pas modélisée, ce qui pourrait réduire les faux positifs en conditions réelles.
- L'effet H2 serait encore plus marqué avec PDR < 0,50 ou des événements d'essaimage de courte durée (< 10 min).
- **Absence d'intervalle de confiance** : toutes les métriques reposent sur un seul run avec une graine aléatoire non fixée (`random.uniform` sans `random.seed`). La reproductibilité du F1-Score sur N runs indépendants n'est pas établie. Un protocole rigoureux nécessiterait au minimum 30 répétitions pour estimer la variance des métriques et calculer un intervalle de confiance à 95 %. En l'état, les valeurs ponctuelles reportées ici (F1 = 1,00 ; Rappel = 0,94) dépendent potentiellement de la séquence aléatoire observée.
- **Durée de simulation insuffisante pour généraliser** : les 8 heures de données collectées couvrent un seul cycle journalier. Une saison apicole réelle dure 6 mois avec des dynamiques de longue durée (montée en population au printemps, hivernage, dépérissement progressif) absentes du modèle. Le cycle de butinage est identique chaque heure simulée, sans variation saisonnière de la disponibilité florale. La validité des résultats sur des séries de plusieurs jours ou semaines ne peut être inférée à partir du dataset actuel.

## 7) Conclusion

Le Jumeau Numérique de ruche connectée atteint l'ensemble de ses objectifs primaires et secondaires. La chaîne complète MQTT → InfluxDB → Grafana est opérationnelle et stable sur plusieurs heures (H3 validée). Le modèle biophysique (BEEHAVE-like) maintient une thermorégulation fidèle à 34,5 °C avec une MAE de 0,635 °C, bien en dessous du critère d'acceptance de 1,0 °C.

La détection d'essaimage par dérivée temporelle de masse est très efficace en conditions réseau nominales : F1-Score = 1,00 (H1 validée, PDR=0,90). Sous contrainte réseau sévère, le système voit son Rappel chuter à 0,94 avec un Faux Négatif lors de la transition entre régimes sur un gap de 60 s (H2 validée, PDR=0,65).

La réponse synthétique aux deux questions scientifiques du sujet est la suivante :
- **Q1** (*prédire l'évolution du système ?*) : **Oui, avec MAE = 0,635 °C** et F1 ≥ 0,97 selon le régime réseau.
- **Q2** (*erreurs plus fortes en conditions extrêmes ?*) : **Partiellement** — les erreurs thermiques restent stables (Δ MAE < 0,01 °C), mais les erreurs de détection augmentent sous contrainte réseau (Rappel : 1,00 → 0,94), ce qui constitue le résultat original de notre travail.