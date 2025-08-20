# cortex-analyst-seqens

Modèle sémantique pour l'analyse des demandes des locataires

---

Aperçu

Ce dépôt décrit un modèle sémantique permettant d’analyser les demandes des locataires provenant de multiples canaux (email, téléphone, etc.), de suivre leur statut (ouvert, en cours, fermé, escaladé) et d’explorer les interactions liées. Le modèle facilite l’accès aux informations clés telles que les catégories de demandes, les dates de création et de clôture, les territoires et groupes, ainsi que l’évolution des demandes dans le temps.

Objectifs

- Centraliser et uniformiser l’analyse des demandes des locataires.
- Fournir des métriques prêtes à l’emploi (volumétrie, délais, répartition par canal/catégorie/territoire).
- Permettre l’exploration ad hoc des tendances et des performances opérationnelles.

Questions métiers prises en charge (exemples)

- Combien de demandes ont été reçues par catégorie ou par canal ?
- Quel est le temps moyen de traitement/résolution des demandes ?
- Quelles sont les demandes en cours et quel est leur statut actuel ?
- Quelle est la répartition des demandes par territoire ou par groupe ?
- Quelles demandes sont encore en attente de clôture ou de transfert ?
- Combien de demandes ont été reçues cette semaine/mois par territoire ?
- Quelle est l’évolution du volume des demandes dans le temps (jour/semaine/mois) ?

Champs et dimensions clés

- Canaux (CHANNEL) : source de la demande (email, téléphone, etc.).
- Statut (REQUESTSTATUS, STATUS) : suivi de l’état (ouvert, en cours, fermé, escaladé…).
- Dates clés (CREATEDON, CLOSINGDATE) : création et clôture pour calculer délais et tendances.
- Évolution (MODIFIEDON, MODIFIEDAT) : dernières modifications pour suivre l’historique.
- Catégories (CATEGORY, CS_SUBCATEGORY) : typologie des demandes (questions, technique, administratif, etc.).
- Territoires et groupes (CS_TERRITORY, CS_GROUP) : analyse géographique et organisationnelle.

Métriques proposées

- Demandes ouvertes (Open Requests): nombre de demandes avec statut ouvert/en cours.
- Demandes fermées (Closed Requests): nombre de demandes clôturées sur une période.
- Temps moyen de traitement (Avg Handling Time): moyenne de CLOSINGDATE - CREATEDON pour les demandes clôturées.
- Âge des demandes (Request Age): nombre de jours depuis CREATEDON (pour les demandes non clôturées).
- Répartition par canal/catégorie/territoire/groupe: part relative (%) ou volumes absolus.

Exemples d’analyses (pseudo-SQL)

- Volume par canal: SELECT CHANNEL, COUNT(*) AS requests FROM Requests GROUP BY CHANNEL;
- Temps moyen de résolution: SELECT AVG(DATEDIFF(day, CREATEDON, CLOSINGDATE)) AS avg_days FROM Requests WHERE CLOSINGDATE IS NOT NULL;
- Backlog par statut: SELECT STATUS, COUNT(*) FROM Requests WHERE STATUS IN ('Open','In progress','Escalated') GROUP BY STATUS;
- Répartition par territoire et catégorie: SELECT CS_TERRITORY, CATEGORY, COUNT(*) FROM Requests GROUP BY CS_TERRITORY, CATEGORY;
- Tendances mensuelles: SELECT DATEFROMPARTS(YEAR(CREATEDON), MONTH(CREATEDON), 1) AS month, COUNT(*) FROM Requests GROUP BY DATEFROMPARTS(YEAR(CREATEDON), MONTH(CREATEDON), 1) ORDER BY month;

Bonnes pratiques de modélisation

- Normaliser les valeurs de statut et de canal pour éviter les doublons (ex. "Email" vs "email").
- Définir des clés stables (ex. identifiant de demande) et des dates cohérentes (timezone, format).
- Calculer les métriques dérivées (âge, temps de traitement) au même endroit pour cohérence.
- Documenter les règles métier (qu’est-ce qu’une demande ouverte ? qu’est-ce qu’une escalade ?).

Qualité et gouvernance des données

- Détection des doublons : identifier les demandes créées plusieurs fois via différents canaux.
- Complétude : s’assurer que CREATEDON/STATUS/CATEGORY sont systématiquement renseignés.
- Fraîcheur : définir des SLA de mise à jour (quotidienne, horaire) selon les besoins opérationnels.
- Traçabilité : conserver les dates de modification (MODIFIEDON/MODIFIEDAT) pour l’audit.

Démarrage rapide

- Intégrer vos données sources en respectant les champs clés listés ci-dessus.
- Mapper vos colonnes aux dimensions/métriques du modèle (CHANNEL, STATUS, CREATEDON, CLOSINGDATE, CATEGORY, CS_TERRITORY, CS_GROUP, etc.).
- Calculer les métriques standard (âge, temps de traitement) et valider les résultats sur un échantillon.
- Construire vos tableaux de bord et analyses (volumétrie, délais, répartition, tendances).

Roadmap (suggestions)

- Ajout d’indicateurs SLA (si date d’échéance disponible).
- Analyse des escalades et des transferts inter-groupes.
- Segmentation par type de locataire et criticité.
- Détection d’anomalies et alerting sur pics de demandes.

Contribution

Les contributions sont les bienvenues. Ouvrez une issue ou une pull request pour proposer des améliorations du modèle, des métriques ou de la documentation.

Licence

À définir. Ajoutez un fichier LICENSE si nécessaire.
