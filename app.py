import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Visualizacion de Grafo con PyVis y Streamlit")

# -----------------------------
# Cargar CSV
# -----------------------------

nodes_df = pd.read_csv("nodes.csv")
edges_df = pd.read_csv("edges.csv")

# -----------------------------
# Cargar opciones del grafo
# -----------------------------

with open("graph_options.json","r") as f:
    options = json.load(f)

# -----------------------------
# Filtro de relaciones
# -----------------------------

st.sidebar.header("Filtros")

relaciones = st.sidebar.multiselect(
    "Tipo de relación",
    edges_df["relation"].unique(),
    default=list(edges_df["relation"].unique())
)

edges_filtered = edges_df[
    edges_df["relation"].isin(relaciones)
]

# -----------------------------
# Crear grafo
# -----------------------------

G = nx.DiGraph()

# agregar nodos
for _, row in nodes_df.iterrows():

    G.add_node(
        row["id"],
        label=row["label"],
        type=row["type"],
        criticality=row["criticality"]
    )

# agregar edges
for _, row in edges_filtered.iterrows():

    G.add_edge(
        row["source"],
        row["target"],
        relation=row["relation"]
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
# colores por tipo
# -----------------------------

color_map = {
    "process": "#ff6b6b",
    "table": "#4dabf7",
    "column": "#51cf66",
    "rule": "#fab005"
}

size_map = {
    "process": 35,
    "table": 30,
    "column": 25,
    "rule": 20
}

# -----------------------------
# agregar nodos
# -----------------------------

for node, data in G.nodes(data=True):

    node_type = data["type"]

    net.add_node(
        node,
        label=data["label"],
        color=color_map.get(node_type,"gray"),
        size=size_map.get(node_type,20),
        title=f"""
        Tipo: {data['type']} <br>
        Criticalidad: {data['criticality']}
        """
    )

# -----------------------------
# agregar edges
# -----------------------------

for source, target, data in G.edges(data=True):

    net.add_edge(
        source,
        target,
        label=data["relation"]
    )


# -----------------------------
# mostrar grafo
# -----------------------------

net.save_graph("graph.html")

with open("graph.html","r",encoding="utf-8") as f:
    html = f.read()

components.html(html,height=750)