# Guía de inicio rápido

## ¿Cuál debería usar?

| Aspecto | Streamlit | Google Colab |
|--------|-----------|--------------|
| **Instalación** | Requiere Python local | Sin instalación, solo navegador |
| **Datos** | En carpetas locales | En Google Drive o local |
| **Personalización** | Máxima: colores, tooltips, filtros | Buena: widget interactivos |
| **Rendimiento** | Excelente para grafos grandes | Bueno (límites de compute) |
| **Colaboración** | Difícil de compartir | Fácil (solo necesitan link) |
| **Mejor para** | Desarrollo, uso local | Demos, presentaciones, análisis rápido |

---

## 🎯 Inicio rápido Streamlit

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Organizar datos
data/
  └── mi_grafo/
      ├── nodes.csv
      └── edges.csv

# 3. Ejecutar
streamlit run app.py

# 4. Abrir navegador
http://localhost:8501
```

---

## 🔥 Inicio rápido Colab

1. Descarga `graphs_colab.ipynb`
2. Abre en [Google Colab](https://colab.research.google.com)
3. Carga tu notebook
4. Actualiza la ruta de datos (celda 4)
5. Ejecuta todas las celdas
6. ¡Disfruta!

---

## Requisitos mínimos de datos

Para que funcione cualquiera de las dos opciones necesitas:

### nodes.csv
```
id;label;type
N1;Entidad 1;Tipo1
N2;Entidad 2;Tipo2
```

### edges.csv
```
src;dst;relationship
N1;N2;conecta
```

**Importante**: Usa `;` como separador (no `,`)

---

## Próximos pasos

1. Prepara tus datos en el formato requerido
2. Elige Streamlit para uso local o Colab para compartir
3. Si tienes preguntas, revisa el README.md completo
