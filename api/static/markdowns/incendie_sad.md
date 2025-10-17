# La méthode Predictops

Le système de prédiction d'incendies de PredictOps intègre environ quarante paramètres, regroupés en trois catégories principales : *topographique* (incluant l'altitude, la couverture du sol et l'indice de végétation), *météorologique* (comme l'évolution climatique sur une semaine, les indices du système canadien et les données météorologiques du jour même), et *socio-économique* (tels que la densité de population et la proximité aux routes). Ce système s'appuie sur un modèle d'intelligence artificielle formé sur des données historiques collectées de 2018 à 2022. L'objectif principal du modèle est de distinguer les points où il y a des feux de ceux où il n'y en a pas. Pour ce faire, les points de non-feux ont été générés dans une zone de 750 mètres autour de chaque point de feu identifié, et collectés à des dates où aucun incendie n'a été enregistré dans le département concerné. Le modèle d'intelligence artificielle attribue ensuite une valeur comprise entre 0 et 1, représentant sa "certitude" que le point analysé est un foyer d'incendie. Ces probabilités sont ensuite réparties en cinq classes de risques :

1. Une probabilité inférieure à 0,2 correspond à un risque *Très faible*.
2. Une probabilité entre 0,2 et 0,4 correspond à un risque *Faible*.
3. Une probabilité entre 0,4 et 0,6 correspond à un risque *Moyen*.
4. Une probabilité entre 0,6 et 0,8 correspond à un risque *Élevé*.
5. Une probabilité supérieure à 0,8 correspond à un risque *Extrême*.

