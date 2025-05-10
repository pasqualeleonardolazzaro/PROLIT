import streamlit as st
import os
import subprocess
import webbrowser
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from KEY import MY_KEY

# Titolo
st.set_page_config(page_title="PROLIT", layout="wide")

# Sidebar per navigazione
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main", "Provenance Chat"])

# Funzione per inizializzare il chain
@st.cache_resource
def init_graph_chain():
    graph = Neo4jGraph(
        url="bolt://localhost:7687",
        username="neo4j",
        password="adminadmin"
    )

    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template="""
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about data provenance.
Convert the user's question based on the schema.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

If no data is returned, do not attempt to answer the question.
Only respond to questions that require you to construct a Cypher statement.
Do not include any explanations or apologies in your responses.

Schema: {schema}
Question: {question}
"""
    )

    llm = ChatGroq(
        model_name="llama3-70b-8192",
        groq_api_key= MY_KEY,
        temperature=0
    )

    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        cypher_prompt=cypher_prompt,
        verbose=True
    )
    return chain

# Pagina principale
if page == "Main":
    st.title("PROLIT - GUI")

    @st.cache_data
    def get_files():
        datasets = os.listdir("datasets") if os.path.exists("datasets") else []
        pipelines = os.listdir("pipelines") if os.path.exists("pipelines") else []
        return datasets, pipelines

    datasets, pipelines = get_files()

    dataset = st.selectbox("Choose a dataset", datasets)
    pipeline = st.selectbox("Choose a pipeline", pipelines)
    frac = st.text_input("Enter the dataset sampling frac value", "1.0")

    granularity_labels = ["Sketch", "Derivation", "Full", "Only_columns"]
    granularity_mapping = {"Sketch": 1, "Derivation": 2, "Full": 3, "Only_columns": 4}
    granularity_label = st.selectbox("Select granularity level", granularity_labels)
    granularity = granularity_mapping[granularity_label]

    if st.button("Run PROLIT"):
        command = f"python prolit_run.py --dataset datasets/{dataset} --pipeline pipelines/{pipeline} --frac {frac} --granularity_level {granularity}"
        with st.spinner("Running PROLIT..."):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("✅ Execution succeeded")
            else:
                st.error("❌ Execution failed")

    if st.button("Open Neo4j Browser"):
        webbrowser.open("http://localhost:7474/browser/")

# Pagina chat stile ChatGPT
elif page == "Provenance Chat":
    st.title("🧠 Chat with the Graph")
    cypher_chain = init_graph_chain()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("Hi! Ask me anything about your Provenance Graph 🧠")

    question = st.chat_input("Ask a question...")
    new_exchange = None

    if question:
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    response = cypher_chain.invoke({"query": question})
                    result = response["result"]
                    st.markdown(result)
                    new_exchange = (question, result)
                except Exception as e:
                    st.error(f"Error: {e}")

    for i, (q, r) in enumerate(st.session_state.chat_history):
        with st.chat_message("user", avatar="👤"):
            st.markdown(q)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(r)

    if new_exchange:
        st.session_state.chat_history.append(new_exchange)
