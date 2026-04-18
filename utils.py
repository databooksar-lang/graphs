import os
import pandas as pd
import gspread
from google.colab import auth
from google.auth import default

def export_sheet_to_csvs(url_sheet, output_dir):
    # 🔐 Autenticación
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)

    # ⚙️ Configuración interna
    nodes_sheet_name = "nodes"
    edges_sheet_name = "edges"

    # 📁 Crear carpeta si no existe
    os.makedirs(output_dir, exist_ok=True)

    # 📊 Abrir Google Sheet
    sheet = gc.open_by_url(url_sheet)

    def sheet_to_csv(sheet, worksheet_name, output_name):
        print(f"Procesando hoja: {worksheet_name}")

        ws = sheet.worksheet(worksheet_name)
        data = ws.get_all_values()

        if not data:
            print(f"⚠️ La hoja {worksheet_name} está vacía")
            return

        columns = data[0]
        rows = data[1:]

        df = pd.DataFrame(rows, columns=columns)

        # 💡 intentar convertir números automáticamente
        df = df.apply(pd.to_numeric, errors='ignore')

        output_path = os.path.join(output_dir, output_name)
        df.to_csv(output_path, index=False, sep=";")

        print(f"✅ Guardado: {output_path}")

    # 🔽 Generar ambos archivos
    sheet_to_csv(sheet, nodes_sheet_name, "nodes.csv")
    sheet_to_csv(sheet, edges_sheet_name, "edges.csv")

    # 📂 Verificación final
    print("\nContenido de data/:")
    print(os.listdir(output_dir))