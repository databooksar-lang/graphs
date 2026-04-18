# Visualización de Grafos

Este proyecto ofrece dos formas de visualizar grafos interactivos según tu entorno de trabajo:

- **Streamlit** (local o en servidor)
- **Google Colab** (basado en Jupyter Notebook)

## 📋 Requisitos generales

```
networkx>=3.6.1
pandas>=1.0.0
plotly>=5.0.0
```

---

## 🚀 Opción 1: Streamlit (Local)

Para ejecutar la aplicación localmente usando Streamlit.

### Instalación

```bash
# Clonar o descargar el repositorio
cd graphs

# Instalar dependencias
pip install -r requirements.txt
```

### Estructura de datos

La carpeta `data/` debe contener subcarpetas para cada grafo:

```
data/
├── grafo1/
│   ├── nodes.csv
│   └── edges.csv
├── grafo2/
│   ├── nodes.csv
│   └── edges.csv
└── ...
```

### Archivos CSV

**nodes.csv**:
```
id;label;type;category;description;power_level;origin;status;tags
N1;Nodo1;Tipo1;Categoría1;Descripción;10;Origen;activo;"tag1;tag2"
```

**edges.csv**:
```
src;dst;relationship
N1;N2;relación1
```

> **Nota**: Los archivos deben estar delimitados por `;` (punto y coma)

### Ejecución

```bash
streamlit run app.py
```

Luego abre tu navegador en `http://localhost:8501`

### Características

✅ Visualización 2D interactiva (PyVis)  
✅ Visualización 3D interactiva (Plotly)  
✅ Selección de múltiples grafos  
✅ Filtrado de relaciones  
✅ Personalización de colores por tipo de nodo  
✅ Tooltips configurables  
✅ Limitación dinámica de nodos  

---

## 🔥 Opción 2: Google Colab

Para ejecutar en Google Colab sin necesidad de instalación local.

### Pasos

1. **Abre Google Colab**: https://colab.research.google.com

2. **Carga el notebook**:
   - Descarga `graphs_colab.ipynb` de este repositorio
   - O crea un nuevo notebook en Colab y copia el contenido

3. **Monta Google Drive** (opcional):
   - Si tus datos están en Drive, el notebook instalará automáticamente la extensión
   - Celda 2 monta tu Drive en `/content/drive`

4. **Configura la ruta de datos**:
   - En la celda 4, actualiza `DATA_DIR` según tu estructura
   - Ejemplo para Drive: `'/content/drive/MyDrive/graphs/data'`
   - Ejemplo local: `'./data'`

5. **Ejecuta las celdas en orden**

### Estructura en Colab

Si usas Google Drive:
```
My Drive/
└── graphs/
    └── data/
        ├── grafo1/
        │   ├── nodes.csv
        │   └── edges.csv
        └── grafo2/
            ├── nodes.csv
            └── edges.csv
```

### Características en Colab

✅ Visualización 2D interactiva  
✅ Visualización 3D interactiva  
✅ Interfaz con widgets interactivos  
✅ Carga automática de grafos disponibles  
✅ Sin configuración server requerida  
✅ Compatible con archivos en Google Drive  

---

## 📊 Formato de datos

### nodes.csv (obligatorio)

Columnas requeridas:
- `id`: identificador único
- `label`: nombre mostrado

Columnas opcionales (se mostrarán en tooltips):
- `type`: clasificación del nodo
- `category`: categoría
- `description`: descripción
- Cualquier otro campo personalizado

### edges.csv (obligatorio)

Columnas requeridas (soporta aliases):
- `src` o `source`: nodo origen
- `dst` o `target`: nodo destino

Columnas opcionales:
- `relationship`: tipo de relación

---

## 🎨 Personalización

### En Streamlit

- **Colores**: Selector interactivo en la sidebar para cada tipo de nodo
- **Tooltips**: Elige qué campos mostrar en la ventana emergente
- **Filtros**: Filtra por tipo de relación
- **Visualización**: Cambia entre 2D y 3D en tiempo real

### En Colab

- **Colores**: Se asignan automáticamente, puedes modificar `generate_color_map()`
- **Visualización**: Selecciona 2D o 3D con el widget RadioButtons

---

## 📋 Ejemplos de datos

### Ejemplo simple

**nodes.csv**:
```
id;label;type
A;Nodo A;TypeA
B;Nodo B;TypeB
C;Nodo C;TypeA
```

**edges.csv**:
```
src;dst;relationship
A;B;conecta_a
B;C;conecta_a
```

---

## 🐛 Troubleshooting

### Streamlit: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Colab: Los datos no se encuentran
- Verifica la ruta en la celda 4
- Asegúrate de montar Drive correctamente
- Comprueba que tienes `nodes.csv` y `edges.csv` en cada subcarpeta

### Error al leer CSV
- Verifica el separador (debe ser `;`)
- Asegúrate de que `id` y `label` existen
- Comprueba la codificación (UTF-8)

---

## 💡 Consejos

1. **Primero local**: Prueba con Streamlit para desarrollo
2. **Luego Colab**: Compartir resultados o trabajar sin instalación
3. **Datos limpios**: Valida nombres de columnas y formatos
4. **Grafos grandes**: Limita nodos en Streamlit para mejor rendimiento

---

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en el repositorio.

---

**Última actualización**: 2026-04-17

Tipos incluidos actualmente:
- `data_system`
- `object`
- `field`
- `process`
- `table`
- `column`
- `rule`

Si aparece un valor de `type` que no este en `color_map`, la app muestra una advertencia y usa el color por defecto `#808080`.

Para agregar un tipo nuevo, alcanza con sumar una entrada en `color_map`.

## Ejemplo minimo

`nodes.csv`

```csv
id,label
n1,Proceso A
n2,Tabla B
```

`edges.csv`

```csv
src,dst
n1,n2
```