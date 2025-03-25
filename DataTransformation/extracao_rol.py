import pandas as pd
import zipfile
import pdfplumber 
import os

def extract_tables_from_pdf(pdf_path):
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf: 
        for page in pdf.pages:
            tables = page.extract_tables() 
            for table in tables:
                if table and len(table) > 1:  # Verifica cabeçalhos e dados
                    all_tables.append(table)
    return all_tables

script_dir = os.path.dirname(os.path.abspath(__file__)) 
pdf_path = os.path.join(script_dir, "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf") # ./Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf não estava funcionando

tables = extract_tables_from_pdf(pdf_path)

all_data = []
headers = None
for table in tables:
    if not headers and table[0]:  # Assume que a primeira linha é o cabeçalho
        headers = [h if h else "" for h in table[0]] 
    for row in table[1:]:  
        all_data.append([cell if cell else "" for cell in row]) 

# Definir cabeçalhos
expected_headers = [
    "PROCEDIMENTO", "RN (included)", "VIGENCIA", "OD", "AMB", "HCO", "HSO", "REF", "PAC", "DUT", "SUBGRUPO", "GRUPO", "CAPITULO"
]

# Ajustar número de colunas
if len(headers) < len(expected_headers):
    headers.extend([""] * (len(expected_headers) - len(headers)))
elif len(headers) > len(expected_headers):
    headers = headers[:len(expected_headers)]

df = pd.DataFrame(all_data, columns=expected_headers[:len(headers)])

abbreviation_map = {
    "OD": "Seg. Odontológica",
    "AMB": "Seg. Ambulatorial",
    "HCO": "Seg. Hospitalar Com Obstetrícia",
    "HSO": "Seg. Hospitalar Sem Obstetrícia",
    "REF": "Plano Referência",
    "PAC": "Procedimento de Alta Complexidade",
    "DUT": "Diretriz de Utilização"
}

for col in ["OD", "AMB", "HCO", "HSO", "REF", "PAC", "DUT"]:
    df[col] = df[col].apply(lambda x: abbreviation_map.get(col, "") if x.strip() else "")

csv_filename = "Rol_Procedimentos_Saude.csv"
df.to_csv(csv_filename, index=False, encoding='utf-8')

zip_filename = "Teste_Endrio_Alberton.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(csv_filename)

os.remove(csv_filename)

print(f"Arquivo CSV '{csv_filename}' criado, compactado em '{zip_filename}' e excluído com sucesso!")