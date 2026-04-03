# Protocole Experimental

## 1) Objectif

Évaluer dans quelle mesure un jumeau numérique, couplant un modèle biologique (BEEHAVE-like) et une alerte de "Time-Series" (dérivée), peut prédire et alerter un état critique (essaimage) sous contrainte d'un réseau dégradé (LoRaWAN).

## 2) Question Scientifique et Hypothèses de Recherche

Le sujet initial pose deux questions fondamentales auxquelles ce protocole répond de manière distincte :

> **Q1** : *Dans quelle mesure un jumeau numérique basé sur des données peut-il prédire l'évolution d'un système physique réel ?*
> **Q2** : *Est-ce que les erreurs augmentent fortement en conditions extrêmes ?*

La question Q2 est intentionnellement ambiguë et appelle une réponse à **deux niveaux** :

- **Niveau 1 — Thermorégulation (modèle biophysique)** : les erreurs de prédiction thermique (MAE/RMSE vs. cible BEEHAVE à 34,5 °C) sont-elles amplifiées lors d'un essaimage ? On s'attend à une relative **stabilité** des erreurs thermiques, car la thermorégulation de la colonie est indépendante de la perte de masse.
- **Niveau 2 — Détection d'essaimage (classification)** : les pertes radio LoRaWAN créent-elles des lacunes temporelles qui empêchent l'algorithme d'alerte de détecter l'essaimage ? On s'attend à une **dégradation du Rappel** (augmentation des Faux Négatifs) lorsque le PDR chute.

Cette distinction est scientifiquement importante : un système de Jumeau Numérique peut être précis thermo-dynamiquement mais défaillant en détection d'événements discrets sous contrainte réseau. Les deux facettes doivent être évaluées séparément.

### Hypothèses formalisées

Notre modèle mathématique de l'essaimage se base sur une forte vitesse de perte de la masse. Nous voulons évaluer la résilience de notre algorithme d'alerte face à différentes qualités de transmission radio.

- **H1 (Détection Physique Nominal)** : En conditions réseau nominales (LoRaWAN Packet Delivery Rate = 90%), le Jumeau Numérique parvient à alerter sur un événement d'essaimage avec un seuil de **Précision ≥ 90 %** (peu de fausses alertes), et la MAE thermique reste inférieure à 1 °C dans les deux régimes.
- **H2 (Résilience Réseau Extrême)** : Si le réseau subit de fortes contraintes (PDR = 65 %), l'interpolation échouera partiellement et le système d'alerte verra chuter son **Rappel** (augmentation des Faux Négatifs), confirmant que les erreurs de détection augmentent en conditions dégradées — même si les erreurs thermiques restent stables.
- **H3 (Intégration de la chaîne complète)** : La chaîne d'intégration MQTT → InfluxDB → Grafana est stable sur une durée d'au moins 6 heures sans interruption ni perte de données non liée au PDR simulé.

## 3) Définitions et Criteres

- **Couvain Nominal** : Température interne maintenue entre 34°C et 35°C par les abeilles, peu importe les variations du jour et de la nuit.
- **Cycle de Butinage** : Perte lente de masse entre 8h et 11h (départ des butineuses), gain de masse de 11h à 18h (+0.2 kg par heure simulée). 
- **Événement "Essaimage"** : Déclenchement brutal (simulateur en SCENARIO=extreme) provoquant une chute très rapide (dérivée **≤ −0,03 kg/min**, conforme au seuil implémenté dans `train_eval.py`).
- **Packet Delivery Rate (PDR)** : Pourcentage de paquets télémesure survivant au trajet IoT. 

## 4) Variables et mesures

### Variables observées brutes
- timestamp (UTC)
- temperature_real (C)
- masse_real (kg)
- temperature_ambient (C)

### Variables derivées
- mass_diff (kg)
- time_diff_min (min)
- mass_derivative (kg/min)
- predicted_swarming (Boolean)

## 5) Plan d'echantillonnage

- **Génération via Simulateur Biotique (`model/random_data_publisher.py`)** : Le publisher mqtt utilise l'heure système courante. Son intervalle de publication simule grossièrement un pas de temps (chaque publication = intervalle de calcul d'une dérivée).
- Pour tester H1, la variable paramètre globale `LORAWAN_PDR` est fixée à `0.9`.
- Pour simuler l'événement d'essaimage, le mode `SCENARIO=extreme` doit être lancé pendant une plage englobant 13:30 et 14:30 (heures UTC).
- En conditions optimales, le système MQTT tournera plusieurs heures. S'il n'y a pas assez de temps, régler le Publisher sur 1 message par seconde pour simuler des "heures/jours" de données plus rapidement.

## 6) Nettoyage et Traitement des Données (Pipeline)

1. Envoi par MQTT (taux d'échec volontaire LORAWAN_PDR)
2. Ingestion via InfluxDB.
3. Exportation et ordonnancement (script `export_csv.py`).
4. **Interpolation Linéaire** : L'algorithme python de validation remplit les "trous" créés par la radio afin de permettre un calcul de dérivée de la masse sur une série temporelle fluide.

## 7) Modèle de Détection d'Essaimage (Alerte)

Si la dérivée temporelle de la masse tombe en dessous de **−0,03 kg/min**, une alerte "Essaimage" (`predicted_swarming = True`) est enregistrée.

> **Justification du seuil** : en régime nominal, la dérivée maximale en valeur absolue est de l'ordre de +0,003 kg/min (départ des butineuses). En régime extrême (SCENARIO=extreme), le simulateur impose une perte de 2,5 kg/h, soit −0,042 kg/min en continu. Le seuil −0,03 kg/min sépare proprement les deux régimes avec une marge de sécurité d'un facteur 10 côté nominal et d'un facteur 1,4 côté extrême. Ce seuil est implémenté dans `model/train_eval.py` (constante `SWARM_DERIVATIVE_THRESHOLD`).

## 8) Critères de validation des hypothèses

L'évaluation porte sur une **Ground Truth** construite à partir du tag `scenario` enregistré dans InfluxDB au moment de la publication (champ indépendant de la prédiction, valeur `nominal` ou `extreme`). Cette approche évite le biais circulaire où la ground truth serait dérivée de la même métrique que la prédiction.

> **Note de rigueur** : le dataset H1 (PDR=0.90, intervalle 5 s) a été produit avant l'implémentation du tag `scenario`. Sa ground truth repose sur la plage horaire de déclenchement (13:30–14:30), ce qui introduit un biais partiel. Le dataset H2 (PDR=0.65, intervalle 60 s) utilise le tag `scenario` — ses résultats sont scientifiquement plus rigoureux.

**Validation Q2 — Thermorégulation (Niveau 1)** :
- La MAE thermique doit être calculée séparément en régime nominal et extrême.
- Si la différence de MAE entre les deux régimes est < 0,1 °C, on conclut que les erreurs thermiques **n'augmentent pas** en conditions extrêmes → résultat négatif attendu, mais scientifiquement important.

**Validation H1 — Détection nominale (Niveau 2)** :
- **H1 est validée** si la Précision ≥ 0,90 sur le dataset PDR=0,90.

**Validation H2 — Dégradation réseau (Niveau 2)** :
- **H2 est validée** en comparant H1 et PDR=0,65 : une chute du Rappel (augmentation des FN) confirme que les erreurs de détection augmentent sous contrainte réseau.

## 9) Menaces à la validité

- **Trivialité du F1 = 1,00 sur H1** : le simulateur génère des dérivées de masse séparées d'un facteur 14 entre les régimes nominal (≈ −0,003 kg/min) et extrême (≈ −0,042 kg/min). Le seuil de seuillage (−0,03 kg/min) est fixé manuellement entre ces deux valeurs connues à l'avance. En conséquence, H1 ne peut pas produire de résultat autre que F1 = 1,00 et constitue une **baseline de référence** plutôt qu'un résultat d'apprentissage. La validité interne réelle de la démarche repose sur H2 (données H2 non déterministes, contrainte réseau externe au modèle).
- La simulation du butinage reste très grossière (les retours de miel au centigramme ne sont pas réels, tout comme le "pic" de départ à 8h tapante).
- Un vrai essaimage s'accompagne d'un changement spectral sonore (fréquence de battement des ailes des futures reines, dit "Chant des reines") que ce modèle n'aborde pas, réduisant ses faux-positifs virtuels par rapport à la réalité.
- L'absence de capteurs physiques réels (ruche hardware) constitue la principale limite de validité externe : les résultats sont valides pour la simulation mais leur transférabilité à un vrai déploiement LoRaWAN reste à démontrer.
- Le PDR est simulé comme un processus de Bernoulli indépendant (tirage aléatoire uniforme par paquet). Un vrai canal radio LoRaWAN présente des pertes corrélées en rafales (*burst errors*), ce qui pourrait amplifier l'effet H2 (pertes consécutives > pertes indépendantes).
- La ground truth du dataset H1 est fondée sur la plage horaire de déclenchement (biais circulaire partiel). Seul le dataset H2 utilise le tag `scenario` indépendant de la dérivée.
- **Durée de simulation limitée (8 h)** : une saison apicole réelle dure 6 mois avec des variations saisonnières (floraison, hivernage, changements de colonie). Le modèle reproduit le même cycle journalier sans variation inter-journalière. Les résultats ne couvrent pas les dynamiques longues (dépérissement progressif, variations de disponibilité du nectar) et leur validité à l'échelle de la semaine ou du mois n'est pas testée.
- **Absence d'intervalle de confiance** : toutes les métriques sont calculées sur un seul run avec une graine aléatoire non fixée (`random.uniform` sans `random.seed`). La reproductibilité des résultats sur plusieurs runs indépendants n'est pas établie. En science expérimentale, un résultat ponctuel sans estimation de variance n'est pas généralisable.