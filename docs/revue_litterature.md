# Revue de Littérature : Jumeaux Numériques et Apiculture de Précision

Cette revue de littérature s'appuie sur la fusion de trois paradigmes récents : la modélisation thermodynamique des ruches (HONEYBEE-pDT), la détection d'anomalies par séries temporelles (Machine Learning) et la simulation de réseaux LPWAN en milieu naturel (LoRaSim).

## 1. Modélisation Thermodynamique et Jumeau Numérique (Digital Twin)
L'apiculture de précision a franchi un cap avec la proposition du modèle **HONEYBEE-pDT**, fortement inspiré du simulateur écologique **BEEHAVE**. L'objectif principal de ces modèles est de calculer le *"budget énergétique"* d'une ruche en fonction des conditions extérieures.
Les travaux démontrent que les abeilles maintiennent une température interne très stricte, autour de 34,5°C pour protéger le couvain. Pour contrer une baisse de la température extérieure (par exemple durant la nuit ou l'hiver), la colonie consomme du miel pour générer de la chaleur. Le "Jumeau Numérique" utilise ces équations biophysiques pour comparer le poids théorique attendu avec les données réelles détectables par capteurs IoT, et met ainsi en évidence les déviations liées à un stress (maladie, manque de ressources).

## 2. Analyse des Séries Temporelles et Détection d'Essaimage
La masse de la ruche est la donnée la plus riche en informations, mais aussi la plus bruitée par l'activité quotidienne (départ au butinage le matin, retour l'après-midi avec nectar). Les recherches récentes en Machine Learning (utilisation de modèles ARIMA, SARIMA et réseaux de neurones Bi-LSTM) se concentrent sur la détection d'anomalies dans ces séries temporelles.
Un événement majeur, **l'essaimage** (départ de l'ancienne reine avec la moitié de la colonie), se caractérise par une perte brutale de masse de l'ordre de 1.5 kg à 3 kg en pleine journée. En analysant la dérivée mathématique de la masse (la vitesse de perte de poids), les algorithmes peuvent isoler informatiquement cette "anomalie" des fluctuations métaphysiques normales (humidité, butinage), fournissant un système d'alerte précoce à l'apiculteur.

## 3. Simulation des Réseaux Faible Consommation (LPWAN / LoRaWAN)
Le déploiement de capteurs dans un rucher (souvent situé en forêt ou en milieu rural isolé) impose des contraintes physiques de type **LoRaWAN**. Des simulateurs comme **FLoRa** (basé sur OMNeT++) ou **LoRaSim** modélisent les pertes de paquets radio liées au *Duty Cycle* (limites de temps d'émission), aux collisions (si le rucher est grand) et à l'atténuation path-loss (générée par le bois humide des ruches et le feuillage estival).
Dans un système d'alerte temps réel, la perte d'un paquet de données juste au moment de l'essaimage peut désynchroniser le modèle de prédiction. Il est donc crucial pour les Jumeaux Numériques IoT d'inclure cette perte stochastique dans leur simulation pour entraîner des modèles tolérants aux données manquantes ("gap management" par interpolation ou imputation).

## Conclusion
Notre projet s'inscrit pleinement dans cette littérature en consolidant (a) le lien *Température/Masse* du budget énergétique abeille, (b) la rupture par *Dérivée Temporelle* en guise de diagnostic, et (c) la dégradation probabiliste de LoRaWAN afin de simuler des conditions de recherche crédibles et pragmatiques.
