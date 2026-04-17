import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import json
import streamlit.components.v1 as components
import os
import plotly.graph_objects as go
from scipy.spatial.distance import pdist, squareform
import numpy as np


REQUIRED_NODE_COLUMNS = {"id", "label"}
EDGE_SOURCE_ALIASES = ["src", "source"]
EDGE_TARGET_ALIASES = ["dst", "target"]
DEFAULT_NODE_COLOR = "#808080"


# Obtener lista de grafos disponibles
data_dir = "./data"
if os.path.exists(data_dir):
    available_graphs = []
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path):
            nodes_path = os.path.join(item_path, "nodes.csv")
            edges_path = os.path.join(item_path, "edges.csv")
            if os.path.exists(nodes_path) and os.path.exists(edges_path):
                available_graphs.append(item)
    available_graphs.sort()
else:
    available_graphs = []

if not available_graphs:
    st.error("No se encontraron grafos válidos en la carpeta data. Cada grafo debe tener una subcarpeta con nodes.csv y edges.csv.")
    st.stop()


def find_first_existing_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def load_csv_or_stop(path):
    try:
        return pd.read_csv(path, sep=';')
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


st.set_page_config(
    layout="wide",
    page_title="Visualización de Grafos",
    page_icon="🌐"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .description {
        font-size: 1.2em;
        color: #34495e;
        text-align: center;
        margin-bottom: 30px;
        line-height: 1.6;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #ecf0f1;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🌐 Visualización de Grafos Interactivos</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="description">
    Explora relaciones complejas entre entidades a través de una visualización de grafo interactiva.
    Utiliza los filtros en la barra lateral para personalizar la vista y descubrir conexiones ocultas.
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Seleccionar grafo
# -----------------------------

selected_graph = st.sidebar.selectbox("Seleccionar grafo", available_graphs, index=0)

# Seleccionar tipo de visualización
visualization_type = st.sidebar.radio("Tipo de visualización", ["2D (PyVis)", "3D (Plotly)"], index=0)

# -----------------------------
# Cargar CSV del grafo seleccionado
# -----------------------------

nodes_df = load_csv_or_stop(f"./data/{selected_graph}/nodes.csv")
edges_df = load_csv_or_stop(f"./data/{selected_graph}/edges.csv")

has_type_column = "type" in nodes_df.columns

nodes_df = prepare_nodes(nodes_df)
edges_df = prepare_edges(edges_df)

# -----------------------------
# Preparar colores y tamaños
# -----------------------------

if has_type_column:
    unique_types = sorted(nodes_df['type'].dropna().unique())
    color_palette = [
        "#e74c3c", "#3498db", "#2ecc71", "#ff6b6b", "#4dabf7", "#51cf66", "#fab005",
        "#fd7e14", "#6f42c1", "#20c997", "#dc3545", "#ffc107", "#17a2b8", "#28a745",
        "#007bff", "#6c757d", "#343a40", "#f8f9fa"
    ]
    color_map = {type_: color_palette[i % len(color_palette)] for i, type_ in enumerate(unique_types)}
    default_node_size = 30
    size_map = {type_: default_node_size for type_ in unique_types}
else:
    color_map = {}
    size_map = {}
    unique_types = []

# -----------------------------
# Configuración del tooltip
# -----------------------------

tooltip_options = [col for col in nodes_df.columns if col not in ['id', 'label']]
selected_tooltip_fields = st.sidebar.multiselect(
    "Campos a mostrar en el tooltip",
    tooltip_options,
    default=['type', 'description'] if 'type' in tooltip_options and 'description' in tooltip_options else tooltip_options[:2]
)

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

st.sidebar.header("🎛️ Filtros y Configuración")

relationship_values = sorted(
    [str(value) for value in edges_df["relationship"].dropna().unique()]
)

if relationship_values:
    relaciones = st.sidebar.multiselect(
        "Tipo de relación",
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
        category=str(row.get("category", "")),
        description=str(row.get("description", "")),
        power_level=str(row.get("power_level", "")),
        origin=str(row.get("origin", "")),
        status=str(row.get("status", "")),
        tags=str(row.get("tags", "")),
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
    "Límite de nodos a mostrar",
    min_value=0,
    max_value=5000,
    value=min(500, G.number_of_nodes()),
    step=50,
)

# -----------------------------
# Personalización de colores
# -----------------------------

if has_type_column:
    st.sidebar.header("🎨 Personalización de Colores")
    for type_ in unique_types:
        color_map[type_] = st.sidebar.color_picker(f"Color para {type_}", value=color_map[type_])

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

    # Construir el tooltip dinámicamente
    title_lines = [f"Label: {node_label}"]
    for field in selected_tooltip_fields:
        value = str(data.get(field, ""))
        if value.strip():  # Solo incluir si tiene valor
            title_lines.append(f"{field.capitalize()}: {value}")
    title = "\n".join(title_lines)

    net.add_node(
        node,
        label=node_label,
        color=node_color,
        size=node_size,
        title=title
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
# Generar visualización 3D con Plotly
# -----------------------------

def generate_3d_graph(G, color_map, size_map, DEFAULT_NODE_COLOR, has_type_column):
    # Usar layout con posiciones 3D
    pos_3d = {}
    
    # Aplicar un layout spring 3D
    pos_2d = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Asignar coordenadas Z aleatorias
    np.random.seed(42)
    for node in G.nodes():
        pos_3d[node] = [pos_2d[node][0], pos_2d[node][1], np.random.uniform(-1, 1)]
    
    # Extraer coordenadas
    x_coords = [pos_3d[node][0] for node in G.nodes()]
    y_coords = [pos_3d[node][1] for node in G.nodes()]
    z_coords = [pos_3d[node][2] for node in G.nodes()]
    
    # Crear aristas
    edge_x, edge_y, edge_z = [], [], []
    for source, target in G.edges():
        edge_x.extend([pos_3d[source][0], pos_3d[target][0], None])
        edge_y.extend([pos_3d[source][1], pos_3d[target][1], None])
        edge_z.extend([pos_3d[source][2], pos_3d[target][2], None])
    
    # Extraer información de nodos
    node_labels = [str(G.nodes[node].get("label", node)) for node in G.nodes()]
    node_types = [str(G.nodes[node].get("type", "unknown")) for node in G.nodes()]
    node_colors = [
        color_map.get(node_type, DEFAULT_NODE_COLOR) if has_type_column else DEFAULT_NODE_COLOR
        for node_type in node_types
    ]
    node_sizes = [safe_node_size(G.nodes[node], size_map) for node in G.nodes()]
    
    # Crear figura
    fig = go.Figure(data=[
        go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode="lines",
            line=dict(color="rgba(125,125,125,0.2)", width=1),
            hoverinfo="none",
            name=""
        ),
        go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode="markers+text",
            text=node_labels,
            textposition="top center",
            hovertext=node_labels,
            hoverinfo="text",
            marker=dict(
                size=8,
                color=node_colors,
                line=dict(color="white", width=1),
                opacity=0.8
            ),
            name="Nodos"
        )
    ])
    
    fig.update_layout(
        title="Visualización 3D del Grafo",
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            zaxis=dict(showgrid=False, zeroline=False),
        ),
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=40),
        height=750
    )
    
    return fig


# Generar gráfico 3D
if visualization_type == "3D (Plotly)":
    fig_3d = generate_3d_graph(G, color_map, size_map, DEFAULT_NODE_COLOR, has_type_column)

# -----------------------------
# mostrar grafo
# ----------------------------- 

if visualization_type == "2D (PyVis)":
    net.save_graph("graph.html")
    with open("graph.html","r",encoding="utf-8") as f:
        html = f.read()
    components.html(html,height=750)
else:  # 3D
    st.plotly_chart(fig_3d, width='stretch')