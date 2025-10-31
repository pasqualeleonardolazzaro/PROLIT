# streamlit_app.py
import os
import sys
import shutil
import traceback
import subprocess
from pathlib import Path
import streamlit as st

# ====================== CONFIG BASE ======================
st.set_page_config(page_title="PROLIT Console", layout="wide")

BASE_DIR = Path(__file__).parent.resolve()
os.chdir(BASE_DIR)

EXTRACTED = BASE_DIR / "extracted_code.py"
EXTRACTED_BAK = BASE_DIR / "extracted_code_llm.py"  # backup del codice generato dall'LLM

# Stato persistente Streamlit
ss = st.session_state
ss.setdefault("last_rc", None)
ss.setdefault("stdout", "")
ss.setdefault("stderr", "")
ss.setdefault("use_manual", True)     # di default usa il codice manuale se presente
ss.setdefault("reload_nonce", 0)      # cambia per forzare reload editor

# ====================== NAVIGAZIONE ======================
st.sidebar.title("PROLIT")
page = st.sidebar.radio("Navigazione", ["Run PROLIT", "Graph Chat", "Provenance Explorer"], index=0)
st.sidebar.caption(f"Working dir: {BASE_DIR}")

# ====================== HELPERS COMUNI ======================
def ensure_backup():
    if EXTRACTED.exists() and not EXTRACTED_BAK.exists():
        shutil.copy2(EXTRACTED, EXTRACTED_BAK)

def save_user_code(text: str):
    ensure_backup()
    EXTRACTED.write_text(text, encoding="utf-8")

def run_prolit(dataset: str, pipeline: str, frac: str, gran_level: int, use_manual: bool):
    """Esegue prolit_run.py come da CLI (get_args() lato script gestisce gli argomenti)."""
    cmd = [
        sys.executable, "prolit_run.py",
        "--dataset", dataset,
        "--pipeline", pipeline,
        "--frac", str(frac),
        "--granularity_level", str(gran_level),
    ]
    if use_manual:
        cmd.append("--use_manual_code")  # richiede la patch in get_args() di prolit_run.py

    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    ss.last_rc = proc.returncode
    ss.stdout = proc.stdout or ""
    ss.stderr = proc.stderr or ""
    return cmd, proc.returncode

# ====================== PAGINA: RUN PROLIT ======================
if page == "Run PROLIT":
    st.title("Run PROLIT")

    # ---- Scansione cartelle per menu a tendina ----
    datasets_dir = BASE_DIR / "datasets"
    pipelines_dir = BASE_DIR / "pipelines"

    dataset_options = sorted(
        [str(p.relative_to(BASE_DIR)).replace("\\", "/") for p in datasets_dir.glob("*.csv")]
    ) if datasets_dir.exists() else []
    pipeline_options = sorted(
        [str(p.relative_to(BASE_DIR)).replace("\\", "/") for p in pipelines_dir.glob("*.py")]
    ) if pipelines_dir.exists() else []

    # fallback se vuoti
    if not dataset_options:
        dataset_options = ["datasets/generated_dataset.csv"]
    if not pipeline_options:
        pipeline_options = ["pipelines/orders_pipeline.py"]

    # ---- Granularity con etichette umane ----
    granularity_labels = ["Sketch", "Only columns", "Detailed", "Full"]
    granularity_map = {"Sketch": 1, "Only columns": 2, "Detailed": 3, "Full": 4}
    default_gran_label = "Only columns"

    colA, colB = st.columns(2)
    with colA:
        dataset = st.selectbox(
            "Dataset",
            dataset_options,
            index=dataset_options.index("datasets/generated_dataset.csv")
            if "datasets/generated_dataset.csv" in dataset_options else 0,
        )
        frac = st.text_input("Frac", "1")
    with colB:
        pipeline = st.selectbox(
            "Pipeline",
            pipeline_options,
            index=pipeline_options.index("pipelines/orders_pipeline.py")
            if "pipelines/orders_pipeline.py" in pipeline_options else 0,
        )
        granularity_label = st.selectbox(
            "Granularity level",
            granularity_labels,
            index=granularity_labels.index(default_gran_label),
        )
        granularity = granularity_map[granularity_label]

    st.divider()
    left, right = st.columns([2, 1])
    with left:
        st.checkbox(
            "Usa codice manuale (extracted_code.py)",
            value=ss.use_manual,
            key="use_manual",
            help="Se attivo, passa --use_manual_code a prolit_run.py (gestito da get_args()).",
        )
    with right:
        if EXTRACTED_BAK.exists():
            if st.button("Ripristina codice LLM"):
                shutil.copy2(EXTRACTED_BAK, EXTRACTED)
                st.success("Ripristinato extracted_code.py dal backup LLM.")
                ss.reload_nonce += 1
                st.rerun()

    # ---- Editor nascosto finché non lo espandi ----
    with st.expander("Editor avanzato: `extracted_code.py` (clicca per espandere)", expanded=False):
        # ricarica SEMPRE il contenuto da file a ogni rerun
        if EXTRACTED.exists():
            try:
                mtime_ns = EXTRACTED.stat().st_mtime_ns
            except Exception:
                mtime_ns = 0
            editor_key = f"editor_{mtime_ns}_{ss.reload_nonce}"
            try:
                file_text = EXTRACTED.read_text(encoding="utf-8")
            except Exception:
                file_text = ""
        else:
            mtime_ns = 0
            editor_key = f"editor_{mtime_ns}_{ss.reload_nonce}"
            file_text = ""

        edited = st.text_area(
            "Contenuto file",
            value=file_text,
            height=350,
            key=editor_key,  # la chiave cambia quando cambia mtime o nonce -> forzato reload
        )

        ecol1, ecol2, ecol3 = st.columns([1,1,2])
        if ecol1.button("💾 Salva"):
            save_user_code(edited)
            st.success("Salvato `extracted_code.py`.")
            ss.reload_nonce += 1
            st.rerun()

        if ecol2.button("↻ Ricarica da file"):
            ss.reload_nonce += 1
            st.rerun()

        ecol3.caption(f"Ultima modifica: {mtime_ns}")

    # ---- Esecuzione ----
    run_clicked = st.button("▶️ Run PROLIT", type="primary")

    if run_clicked:
        # forza anche il reload editor al prossimo rerun
        ss.reload_nonce += 1

        # se usi manuale, salva PRIMA di eseguire (se hai l'editor aperto e modifiche non salvate)
        # qui non possiamo leggere il valore del text_area senza chiave fissa;
        # quindi confidiamo che l'utente abbia premuto "Salva".
        # (scelta intenzionale: vogliamo reload da file a ogni run)
        with st.status("Esecuzione in corso…", expanded=True) as status:
            cmd, rc = run_prolit(dataset, pipeline, frac, granularity, ss.use_manual)
            st.code(" ".join(cmd), language="bash")

            # Fallback automatico se non hai ancora patchato get_args() con --use_manual_code
            if rc != 0 and ss.use_manual and ("unrecognized arguments" in ss.stderr.lower()):
                status.update(
                    label="⚠️ `prolit_run.py` non supporta --use_manual_code (patch get_args() mancante). Rilancio senza flag…",
                    state="running",
                )
                cmd2 = [
                    sys.executable, "prolit_run.py",
                    "--dataset", dataset,
                    "--pipeline", pipeline,
                    "--frac", str(frac),
                    "--granularity_level", str(granularity),
                ]
                proc2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=BASE_DIR)
                ss.last_rc = proc2.returncode
                ss.stdout = proc2.stdout or ""
                ss.stderr = proc2.stderr or ""
                st.info("Rilanciato senza flag; verifica che `prolit_run.py` importi/usi `extracted_code.py` manuale.")

            st.subheader("STDOUT")
            st.code(ss.stdout or "(vuoto)")
            st.subheader("STDERR")
            st.code(ss.stderr or "(vuoto)")

            if ss.last_rc == 0:
                status.update(label="✅ Execution succeeded", state="complete")
            else:
                status.update(label=f"❌ Exit code {ss.last_rc}", state="error")
                st.error("Se necessario, espandi l'editor, salva le modifiche al file e rilancia.")

# ====================== PAGINA: GRAPH CHAT ======================
elif page == "Graph Chat":
    st.title("Graph Chat (Neo4j)")

    # Credenziali da env/secrets
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    st.caption(f"DB: {NEO4J_DATABASE} @ {NEO4J_URI}")

    try:
        from langchain_community.graphs import Neo4jGraph
        graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE,
        )
    except Exception as e:
        st.error(f"Connessione Neo4j fallita: {e}")
        st.stop()

    st.write("Inserisci una query Cypher (es.: `MATCH (n) RETURN n LIMIT 5`).")
    cypher = st.text_area("Cypher", "MATCH (n) RETURN n LIMIT 5", height=120)

    if st.button("Esegui query"):
        try:
            res = graph.query(cypher)
            if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict):
                import pandas as pd
                st.dataframe(pd.DataFrame(res), use_container_width=True)
            else:
                st.write(res)
            st.success("Query eseguita.")
        except Exception as e:
            st.error(f"Errore: {e}")
            st.code(traceback.format_exc())

# ====================== PAGINA: PROVENANCE EXPLORER ======================
elif page == "Provenance Explorer":
    st.title("Provenance Explorer")

    st.write("Apri il Neo4j Browser per esplorare il grafo di provenance:")
    # link cliccabile
    st.markdown("[🌐 Apri Neo4j Browser](http://localhost:7474/browser/)")

    # pulsante che apre in nuova scheda
    if st.button("Apri Neo4j Browser"):
        st.components.v1.html(
            "<script>window.open('http://localhost:7474/browser/', '_blank');</script>",
            height=0,
            width=0,
        )
