import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import json
import time
from typing import Dict, List, Optional, Tuple


import _snowflake
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.exceptions import SnowparkSQLException

# Constants and paths
AVAILABLE_SEMANTIC_MODELS_PATHS = ["DATA_LAKE_DEV.COLIBRI.RAW_DATA/colibri_crm.yaml"]
API_ENDPOINT = "/api/v2/cortex/analyst/message"
API_TIMEOUT = 50000  # in milliseconds



# Initialize a Snowpark session for executing queries
session = get_active_session()

# Configuration de la page
st.set_page_config(page_title="Assistant IA - Colibri", layout='wide')

# Utilisation de Markdown avec CSS personnalisé
st.markdown("""
    <style>
    .title {
        font-size: 4em;  /* Taille du texte */
        font-weight: bold;  /* Gras */
        text-align: center;  /* Centrer le titre */
        color: #31c0e7;  /* Couleur personnalisée */
        font-family: 'Helvetica', sans-serif;  /* Police élégante */
        text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2);  /* Ombre portée */
    }
    </style>
""", unsafe_allow_html=True)

# Titre personnalisé avec la classe CSS
st.markdown('<h1 class="title">Assistant IA pour Colibri ❄️</h1>', unsafe_allow_html=True)

# Affichage du logo
st.sidebar.image("https://www.seqens.fr/wp-content/uploads/2019/08/Logo_SEQENS.png", use_column_width=True)

# Ajout d'un espace entre le logo et le menu
st.sidebar.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

# Ajout de styles CSS pour le menu
st.markdown("""
    <style>
    .menu-button {
        background-color: #31c0e7;
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
    }
    .menu-button:hover {
        background-color: #249dda;
    }
    </style>
""", unsafe_allow_html=True)

# Menu avec les boutons de navigation
menu_html_v1 = """
<div>
    <div class='menu-button' onclick="window.location.href='?page=AboutApp'">ℹ️ About App</div>
    <div class='menu-button' onclick="window.location.href='?page=DataOverview">📑 Data Overview</div>
    <div class='menu-button' onclick="window.location.href='?page=DataExploration'">🔍 Data Exploration</div>
    <div class='menu-button' onclick="window.location.href='?page=ColibriAnalytics'">📊 Colibri Insights Analytics</div>
    <div class='menu-button' onclick="window.location.href='?page=Chatbot'">🤖 Chatbot</div>
    <div class='menu-button' onclick="window.location.href='?page=CortexAnalyst'">💬 Cortex Analyst</div>

</div>
"""


# Menu avec les boutons de navigation
menu_html = """
<div>
    <div class='menu-button' onclick="window.location.href='?page=AboutApp'">ℹ️ About App</div>
    <div class='menu-button' onclick="window.location.href='?page=Data">📑 Data </div>
    <div class='menu-button' onclick="window.location.href='?page=CortexAnalyst'">💬 Cortex Analyst</div>

</div>
"""


st.sidebar.markdown(menu_html, unsafe_allow_html=True)

# Variable pour la sélection de l'option dans la sidebar
# choose_side_opt = st.sidebar.radio("Choisissez une option", ["About App", "Data Overview", "Data Exploration", "Colibri Insights Analytics", "Chatbot", "Cortex Analyst"])
choose_side_opt = st.sidebar.radio("Choisissez une option", ["About App", "Data", "Cortex Analyst"])


# Fonction pour charger les données
@st.cache_data
def load_data(query_of_interest):
    return session.sql(query_of_interest).to_pandas()




def appinfo():
    # Description générale
    
    st.markdown("""

    Cette application vous permet d'analyser des données, d'explorer des ressources et d'interagir avec un chatbot intelligent pour obtenir des informations précieuses.

    
    ### Outil d'Analyse des Demandes des Locataires avec Assistance IA
    Cette application permet aux utilisateurs d'analyser facilement les demandes des locataires provenant de différents canaux (email, téléphone, etc.). Grâce à des outils puissants d'analyse, elle facilite la gestion des demandes en offrant des informations précieuses sur leur état, leur statut, leur catégorie, ainsi que des données temporelles importantes (dates de création, de clôture, etc.).

    L'application est conçue pour vous aider à obtenir rapidement des informations clés sur les demandes de vos locataires et à suivre leur évolution en temps réel. Voici les types de questions auxquelles l'outil peut répondre :
    
    - Combien de demandes ont été reçues par catégorie ou par canal ?
    - Quel est le temps moyen pour traiter les demandes ?
    - Quelles sont les demandes en cours et quel est leur statut actuel ?
    - Comment sont réparties les demandes selon les territoires ou les groupes ?
    - Quelles demandes sont encore en attente de clôture ou de transfert ?
    
    L'outil permet également d'analyser les tendances des demandes au fil du temps et d'explorer les variations par groupe ou territoire.
    """)

    # Détails supplémentaires
    st.markdown("""
    ### Fonctionnalités Clés

    - **Canaux de Demandes** : Analysez les demandes provenant de différents canaux comme l'email, le téléphone, etc. Cela vous permet de savoir d'où viennent vos demandes et de mieux gérer chaque canal.
    
    - **Suivi du Statut des Demandes** : Gérez l'état de chaque demande (ouverte, en cours, fermée, escaladée) pour prioriser efficacement les actions à mener et améliorer votre réactivité.
    
    - **Dates Importantes** : Visualisez les dates de création et de clôture des demandes. Cela vous aide à analyser le temps moyen de traitement et à identifier les périodes de pic ou les délais d'attente.
    
    - **Catégories et Types de Demandes** : Classez les demandes par catégorie (questions administratives, problèmes techniques, demandes urgentes, etc.). Cela vous permet de mieux comprendre les types de problèmes rencontrés et d'y répondre plus efficacement.
    
    - **Suivi de l'Évolution des Demandes** : Suivez les demandes qui ont été modifiées au fil du temps. Cela vous permet de voir les actions entreprises et d'évaluer l'efficacité de la gestion des demandes.
    
    - **Répartition Géographique et par Groupe** : Analysez la répartition des demandes selon les territoires ou groupes. Cela vous aide à mieux comprendre l'impact des demandes dans différentes zones géographiques ou au sein de groupes spécifiques.

    """)

    # Exemple détaillé
    st.markdown("""
    ### Exemple d'Analyse des Demandes des Locataires via Plusieurs Canaux

    Cette application permet de suivre et analyser les demandes des locataires soumises par différents canaux (email, téléphone, etc.). Voici quelques exemples des questions que vous pouvez poser pour obtenir des informations pertinentes :
    
    - Combien de demandes ont été reçues cette semaine/mois par territoire ?
    - Quel est le délai moyen pour résoudre une demande ?
    - Quelle est la répartition des demandes par groupe ou par catégorie ?
    - Quelles demandes sont actuellement ouvertes et que fait-on pour les résoudre ?
    - Quel est l'impact des demandes selon les différents territoires et canaux ?

    En résumé, cette application vous permet de mieux gérer les demandes des locataires, d'optimiser le temps de traitement et de suivre les performances à travers des analyses précises, tout en offrant une vue globale de la situation.
    
    
    
    ### À propos de l'équipe :
    L'équipe derrière cette application est composée d'experts en analyse de données et en intelligence artificielle, visant à rendre l'analyse des données plus accessible et plus efficace.
    """)



# Fonction data_overview() pour avoir une vue global données de manière interactive
def data_overview():
    # Query to list tables in the 'COLIBRI' schema
    sql = """SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'COLIBRI'"""
    result = session.sql(sql).collect()
    
    # Convert the result to a Pandas DataFrame
    table_names = pd.DataFrame([row.as_dict() for row in result])

    # Display the table names
    st.write("Tables in the COLIBRI Schema of the DATA_LAKE_DEV Database:")
    st.dataframe(table_names)

    # Let the user select a table
    selected_table = st.selectbox("Choisissez une table", table_names['TABLE_NAME'])

    if selected_table:
        st.write(f"Exploration de la table : {selected_table}")
        
        # Charger les données de la table sélectionnée
        data_sql = f"SELECT * FROM COLIBRI.{selected_table} LIMIT 100"
        table_data = session.sql(data_sql).collect()

        # Convert the table data to a DataFrame
        table_df = pd.DataFrame([row.as_dict() for row in table_data])

        # Affichage de l'aperçu des données
        st.dataframe(table_df)

        # Options d'exploration supplémentaires
        st.sidebar.subheader("Options d'exploration")
        
        # Choisir des colonnes à afficher
        columns_to_show = st.sidebar.multiselect("Sélectionner les colonnes à afficher", table_df.columns.tolist())
        if columns_to_show:
            st.write("Données avec les colonnes sélectionnées :")
            st.dataframe(table_df[columns_to_show])
        
        # Appliquer un filtre aux données
        st.sidebar.subheader("Filtrer les données")
        filter_column = st.sidebar.selectbox("Choisissez une colonne pour filtrer", table_df.columns.tolist())
        filter_value = st.sidebar.text_input("Entrez la valeur de filtre")
        
        if filter_value:
            filtered_df = table_df[table_df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
            st.write(f"Données filtrées par la colonne {filter_column} avec la valeur '{filter_value}':")
            st.dataframe(filtered_df)
        
        # Afficher des statistiques de base
        if st.sidebar.checkbox("Afficher des statistiques descriptives", value=False):
            st.write("Statistiques descriptives :")
            st.write(table_df.describe())




def chatbot_v1(session):

    st.subheader("Assistant IA - Analyse des demandes des locataires")

    with st.expander("ℹ️ Instructions", expanded=True):
        st.markdown(
            """
            Cet assistant vous aide à analyser les demandes des locataires en accédant aux données pertinentes et en fournissant des insights exploitables.
            
            **Exemples de questions :**

            1. Quel est le nombre total de demandes en cours par territoire ?
            2. Quelle est la durée moyenne de traitement des demandes clôturées ce mois-ci ?
            3. Combien de demandes ont été reçues via le canal téléphonique cette semaine ?
            4. Quelles sont les demandes ouvertes les plus urgentes à traiter ?
            5. Quels sont les motifs les plus fréquents des demandes escaladées ?

            """
        )

    def build_prompt(message):
        prompt = " "
        content = " "
        num_tokens = 512
        question = st.session_state.messages[-1]["content"]
        content = get_context(question)

        if model == "llama2-70b-chat":
            num_tokens = 4096
        else:
            num_tokens = 512

        prompt += f"\"<question>\n{question}\n</question>\n"
        prompt += f"\"<content>\n{content}\n</content>\n"
        prompt += f'''
        \n Vous êtes un assistant intelligent spécialisé dans l'analyse des demandes des locataires. 
        Vous aidez les gestionnaires à comprendre les tendances, à identifier les demandes prioritaires et à optimiser les délais de traitement. 
        Basez toujours vos réponses sur les données fournies entre les balises <content> et </content>. Limitez votre réponse à {num_tokens} tokens.'''

        prompt = re.sub("'", "''", prompt)
        return prompt

    model = st.selectbox(
        "Choisissez le modèle IA à utiliser :",
        options=['llama2-70b-chat', 'llama2-7b-chat']
    )

    def get_context(question):
        sql_stmt = f'''
        WITH top_response AS (
            SELECT REQUEST_DATA, vector_cosine_distance(ct_embedding, 
            SNOWFLAKE.CORTEX.embed_text('e5-base-v2', '{question}')) as similarity 
            FROM Requests_Embedding 
            ORDER BY similarity DESC LIMIT 1
        ) 
        SELECT REQUEST_DATA FROM top_response;
        '''
        df = session.sql(sql_stmt).to_pandas()
        return df['REQUEST_DATA'][0] if not df.empty else "Aucune donnée pertinente trouvée."

    def get_df(question):
        sql_stmt = f'''
        WITH top_response AS (
            SELECT REQUEST_DATA, vector_cosine_distance(ct_embedding, 
            SNOWFLAKE.CORTEX.embed_text('e5-base-v2', '{question}')) as similarity 
            FROM Requests_Embedding 
            ORDER BY similarity DESC LIMIT 3
        ) 
        SELECT 
            REQUEST_DATA:REQUESTID::string as RequestID,
            REQUEST_DATA:CATEGORY::string as Category,
            REQUEST_DATA:STATUS::string as Status,
            REQUEST_DATA:CREATEDON::date as CreatedOn
        FROM top_response;
        '''
        df = session.sql(sql_stmt).to_pandas()
        return df

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Comment puis-je vous aider aujourd'hui ?"}]

    st.sidebar.button('Effacer l’historique du chat', on_click=clear_chat_history)

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "Comment puis-je vous aider aujourd’hui ?"}
        ]

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                prompt = build_prompt(st.session_state.messages)
                sql_stmt = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{prompt}') as answer"
                df = session.sql(sql_stmt).to_pandas()
                response = df['ANSWER'][0] if not df.empty else "Je n’ai pas trouvé d’information pertinente."
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})





def chatbot(session):
    st.subheader("Assistant IA - Analyse des demandes des locataires")

    with st.expander("ℹ️ Instructions", expanded=True):
        st.markdown(
            """
            Cet assistant vous aide à analyser les demandes des locataires en accédant aux données pertinentes et en fournissant des insights exploitables.
            """
        )



    def build_prompt(question, model):
        num_tokens = 512
        if model == "llama3.1-70b":
            num_tokens = 4096
            
            
        prompt = f'''
        Vous êtes un assistant intelligent spécialisé dans l'analyse des demandes des locataires. 
        Voici une question posée par l'utilisateur : "{question}".
        Répondez de manière pertinente en {num_tokens} tokens maximum.
        '''
        
        return prompt.replace("'", "''")  # Sécuriser l'apostrophe pour SQL


    
        

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Comment puis-je vous aider aujourd’hui ?"}]

    st.sidebar.button('Effacer l’historique du chat', on_click=clear_chat_history)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Comment puis-je vous aider aujourd’hui ?"}]

    if user_input := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": user_input})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                question = st.session_state.messages[-1]["content"]
                #prompt = build_prompt(question)
                prompt = build_prompt(question, model="mistral-7b")


                # 🔹 Simulation de l'appel au modèle sans embeddings
                model="mistral-7b"
                sql_stmt = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{prompt}') as answer"
                df = session.sql(sql_stmt).to_pandas()
                response = df['ANSWER'][0] if not df.empty else "Je n’ai pas trouvé d’information pertinente."

                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})





def chatbotSQL(session):

    st.subheader("Call Centre Insurance Assistant - Text2SQL")

    with st.expander("ℹ️ Instructions",expanded=True):
        st.markdown(
            """
            You can input your question as natural language text and the chatbot will return you the output as a table ! 
            Shows you on how to use your own co-pilot from the app.
            
            **Examples that you can use:**

            1. Give me count of records for every resolution
            2. Give me rows with the claim number CLM456789
            3. Give me all rows where purpose of call like policy inquiry in the month december 2023
            4. Give the sum of callduration for every representative where the response mode is Resolved
            5. list the unique issues handled by the representatives name starting with emma in November and end of December 2023
            6. what is the sum of call duration for every representative and for every resolution

            """
        )

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Ask your question?"}]

    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    
    # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I assist you today?"}
        ]

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    # display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = st.session_state.messages[-1]["content"]
                your_system_message=''' You are a sql expert and you know the schema of the table well and it is as below. Answer the SQL queries based on the below schema.
                  CREATE TABLE STREAMLITAPPTABLE (
                        DATETIME DATE,
                        AUDIO_FILE_NAME VARCHAR(100),
                        DURATION FLOAT,
                        CALLTOACTION VARCHAR(16777216),
                        CLAIMNUMBER VARCHAR(16777216),
                        CUSTOMER VARCHAR(16777216),
                        INTENT VARCHAR(16777216),
                        ISSUE VARCHAR(16777216),
                        POLICYNUMBER VARCHAR(16777216),
                        PURPOSEOFCALL VARCHAR(16777216),
                        REPRESENTATIVE VARCHAR(16777216),
                        RESOLUTION VARCHAR(16777216),
                        RESPONSEMODE VARCHAR(16777216),
                        MODEOFUPDATE VARCHAR(16777216),
                        NEXTSTEPS VARCHAR(16777216),
                        CALLSENTIMENT VARCHAR(8),
                        FIRSTCALLRESOLUTION VARCHAR(3)
                    )  '''
                #build_prompt(st.session_state.messages)
                # sql_stmt = f"SELECT SNOWFLAKE.ML.COMPLETE('{model}', '{prompt}') as answer"
                sql_stmt=f'''select text2sql('{prompt}')::string '''
                sql_stmt_qry= session.sql(sql_stmt).collect()[0][0]
                sql_stmt_qry=sql_stmt_qry.replace("'","''")
                updated_qry=f'''select SNOWFLAKE.CORTEX.COMPLETE('llama2-70b-chat',concat('<s>[INST]Replace the sql like to ilike if found in the SQL query between the tage <query> </query> and ensure the SQL query is a valid Snowflake query. 
                                                Only ouput the SQL Query and do not include the user prompt. Do not include details about the replacement .Do not provide any explaination about the modified query and output the modified query only without any detail .
                                                Do not output like The query is syntactically valid Snowflake SQL statement
                                                Some of the date based queries and prompts are as below:
                                                [/INST]
                                                For the prompt: Give me count of total calls in the month november 2023. 
                                                SQL Query: SELECT count(*) FROM STREAMLITAPPTABLE WHERE DATETIME = 2023-11-01 between 2023-11-30

                                                For the prompt : list the unique issues handled by the representative name starts with emma in the month November 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike emma% and datetime between 2023-11-01 and 2023-11-30;

                                                For the prompt : list the unique issues handled by the representative name starts with emma in the month November and December 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike emma% and datetime between 2023-11-01 and 2023-12-31;
                                                
                                                For the prompt : give me call details for the representative name like Ryan where the call sentiment is negative in the month November 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike Ryan% and AND CALLSENTIMENT = ''Negative'' and datetime between 2023-11-01 and 2023-11-30;
                                               
                                                [INST] Do not provide any explaination about the modified query and output the modified query only without any detail for the query found between <query> </query> tag. If you a. If you are unable to change the SQL ouput it as Select 1; . Do not include th query tags in output. Do not include the explanation about the ilike operator or the query output', '<query>','{sql_stmt_qry}','</query>  [/INST] Answer: Sure, I would be happy to help!')) as qry'''

                df_updated=session.sql(updated_qry).to_pandas()
                # print(f"updated qry -> {updated_qry}")
                # print(f"sql_stmt_qry  -> {sql_stmt_qry}")
                
                try:
                    
                    if 1==0:
                        pass
                    # ':' in df_updated['QRY'][0]:
                    #     print(f"df_updated['QRY'][0] -> {df_updated['QRY'][0]}")
                    #     run_qry=df_updated['QRY'][0].split(':')[1].strip()
                    #     print(f'run query in : -> {run_qry}')
                    #     if ';' in run_qry:
                    #         print(run_qry)
                    #         final_qry = run_qry.split(';')[0].strip()
                    #     else: final_qry=run_qry
                    else:
                        run_qry=df_updated['QRY'][0].split('\n')[0]
                        # print(f'run query in else -> {run_qry}')
                        if ';' in run_qry:
                            print(run_qry)
                            final_qry = run_qry.split(';')[0].strip()
                        else: final_qry=run_qry
                    
                    # print('-------------final full qyery------')
                    # print(final_qry)
                    # print('------------------------- markdown query split list')
                    # print(final_qry.split('```'))
                    # print('------------------------')
                    # st.write(final_qry)
                    for idx,qy in enumerate(final_qry.split('```')):
                        if 'SELECT' in qy:
                            # print("inside loop...")
                            # print(qy)
                            # print(f'The query which is getting executed is ->  {qy}')
                            pd_df=session.sql(qy).to_pandas()
                            
                            # print(qy)
                            break

                    # pd_df=session.sql(final_qry.split('```')[0]).to_pandas()
                    
                    st.dataframe(pd_df)

                    if '```' in final_qry:
                        st.code(final_qry.split('```')[0])
                    else: 
                        st.code(final_qry)
                    # with st.form("Execute Query",border=False):
                    #     input= st.chat_input("Update your query ",key='EQ')
                    #     summarize_button = st.form_submit_button("Run")

                    # st.dataframe(get_df(st.session_state.messages[-1]["content"]))
                    message = {"role": "assistant", "content": pd_df}
                    st.session_state.messages.append(message)  
                except Exception as e:
                    st.write(f"Sorry invalid query to execute. Please change the prompt. Below is the query generated for your prompt.")
                    if '```' in final_qry:
                        st.code(final_qry.split('```'))
                    else: 
                        st.code(final_qry)






def cortex_analyst_chat(session):
    """Main function that handles chat interaction and responses from Cortex Analyst."""
    
    def get_analyst_response(messages: List[Dict]) -> Tuple[Dict, Optional[str]]:
        """Send chat history to the Cortex Analyst API and return the response."""
        request_body = {
            "messages": messages,
            "semantic_model_file": f"@{st.session_state.selected_semantic_model_path}",
        }

        resp = _snowflake.send_snow_api_request(
            "POST", API_ENDPOINT, {}, {}, request_body, None, API_TIMEOUT
        )

        parsed_content = json.loads(resp["content"])

        if resp["status"] < 400:
            return parsed_content, None
        else:
            error_msg = f"""
                🚨 An Analyst API error has occurred 🚨
                    * response code: `{resp['status']}`
                    * request-id: `{parsed_content['request_id']}`
                    * error code: `{parsed_content['error_code']}`
                    Message:
                    ```
                        {parsed_content['message']}
                    ```
            """
            return parsed_content, error_msg




    
    def read_yaml_file(yaml_path: str) -> str:
        """
        Lit le contenu d'un fichier YAML stocké dans un stage Snowflake.
    
        :param yaml_path: Le chemin du fichier YAML dans le stage Snowflake (format: <DATABASE>.<SCHEMA>.<STAGE>/<FILE-NAME>).
        :return: Le contenu du fichier YAML sous forme de chaîne de caractères.
        """
        session = get_active_session()
    
        # Extraire le nom du stage et le chemin du fichier
        stage_path = yaml_path.split("/")[0]  # "DATA_LAKE_DEV.COLIBRI.RAW_DATA"
        file_name = yaml_path.split("/")[1]   # "colibri_crm.yaml"
    
        # Extraire le nom du stage (dernier élément après le point)
        stage_name = stage_path.split(".")[-1]  # "RAW_DATA"
    
        # Construire le chemin complet du stage avec '@'
        full_stage_path = f"@{stage_name}"
    
        # Lire le contenu du fichier YAML
        query = f"SELECT $1 AS content FROM '{full_stage_path}/{file_name}'"
        result = session.sql(query).collect()
    
        if result:
            return result[0]["CONTENT"]
    
        return None
    
    
    
    
    def handle_user_inputs():
        """Handle user inputs from the chat interface."""
        user_input = st.chat_input("What is your question?")
        if user_input:
            process_user_input(user_input)
        elif st.session_state.active_suggestion is not None:
            suggestion = st.session_state.active_suggestion
            st.session_state.active_suggestion = None
            process_user_input(suggestion)

    def process_user_input(prompt: str):
        """Process user input and update the conversation history."""
        new_user_message = {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
        st.session_state.messages.append(new_user_message)
        with st.chat_message("user"):
            display_message(new_user_message["content"], len(st.session_state.messages) - 1)

        with st.chat_message("analyst"):
            with st.spinner("Waiting for Analyst's response..."):
                time.sleep(1)
                response, error_msg = get_analyst_response(st.session_state.messages)
                if error_msg is None:
                    analyst_message = {
                        "role": "analyst",
                        "content": response["message"]["content"],
                        "request_id": response["request_id"],
                    }
                    st.session_state.messages.append(analyst_message)
                else:
                    analyst_message = {
                        "role": "analyst",
                        "content": [{"type": "text", "text": error_msg}],
                        "request_id": response["request_id"],
                    }
                    st.session_state["fire_API_error_notify"] = True
                    st.session_state.messages.append(analyst_message)
                st.rerun()



    @st.cache_data(show_spinner=False)
    def get_query_exec_result(query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Execute the SQL query and convert the results to a pandas DataFrame.

        Args:
            query (str): The SQL query.

        Returns:
            Tuple[Optional[pd.DataFrame], Optional[str]]: The query results and the error message.
        """
        global session
        try:
            df = session.sql(query).to_pandas()
            return df, None
        except SnowparkSQLException as e:
            return None, str(e)


    
    def display_sql_query(sql: str, message_index: int):
        """
        Executes the SQL query and displays the results in form of data frame and charts.
        Also generates a natural language summary of the results using provide_insights.
        """
        # Display the SQL query
        with st.expander("SQL Query", expanded=False):
            st.code(sql, language="sql")

        # Display the results of the SQL query
        with st.expander("Results", expanded=True):
            with st.spinner("Running SQL..."):
                df, err_msg = get_query_exec_result(sql)
                if df is None:
                    st.error(f"Could not execute generated SQL query. Error: {err_msg}")
                    return

                if df.empty:
                    st.write("Query returned no data")
                    return

                # Show query results in two tabs
                data_tab, chart_tab = st.tabs(["Data 📄", "Chart 📈 "])
                with data_tab:
                    st.dataframe(df, use_container_width=True)

                with chart_tab:
                    display_charts_tab(df, message_index)
                    #pass

                # Generate insights if results are available
                if not df.empty:
                    pass

                    
                    # Convert the DataFrame to a string representation
                    #results_summary = df.to_string(index=False)

                    # Read the YAML file
                    #yaml_path = st.session_state.selected_semantic_model_path
                    #yaml_content = read_yaml_file(yaml_path)

                    # Generate insights based on the results and YAML
                    #insights = provide_insights("Quelles sont les tendances clés ?", results_summary, yaml_content=yaml_content)

                    # Display the insights
                    #st.markdown("---")  # Add a separator
                    #st.markdown("### Insights")
                    #st.markdown(insights   


    def display_charts_tab(df: pd.DataFrame, message_index: int) -> None:
        """
        Display the charts tab.

        Args:
            df (pd.DataFrame): The query results.
            message_index (int): The index of the message.
        """
        # There should be at least 2 columns to draw charts
        if len(df.columns) >= 2:
            all_cols_set = set(df.columns)
            col1, col2 = st.columns(2)
            x_col = col1.selectbox(
                "X axis", all_cols_set, key=f"x_col_select_{message_index}"
            )
            y_col = col2.selectbox(
                "Y axis",
                all_cols_set.difference({x_col}),
                key=f"y_col_select_{message_index}",
            )
            chart_type = st.selectbox(
                "Select chart type",
                options=["Line Chart 📈", "Bar Chart 📊"],
                key=f"chart_type_{message_index}",
            )      
            if chart_type == "Line Chart 📈":
                st.line_chart(df.set_index(x_col)[y_col])
            elif chart_type == "Bar Chart 📊":
                st.bar_chart(df.set_index(x_col)[y_col])
        else:
            st.write("At least 2 columns are required")

    

    def display_conversation():
        """Display the conversation history between the user and the assistant."""
        for idx, message in enumerate(st.session_state.messages):
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                display_message(content, idx)

    def display_message(content, message_index):
        """Display a single message content."""
        for item in content:
            if item["type"] == "text":
                st.markdown(item["text"])
            elif item["type"] == "suggestions":
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(
                        suggestion, key=f"suggestion_{message_index}_{suggestion_index}"
                    ):
                        st.session_state.active_suggestion = suggestion
            elif item["type"] == "sql":
                display_sql_query(item["statement"], message_index)

    def reset_session_state():
        """Reset important session state elements."""
        st.session_state.messages = []  # List to store conversation messages
        st.session_state.active_suggestion = None  # Currently selected suggestion

    def show_header_and_sidebar():
        """Display the header and sidebar of the app."""
        #st.title("Cortex Analyst")
        #st.markdown(
        #    "Welcome to Cortex Analyst! Type your questions below to interact with your data. "
        #)

        with st.sidebar:
            st.selectbox(
                "Selected semantic model:",
                AVAILABLE_SEMANTIC_MODELS_PATHS,
                format_func=lambda s: s.split("/")[-1],
                key="selected_semantic_model_path",
                on_change=reset_session_state,
            )
            st.divider()
            _, btn_container, _ = st.columns([2, 6, 2])
            if btn_container.button("Clear Chat History", use_container_width=True):
                reset_session_state()

    # Initialize session state
    if "messages" not in st.session_state:
        reset_session_state()
    show_header_and_sidebar()
    
    #if len(st.session_state.messages) == 0:
    #    process_user_input("What questions can I ask?")
    
    display_conversation()
    handle_user_inputs()


   










# Logique pour chaque option choisie
if choose_side_opt == "About App":
    #st.subheader("Bienvenue sur Colibri Insight Analyzer ❄️")
    st.subheader("À propos de l'application")
    # Place ton code spécifique pour "About App" ici
    appinfo()  # Afficher le contenu du README.md ou de la description


elif choose_side_opt == "Data":
    st.subheader("Data Overview")
    data_overview()  # Obtenir une vision d'ensemble sur les données


elif choose_side_opt == "Data Exploration":
    st.subheader("Data Exploration")
    # Place ton code spécifique pour "Audio Analytics" ici
    st.write("L'analyse exploratoire permet de traiter et d'analyser des données  pour obtenir des informations utiles.")
    # analytics_main(session=session)  # Décommente et adapte cette ligne

elif choose_side_opt == "Colibri Insights Analytics":
    st.subheader("L'analytics ")
    # Place ton code spécifique pour "Resource Allocation Efficiency" ici
    st.write("Cette section analyse permet.")
    # res_main(session=session)  # Décommente et adapte cette ligne

elif choose_side_opt == "Chatbot":
    st.subheader("Chatbot")
    # Place ton code spécifique pour "Chatbot" ici
    #st.write("Interagissez avec le chatbot pour obtenir des réponses.")
    # chatbot(session=session)  # Décommente et adapte cette ligne
    #chatbot(session=session)

elif choose_side_opt == "Cortex Analyst":
    # st.subheader("Cortex Analyst")
    # Place ton code spécifique pour "Text2SQLBot" ici
    #st.write("Posez des questions en texte libre et obtenez des requêtes SQL générées.")
    #chatbotSQL(session)  # Décommente et adapte cette ligne


    st.subheader("Interagissez avec les données Colibri Snowflake")

    with st.expander("ℹ️ À propos de cet assistant", expanded=True):
        st.markdown(
    """
    Ce chatbot utilise un modèle de langage avancé (LLM) pour générer des requêtes SQL en fonction de vos questions métier.

    ⚠️ Il **accède aux données internes de l'entreprise** sur Snowflake pour produire des résultats personnalisés et pertinents.  
    Il comprend le contexte métier spécifique et interagit avec les données structurées pour fournir des réponses basées sur les informations internes.

    ✅ Utile pour des questions **métier spécifiques**.  
    ❌ Pas adapté pour des questions générales qui ne sont pas liées aux données internes de l'entreprise.
    """)
    cortex_analyst_chat(session)



