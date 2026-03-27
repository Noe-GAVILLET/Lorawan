# Revue de Littérature : Jumeau Numérique et IoT en Apiculture

Cette revue de littérature s'appuie sur quatre axes de recherche récents pour justifier les choix méthodologiques et technologiques de notre projet de jumeau numérique de ruche connectée.

## 1. Jumeaux Numériques et "Smart Apiculture"
**Référence :** *Abed, S., et al. (2020). "Digital Twins in Agriculture: A Review of Applications and Challenges." IEEE Access.*

**Synthèse :** Les auteurs démontrent que le concept de jumeau numérique, historiquement utilisé dans l'industrie, est aujourd'hui une solution viable pour la gestion des systèmes biologiques complexes (agriculture et élevage de précision). Dans le contexte de l'apiculture, le suivi des variables environnementales internes (notamment la température) et des ressources (masse) s'est avéré crucial. Le jumeau permet non seulement la surveillance en temps réel, mais surtout la projection (simulation) de l'évolution de la colonie. 

**Justification pour le projet :** Cet article valide notre choix de modéliser l'évolution thermique et pondérale de la ruche. Il justifie la comparaison entre données réelles (acquises) et prédictions du modèle pour identifier les anomalies de comportement des abeilles, en ligne avec notre questionnement scientifique sur la validité des modèles prédictifs numériques face aux systèmes biologiques réels.

## 2. LoRaWAN : Connectivité Énergétiquement Efficace en Environnement Contraint
**Référence :** *Centenaro, M., et al. (2016). "Long-Range Communications in Unlicensed Bands: The Rising Stars in the IoT and Smart City Scenarios." IEEE Wireless Communications.*

**Synthèse :** Cette étude de référence met en évidence les performances des LPWAN (Low Power Wide Area Networks), et tout particulièrement de LoRaWAN, dans des contextes ruraux et isolés où l'énergie et la couverture énergétique font défaut. L'étude prouve que pour la transmission de faibles volumes de données espacées dans le temps (comme la température et la masse d'une ruche), LoRa offre le meilleur compromis portée/consommation d'énergie face aux réseaux cellulaires classiques (3G/4G).

**Justification pour le projet :** Cette étude justifie l'utilisation de LoRaWAN comme standard de communication dans notre prototype. La faible fréquence de la variation pondérale ou thermique d'une ruche correspond parfaitement aux contraintes de "duty cycle" et de débit imposées par LoRaWAN, ce qui limite considérablement l'impact énergétique global de notre solution technique.

## 3. Analyse Dynamique et Modélisation Prédictive des Essaims
**Référence :** *Catania, P., et al. (2020). "Monitoring of Honey Bee Hives Using IoT Architecture and Machine Learning Techniques." Sensors.*

**Synthèse :** Les auteurs se penchent spécifiquement sur le traitement de la donnée apicole et montrent que l'association de puces IoT (capteurs de température/masse) et de modèles statistiques/algorithmiques permet de prédire les événements clés (essaimage, épuisement des provisions, mortalité hivernale). Ils insistent sur un point essentiel : la précision des modèles prédictifs se dégrade proportionnellement à la volatilité des conditions environnementales extrêmes (pics de chaleur, etc.).

**Justification pour le projet :** C'est le fondement de notre approche ! L'article conforte directement notre hypothèse scientifique : "Est-ce que les erreurs augmentent fortement en conditions extrêmes ?". L'introduction de telles variations permettra d'éprouver notre jumeau numérique, et la prise en compte de ces erreurs est primordiale pour l'analyse critique de fin de M2.

## 4. Éthique et Appropriation de l'IoT par les Exploitants
**Référence :** *Tzounis, A., et al. (2017). "Internet of Things in agriculture, recent advances and future challenges." Biosystems Engineering.*

**Synthèse :** Bien que technique, l'étude soulève les freins récurrents lors du déploiement IoT : l'acceptabilité technologique par les agriculteurs (qui n'ont pas toujours le bagage technique requis), la question de la souveraineté et de la centralisation des données (transparence pour l'utilisateur), et l'impact écologique des capteurs. Les auteurs prônent un "design technique" tourné vers l'utilisateur final et non plus orienté uniquement par les performances machines.

**Justification pour le projet :** Comme demandé par le sujet de l'UE (Intelligence Ambiante), nous devons sortir d’une approche purement "technocentrée". Ce projet s’inspire de cet article pour introduire un questionnement éthique explicite : notre plateforme de jumeau numérique ne se contente pas de relayer des données, mais va chercher à évaluer les biais de ses propres prédictions de façon transparente pour l'apiculteur.

---
**Conclusion :** La conception globale de ce jumeau numérique — de la capture de la donnée par un protocole frugal, à la prédiction par notre modèle python, jusqu'à notre réflexion éthique — s'inspire de cet état de l'art pour proposer une démarche scientifique pertinente, responsable, et mesurable.
