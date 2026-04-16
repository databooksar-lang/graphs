# graphs

Visualizacion de grafo con Streamlit + NetworkX + PyVis a partir de archivos CSV en la carpeta `data`.

## Formato de datos

La app esta preparada para funcionar con esquemas variables, con estas columnas minimas:

### nodes.csv

Columnas obligatorias:
- `id`
- `label`

Columnas opcionales reconocidas:
- `type` (default: `unknown`)
- `criticality` (default: `n/a`)
- `size` (si existe y es numerico, se usa para el tamano del nodo)

Si faltan `id` o `label`, la app muestra error y detiene la ejecucion.

### edges.csv

Columnas obligatorias:
- `src`
- `dst`

Compatibilidad:
- Tambien se aceptan `source` y `target` (se normalizan internamente a `src` y `dst`).

Columnas opcionales reconocidas:
- `relationship` (default: `related_to`)

Compatibilidad temporal:
- Si el archivo trae `relation`, tambien se acepta y se normaliza a `relationship`.

Si faltan columnas obligatorias de aristas, la app muestra error y detiene la ejecucion.

## Comportamiento por defecto

- Nodos sin `id` o `label` se omiten.
- Aristas sin `src` o `dst` se omiten.
- El filtro lateral de relaciones se muestra cuando hay valores de `relationship`.
- Si existe `type`, los nodos usan color por tipo.
- Si no existe `type`, todos los nodos usan un unico color por defecto.

## Colores por tipo

El color del nodo se define en `color_map` dentro de `app.py`.

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