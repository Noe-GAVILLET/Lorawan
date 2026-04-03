# Revue de Littérature : Jumeaux Numériques et Apiculture de Précision

Cette revue de littérature s'appuie sur la fusion de trois paradigmes récents : la modélisation thermodynamique des ruches (HONEYBEE-pDT), la détection d'anomalies par séries temporelles (Machine Learning) et la simulation de réseaux LPWAN en milieu naturel (LoRaSim). Les cinq articles retenus ont été sélectionnés pour leur pertinence directe avec les hypothèses du projet et la robustesse de leur méthodologie.

## 1. Modélisation Thermodynamique et Jumeau Numérique (Digital Twin)

L'apiculture de précision a franchi un cap avec la proposition du modèle **HONEYBEE-pDT**, fortement inspiré du simulateur écologique **BEEHAVE** [1]. L'objectif principal de ces modèles est de calculer le *"budget énergétique"* d'une ruche en fonction des conditions extérieures.
Les travaux de Becher et al. [1] démontrent que les abeilles maintiennent une température interne très stricte, autour de 34,5 °C pour protéger le couvain. Pour contrer une baisse de la température extérieure (par exemple durant la nuit ou l'hiver), la colonie consomme du miel pour générer de la chaleur. Le Jumeau Numérique utilise ces équations biophysiques pour comparer le poids théorique attendu avec les données réelles détectables par capteurs IoT, et met ainsi en évidence les déviations liées à un stress (maladie, manque de ressources).

**Limites de BEEHAVE et écart avec notre implémentation** : il est important de souligner que BEEHAVE [1] est un modèle à base d'agents (ABM) qui simule des milliers d'abeilles individuellement, intègre un *patch model* de butinage avec des distances de vol, des ressources florales variables et une modélisation des populations de couvain sur plusieurs semaines. Notre implémentation en est une approximation de premier ordre : le cycle de butinage est réduit à une variation linéaire par paliers (−0,15 kg/h au départ, +0,20 kg/h au retour), sans variation saisonnière ni modélisation de la disponibilité florale. La thermorégulation est simulée comme une constante bruitée (34,5 ± 0,1 °C) plutôt que comme l'émergence d'un comportement collectif. Cet écart est assumé dans le cadre d'un projet académique contraint : l'objectif n'est pas de reproduire BEEHAVE mais de s'en inspirer pour générer des séries temporelles suffisamment réalistes pour tester un algorithme de détection d'essaimage. La comparaison quantitative entre les dynamiques de masse BEEHAVE réel et notre simulateur reste une perspective d'amélioration ouverte.

Le concept de Jumeau Numérique lui-même trouve sa définition formelle chez Grieves & Vickers [2], qui le définissent comme un système tripartite : l'entité physique réelle, son homologue virtuel, et le flux de données bidirectionnel les reliant. C'est précisément cette architecture que nous implémentons : données issues du simulateur biophysique (entité virtuelle) comparées à leur comportement attendu théorique (modèle BEEHAVE).

La surveillance non-intrusive par capteurs IoT comme alternative à l'inspection visuelle a été validée dans un cadre opérationnel réel par Meikle & Holst [3], qui démontrent que l'enregistrement continu du poids et de la température permet de détecter des événements biologiques majeurs (essaimage, hivernage, pic de butinage) avec une fidélité comparable à l'observation directe.

## 2. Analyse des Séries Temporelles et Détection d'Essaimage

La masse de la ruche est la donnée la plus riche en informations, mais aussi la plus bruitée par l'activité quotidienne (départ au butinage le matin, retour l'après-midi avec nectar). Les recherches récentes en Machine Learning — notamment l'approche DeepAnT de Munir et al. [4], qui utilise des réseaux de neurones convolutifs pour la détection d'anomalies non supervisée — se concentrent sur l'isolation de ruptures dans ces séries temporelles.

Un événement majeur, **l'essaimage** (départ de l'ancienne reine avec la moitié de la colonie), se caractérise par une perte brutale de masse de l'ordre de 1,5 à 3 kg en pleine journée. Comme le montre la littérature établie depuis Meikle & Holst [3], en analysant la dérivée mathématique de la masse (la vitesse de perte de poids), les algorithmes peuvent isoler informatiquement cette anomalie des fluctuations normales (humidité, butinage), fournissant un système d'alerte précoce à l'apiculteur. Notre approche par seuillage de dérivée constitue une implémentation délibérément simple et interprétable de ce principe, contrairement aux approches LSTM [4] qui offrent une meilleure généralisation mais au prix d'une boîte noire difficile à auditer.

## 3. Simulation des Réseaux Faible Consommation (LPWAN / LoRaWAN)

Le déploiement de capteurs dans un rucher (souvent situé en forêt ou en milieu rural isolé) impose des contraintes physiques propres au **LoRaWAN**. La question fondamentale de la scalabilité de ce protocole est traitée par Bor et al. [5] via leur simulateur **LoRaSim**, qui modélise les pertes de paquets radio liées au *Duty Cycle* (limites de temps d'émission), aux collisions (si le rucher est dense) et à l'atténuation path-loss (générée par le bois humide des ruches et le feuillage estival). Leurs résultats montrent que le PDR chute significativement au-delà de quelques centaines de nœuds sur un même gateway, mais reste supérieur à 90 % pour un déploiement de taille modeste — ce qui justifie notre choix de PDR = 0,90 comme condition nominale (H1) et PDR = 0,65 comme condition dégradée (H2).

Dans un système d'alerte temps réel, la perte d'un paquet de données juste au moment de l'essaimage peut désynchroniser le modèle de prédiction. Il est donc crucial pour les Jumeaux Numériques IoT d'inclure cette perte stochastique dans leur simulation pour entraîner des modèles tolérants aux données manquantes (gestion des lacunes par interpolation ou imputation). Notre pipeline — simulation PDR côté publisher → interpolation linéaire dans `train_eval.py` — reproduit précisément cette démarche de robustesse décrite dans [5].

## Conclusion

Notre projet s'inscrit pleinement dans cette littérature en consolidant :
- **(a)** le lien *Température/Masse* du budget énergétique abeille, formalisé par BEEHAVE [1] ;
- **(b)** l'architecture Jumeau Numérique telle que définie par Grieves & Vickers [2] ;
- **(c)** la surveillance IoT non-intrusive validée par Meikle & Holst [3] ;
- **(d)** la rupture par *Dérivée Temporelle* comme diagnostic rapide inspiré des approches de Munir et al. [4], mais dans une approche explicable ;
- **(e)** la dégradation probabiliste de LoRaWAN modélisée via LoRaSim [5] pour simuler des conditions de terrain crédibles.

---

## Références bibliographiques

[1] Becher, M. A., Grimm, V., Thorbek, P., Horn, J., Kennedy, P. J., & Osborne, J. L. (2014). BEEHAVE: a systems model of honeybee colony dynamics and foraging to explore multifactorial causes of colony failure. *Journal of Applied Ecology*, 51(2), 470–482. https://doi.org/10.1111/1365-2664.12222

[2] Grieves, M., & Vickers, J. (2017). Digital Twin: Mitigating Unpredictable, Undesirable Emergent Behavior in Complex Systems. In F.-J. Kahlen, S. Flumerfelt, & A. Alves (Eds.), *Transdisciplinary Perspectives on Complex Systems* (pp. 85–113). Springer. https://doi.org/10.1007/978-3-319-38756-7_4

[3] Meikle, W. G., & Holst, N. (2015). Application of continuous monitoring of honeybee colonies. *Apidologie*, 46(1), 10–22. https://doi.org/10.1007/s13592-014-0298-x

[4] Munir, M., Siddiqui, S. A., Dengel, A., & Ahmed, S. (2019). DeepAnT: A deep learning approach for unsupervised anomaly detection in time series. *IEEE Access*, 7, 1991–2005. https://doi.org/10.1109/ACCESS.2018.2886457

[5] Bor, M. C., Roedig, U., Voigt, T., & Alonso, J. M. (2016). Do LoRa Low-Power Wide-Area Networks Scale? In *Proceedings of the 19th ACM International Conference on Modeling, Analysis and Simulation of Wireless and Mobile Systems* (MSWiM '16), pp. 59–67. ACM. https://doi.org/10.1145/2988287.2989163
