# Cortex Analyst Seqens

Application Streamlit intégrée à Snowflake Cortex Analyst pour l’analyse des demandes des locataires.
Le fichier colibri_crm.yaml est une ressource sémantique consommée par l’application, pas une finalité en soi.

Résumé
- Cette app Streamlit (cortext-seqens.py) s’exécute avec un Session Snowpark actif et appelle l’API Cortex Analyst de Snowflake pour générer des requêtes SQL à partir de questions en langage naturel.
- Le modèle sémantique (colibri_crm.yaml) sert de ressource de contexte à Cortex Analyst afin d’orienter la génération de SQL et la compréhension métier.
- L’application propose:
  - Une vue “Data” pour explorer rapidement les tables du schéma COLIBRI
  - Un chat “Cortex Analyst” pour poser des questions, afficher le SQL généré, exécuter la requête et visualiser les résultats et graphiques

Fonctionnalités
- Navigation simple via la sidebar:
  - About App: présentation des capacités de l’outil (texte)
  - Data: exploration des tables du schéma COLIBRI (aperçu, filtres simples, stats descriptives)
  - Cortex Analyst: chat alimenté par l’API Analyst + rendu SQL + résultats tabulaires + graphiques (barre/ligne)
- Intégration Analyst:
  - Envoi du contexte de conversation et du chemin du modèle sémantique à l’API /api/v2/cortex/analyst/message
  - Retour du SQL généré, exécution via Snowpark, affichage des résultats et visualisations
- Mise en cache:
  - @st.cache_data pour le chargement de données et l’exécution SQL afin d’améliorer la réactivité
- UI enrichie:
  - CSS léger, logo, onglets résultats/graphiques, sélection dynamique des axes

Architecture et cartographie du code
- Fichier principal: cortext-seqens.py
  - Configuration UI:
    - st.set_page_config, styles CSS, sidebar (logo, menu)
    - Radio de navigation: ["About App", "Data", "Cortex Analyst"]
  - Session Snowpark:
    - session = get_active_session() (exécution attendue dans l’environnement Snowflake Streamlit)
  - Constantes:
    - AVAILABLE_SEMANTIC_MODELS_PATHS = ["DATA_LAKE_DEV.COLIBRI.RAW_DATA/colibri_crm.yaml"]
    - API_ENDPOINT = "/api/v2/cortex/analyst/message"
    - API_TIMEOUT = 50000 ms
  - Fonctions principales:
    - appinfo(): texte de présentation de l’outil et de ses cas d’usage métier
    - data_overview():
      - Liste les tables via INFORMATION_SCHEMA.TABLES (schema = 'COLIBRI')
      - Aperçu des données (SELECT * FROM COLIBRI.<table> LIMIT 100)
      - Filtres, sélection de colonnes, stats descriptives
      - Attention: s’appuie sur la base “courante” de la session
    - cortex_analyst_chat(session):
      - Chat + suggestions
      - get_analyst_response(): appel _snowflake.send_snow_api_request vers l’API Analyst en passant le chemin du modèle sémantique sélectionné
      - Affiche SQL généré, résultats et graphiques
      - Lecture optionnelle d’un fichier YAML depuis un stage (read_yaml_file)
    - chatbot(), chatbot_v1(), chatbotSQL():
      - Exemples/expérimentations (non liés au menu actuel). chatbot_v1 illustre une approche avec embeddings; chatbotSQL un Text2SQL générique. Ils ne sont pas utilisés par la navigation par défaut.
  - Flux à l’écran “Cortex Analyst”:
    - Sélection du modèle sémantique en sidebar
    - Saisie d’une question
    - Réception d’un message Analyst contenant SQL → exécution → affichage Data/Charts

Ressource sémantique (colibri_crm.yaml)
- Rôle: Ressource de contexte pour Cortex Analyst. Il décrit les tables/colonnes, dimensions, faits, synonymes et champs clés du domaine “demandes des locataires”.
- Localisation attendue: stage Snowflake
  - Chemin par défaut dans l’app: DATA_LAKE_DEV.COLIBRI.RAW_DATA/colibri_crm.yaml
  - L’app transmet "@<stage>/<fichier>" à l’API Analyst. Exemple: "@DATA_LAKE_DEV.COLIBRI.RAW_DATA/colibri_crm.yaml"
- Contenu (extrait):
  - Table principale: DATA_LAKE_DEV.COLIBRI.CUSTOMERREQUESTS
  - Dimensions: CHANNEL, REQUESTSTATUS/STATUS, CREATEDON/CLOSINGDATE, CATEGORY/CS_SUBCATEGORY, CS_TERRITORY, CS_GROUP, etc.
  - Faits: STATUS, CATEGORY, CS_SUBCATEGORY, etc.
- Mise à jour:
  - Versionnez colibri_crm.yaml dans ce dépôt pour la maintenance
  - Publiez la version à jour dans le stage référencé par AVAILABLE_SEMANTIC_MODELS_PATHS
  - Adaptez la liste AVAILABLE_SEMANTIC_MODELS_PATHS si vous changez d’emplacement

Prérequis
- Environnement Snowflake avec:
  - Snowflake Cortex Analyst activé
  - Rôles/droits permettant:
    - Appeler l’API Analyst depuis Streamlit (_snowflake helper disponible dans l’environnement Streamlit Snowflake)
    - Lire le stage et le fichier YAML
    - Lire les tables de DATA_LAKE_DEV.COLIBRI (ex. CUSTOMERREQUESTS)
- Exécution recommandée: App Streamlit hébergée dans Snowflake (Snowsight)
  - La fonction get_active_session() suppose un contexte Streamlit/Snowflake
- Exécution locale (optionnelle, pour développement uniquement):
  - Python 3.10+
  - pip install streamlit snowflake-snowpark-python pandas numpy
  - Note: get_active_session() échouera si vous n’établissez pas manuellement une Session Snowpark. L’app telle que fournie est destinée à Snowflake Streamlit. Pour un run local, adaptez la création de session (non fournie ici) ou utilisez Snowflake Streamlit.

Déploiement dans Snowflake (recommandé)
- Étapes indicatives:
  1) Publiez cortext-seqens.py et colibri_crm.yaml dans un stage (ou utilisez Git + Snowflake Native App si applicable)
  2) Vérifiez le chemin du stage pour colibri_crm.yaml:
     - Exemple: @DATA_LAKE_DEV.COLIBRI.RAW_DATA/colibri_crm.yaml
     - Ajustez AVAILABLE_SEMANTIC_MODELS_PATHS si nécessaire
  3) Créez ou mettez à jour l’app Streamlit dans Snowsight:
     - Snowsight > Streamlit > New App > Pointez vers le script cortext-seqens.py
  4) Donnez au rôle de l’app l’accès aux objets requis:
     - USAGE/SELECT sur DATA_LAKE_DEV.COLIBRI
     - READ sur le stage et le fichier YAML
     - Permissions nécessaires pour l’API Cortex Analyst
- Données attendues:
  - Schéma COLIBRI avec notamment la table CUSTOMERREQUESTS
  - Le YAML doit refléter la réalité des colonnes/typos (types, noms)

Utilisation
- About App:
  - Présentation et cas d’usage (demandes des locataires, canaux, statuts, délais, répartition, tendances)
- Data:
  - Liste les tables du schéma COLIBRI (dans la base active)
  - Aperçu de 100 lignes, sélection de colonnes, filtres (contains), stats descriptives
  - Conseil: Positionnez la base courante sur DATA_LAKE_DEV pour interroger COLIBRI.<table>
- Cortex Analyst:
  - Sélectionnez le modèle sémantique (colibri_crm.yaml) dans la sidebar
  - Posez une question métier (ex. “Combien de demandes ouvertes par territoire ce mois-ci ?”)
  - L’app affiche:
    - SQL généré par Analyst
    - Résultats tabulaires (paginés dans Streamlit)
    - Graphiques (bar/line) avec choix des axes
  - En cas d’erreur Analyst, un message détaillé (code, request-id, error_code) est affiché

Configuration
- Constantes (dans cortext-seqens.py):
  - AVAILABLE_SEMANTIC_MODELS_PATHS: liste de fichiers YAML disponibles, référencés depuis un stage
  - API_ENDPOINT: /api/v2/cortex/analyst/message (interne à Snowflake)
  - API_TIMEOUT: 50000 ms
- Schéma/données:
  - L’onglet Data utilise INFORMATION_SCHEMA.TABLES (schema = 'COLIBRI') et SELECT * FROM COLIBRI.<table>
  - La base courante (USE DATABASE) doit être positionnée correctement (ex. DATA_LAKE_DEV)

Notes et limitations
- Exécution locale:
  - L’app suppose un get_active_session() (environnement Streamlit Snowflake). En local, vous devrez créer une Session Snowpark (Session.builder...) et remplacer les appels correspondants. Non couvert par ce dépôt.
- Fonctions “Chatbot” et “ChatbotSQL”:
  - Exemples non exposés par le menu actuel. L’onglet opérationnel est “Cortex Analyst”.
- Sécurité/robustesse:
  - Les prompts et SQL générés sont exécutés côté Snowflake; veillez à restreindre les rôles/permissions.
  - Vérifiez l’orthographe des schémas/tables/colonnes dans colibri_crm.yaml pour éviter des erreurs SQL.
- Schéma COLIBRI:
  - Le code “Data” n’inclut pas explicitement le nom de base dans les requêtes de données; la base courante doit être correcte.

Feuille de route (suggestions)
- Ajouter une configuration pour la base par défaut (ex. sélection en sidebar)
- Permettre la sélection de plusieurs modèles sémantiques (multi-stages)
- Historiser les conversations et SQL générés (audit/traces)
- Activer les exemples Chatbot/ChatbotSQL via le menu ou les retirer pour clarté
- Ajout de métriques SLA/alerting dans les insights (si champs disponibles)

Contribution
- Ouvrez une issue/PR en décrivant:
  - Le besoin métier
  - Les modifications proposées (UI, logique, YAML)
  - L’impact sur les droits Snowflake, stages et données

Licence
- À définir. Ajoutez un fichier LICENSE si nécessaire.

Crédits
- Snowflake Snowpark, Streamlit in Snowflake, Snowflake Cortex Analyst
- Logo Seqens utilisé à des fins de démonstration
