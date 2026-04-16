import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
import streamlit.components.v1 as components


REQUIRED_NODE_COLUMNS = {"id", "label"}
EDGE_SOURCE_ALIASES = ["src", "source"]
EDGE_TARGET_ALIASES = ["dst", "target"]
DEFAULT_NODE_COLOR = "#808080"


def find_first_existing_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def load_csv_or_stop(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"No se encontro el archivo requerido: {path}")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error(f"El archivo esta vacio: {path}")
        st.stop()
    except Exception as exc:
        st.error(f"No se pudo leer {path}: {exc}")
        st.stop()


def prepare_nodes(df):
    missing = REQUIRED_NODE_COLUMNS - set(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        st.error(f"nodes.csv no tiene columnas obligatorias: {missing_text}")
        st.stop()

    nodes = df.copy()

    if "type" not in nodes.columns:
        nodes["type"] = "unknown"

    if "size" in nodes.columns:
        nodes["size"] = pd.to_numeric(nodes["size"], errors="coerce")
    else:
        nodes["size"] = pd.NA

    return nodes


def prepare_edges(df):
    source_column = find_first_existing_column(df, EDGE_SOURCE_ALIASES)
    target_column = find_first_existing_column(df, EDGE_TARGET_ALIASES)

    if source_column is None or target_column is None:
        st.error(
            "edges.csv debe tener columnas obligatorias src y dst "
            "(tambien se aceptan source y target por compatibilidad)."
        )
        st.stop()

    edges = df.copy().rename(columns={source_column: "src", target_column: "dst"})

    if "relationship" not in edges.columns:
        if "relation" in edges.columns:
            edges = edges.rename(columns={"relation": "relationship"})
        else:
            edges["relationship"] = "related_to"

    return edges


def safe_node_size(node_data, default_by_type, default_size=20):
    raw_size = node_data.get("size")
    parsed_size = pd.to_numeric(raw_size, errors="coerce")
    if pd.notna(parsed_size):
        return int(max(10, min(80, parsed_size)))

    node_type = str(node_data.get("type", "unknown"))
    return default_by_type.get(node_type, default_size)


st.set_page_config(layout="wide")

st.title("Visualizacion de Grafo con PyVis y Streamlit")

# -----------------------------
# Cargar CSV
# -----------------------------

nodes_df = load_csv_or_stop("./data/nodes.csv")
edges_df = load_csv_or_stop("./data/edges.csv")

has_type_column = "type" in nodes_df.columns

nodes_df = prepare_nodes(nodes_df)
edges_df = prepare_edges(edges_df)

# -----------------------------
# Cargar opciones del grafo
# -----------------------------

try:
    with open("graph_options.json", "r", encoding="utf-8") as f:
        options = json.load(f)
except Exception as exc:
    st.error(f"No se pudo leer graph_options.json: {exc}")
    st.stop()

# -----------------------------
# Filtro de relaciones
# -----------------------------

st.sidebar.header("Filtros")

relationship_values = sorted(
    [str(value) for value in edges_df["relationship"].dropna().unique()]
)

if relationship_values:
    relaciones = st.sidebar.multiselect(
        "Tipo de relacion",
        relationship_values,
        default=relationship_values,
    )
    edges_filtered = edges_df[edges_df["relationship"].astype(str).isin(relaciones)]
else:
    st.sidebar.info("No hay relaciones para filtrar")
    edges_filtered = edges_df.copy()

# -----------------------------
# Crear grafo
# -----------------------------

G = nx.DiGraph()

# agregar nodos
invalid_nodes = 0
for _, row in nodes_df.iterrows():
    node_id = row.get("id")
    node_label = row.get("label")

    if pd.isna(node_id) or pd.isna(node_label):
        invalid_nodes += 1
        continue

    G.add_node(
        str(node_id),
        label=str(node_label),
        type=str(row.get("type", "unknown")),
        criticality=str(row.get("criticality", "n/a")),
        size=row.get("size", pd.NA),
    )

# agregar edges
invalid_edges = 0
for _, row in edges_filtered.iterrows():
    source = row.get("src")
    target = row.get("dst")

    if pd.isna(source) or pd.isna(target):
        invalid_edges += 1
        continue

    G.add_edge(
        str(source),
        str(target),
        relationship=str(row.get("relationship", "related_to")),
    )

if invalid_nodes > 0:
    st.warning(f"Se omitieron {invalid_nodes} nodos por id/label faltante")

if invalid_edges > 0:
    st.warning(f"Se omitieron {invalid_edges} aristas por src/dst faltante")

# -----------------------------
# Limitar grafo antes de renderizar
# -----------------------------

MAX_NODES = st.sidebar.number_input(
    "Limite de nodos a mostrar",
    min_value=0,
    max_value=5000,
    value=min(500, G.number_of_nodes()),
    step=50,
)

original_edges = G.number_of_edges()

if original_edges == 0:
    st.warning(
        "El grafo no tiene aristas con los filtros actuales. "
        "Prueba ajustar el filtro de relaciones."
    )

if G.number_of_nodes() > MAX_NODES:
    # Priorizar nodos conectados y completar con aislados solo si hace falta.
    nodes_with_edges = [node for node in G.nodes() if G.degree(node) > 0]
    isolated_nodes = [node for node in G.nodes() if G.degree(node) == 0]

    limited_nodes = nodes_with_edges[:MAX_NODES]
    remaining_capacity = MAX_NODES - len(limited_nodes)
    if remaining_capacity > 0:
        limited_nodes.extend(isolated_nodes[:remaining_capacity])

    G = G.subgraph(limited_nodes).copy()
    st.info(
        f"Grafo limitado a {MAX_NODES} nodos para mejor rendimiento "
        f"({G.number_of_nodes()} nodos, {G.number_of_edges()} aristas)."
    )

# -----------------------------
# Visualización PyVis
# -----------------------------

net = Network(
    height="750px",
    width="100%",
    directed=True
)

net.set_options(json.dumps(options))

# -----------------------------
# tamanos por tipo
# -----------------------------

color_map = {
    "data_system": "#e74c3c",
    "object": "#3498db",
    "field": "#2ecc71",
    "process": "#ff6b6b",
    "table": "#4dabf7",
    "column": "#51cf66",
    "rule": "#fab005",
}

size_map = {
    "data_system": 40,
    "object": 32,
    "field": 24,
    "process": 35,
    "table": 30,
    "column": 25,
    "rule": 20
}

if has_type_column:
    present_types = {str(node_data.get("type", "unknown")) for _, node_data in G.nodes(data=True)}
    unmapped_types = sorted(node_type for node_type in present_types if node_type not in color_map)
    if unmapped_types:
        st.warning(
            "Hay tipos de nodo sin color definido: "
            f"{', '.join(unmapped_types)}. Se usara {DEFAULT_NODE_COLOR} para esos casos."
        )

# -----------------------------
# agregar nodos
# -----------------------------

for node, data in G.nodes(data=True):

    node_label = str(data.get("label", node))
    node_type = str(data.get("type", "unknown"))
    node_criticality = str(data.get("criticality", "n/a"))
    node_size = safe_node_size(data, size_map)
    node_color = (
        color_map.get(node_type, DEFAULT_NODE_COLOR)
        if has_type_column
        else DEFAULT_NODE_COLOR
    )

    net.add_node(
        node,
        label=node_label,
        color=node_color,
        size=node_size,
        title=f"""
        Label: {node_label} <br>
        Tipo: {node_type} <br>
        Criticalidad: {node_criticality}
        """
    )

# -----------------------------
# agregar edges
# -----------------------------

for source, target, data in G.edges(data=True):

    net.add_edge(
        source,
        target,
        title=str(data.get("relationship", "related_to")),
    )


# -----------------------------
# mostrar grafo
# -----------------------------

net.save_graph("graph.html")

with open("graph.html","r",encoding="utf-8") as f:
    html = f.read()

components.html(html,height=750)