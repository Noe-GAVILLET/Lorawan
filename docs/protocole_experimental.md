# Protocole Experimental

## 1) Objectif

Évaluer dans quelle mesure un jumeau numérique, couplant un modèle biologique (BEEHAVE-like) et une alerte de "Time-Series" (dérivée), peut prédire et alerter un état critique (essaimage) sous contrainte d'un réseau dégradé (LoRaWAN).

## 2) Hypothèses de Recherche (Reformulées)

Notre modèle mathématique de l'essaimage se base sur une forte vitesse de perte de la masse. Nous voulons évaluer la résilience de notre algorithme d'alerte face à différentes qualites de transmission radio.

- **H1 (Détection Physique Nominal)** : En conditions réseau de base (LoRaWAN Packet Delivery Rate = 90%), le "Jumeau Numérique" parvient à alerter sur un événement d'essaimage avec un seuil de **Précision >= 90%** (peu de fausses alertes).
- **H2 (Résilience Réseau Extrême)** : Si le réseau subit de fortes contraintes (interférences, pertes massives menant à un Packet Delivery Rate = 65%), l'interpolation échouera partiellement et le système d'alerte verra chuter son **Rappel** (il manquera les alertes d'essaimage).

## 3) Définitions et Criteres

- **Couvain Nominal** : Température interne maintenue entre 34°C et 35°C par les abeilles, peu importe les variations du jour et de la nuit.
- **Cycle de Butinage** : Perte lente de masse entre 8h et 11h (départ des butineuses), gain de masse de 11h à 18h (+0.2 kg par heure simulée). 
- **Événement "Essaimage"** : Déclenchement brutal (simulateur en SCENARIO=extreme) provoquant une chute très rapide (dérivée <= -0.05 kg / minute).
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

Si la dérivée temporelle de la masse tombe en dessous de -0.05 kg/Minute, une alerte "Essaimage" (predicted_swarming = True) est enregistrée.

## 8) Criteres de validation des hypotheses

L'évaluation porte sur une "Ground Truth" (la plage absolue où l'évènement destructeur est commandé par le simulateur entre 13:30 et 14:30).

- **H1 est validée** si le F1-Score et spécifiquement la **Précision** ressortent >= 0.90 sur les tests pour un dataset PDR=0.9.
- **H2 est validée** en confrontant ce test avec un dataset PDR=0.65, et en démontrant logiquement la chute du FN (Faux Négatifs augmentent) et donc la chute du Rappel.

## 9) Menaces a la validite 

- La simulation du butinage reste très grossière (les retours de miel au centigramme ne sont pas réels, tout comme le "pic" de départ à 8h tapante).
- Un vrai essaimage s'accompagne d'un changement spectral sonore (fréquence de battement des ailes des futures reines dite "Chant des reines") que ce modèle n'aborde pas, réduisant ses faux-positifs virtuels par rapport à la réalité.