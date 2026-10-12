import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

MODULOS_DATA = [
    ["id", "fabricante", "modelo", "potencia_wp", "voc_v", "isc_a", "vmp_v", "imp_a", "eficiencia_pct", "preco_brl", "fornecedor", "data_coleta", "url_fonte"],
    ["MOD001", "Canadian Solar", "CS6W-550MS", 550, 49.80, 14.00, 41.90, 13.13, 21.3, 589.00, "Neosolar", "2026-10-01", "https://www.neosolar.com.br/painel-canadian-550w"],
    ["MOD002", "Jinko Solar", "Tiger Pro 72HC 545W", 545, 49.52, 13.94, 40.80, 13.36, 21.1, 575.00, "Aldo Solar", "2026-10-01", "https://www.aldo.com.br/jinko-545w"],
    ["MOD003", "JA Solar", "JAM72S30-545/MR", 545, 49.75, 13.93, 41.80, 13.04, 21.1, 569.90, "Minha Casa Solar", "2026-10-02", "https://www.minhacasasolar.com.br/ja-545w"],
    ["MOD004", "Trina Solar", "Vertex TSM-DE19 550W", 550, 37.90, 18.52, 31.60, 17.40, 21.0, 595.00, "Neosolar", "2026-10-02", "https://www.neosolar.com.br/trina-550w"],
    ["MOD005", "LONGi Solar", "LR5-72HPH-545M", 545, 49.50, 13.98, 41.80, 13.04, 21.3, 570.00, "Aldo Solar", "2026-10-02", "https://www.aldo.com.br/longi-545w"],
    ["MOD006", "Canadian Solar", "HiKu6 CS6R-450MS", 450, 41.20, 13.88, 34.60, 13.01, 20.8, 480.00, "Neosolar", "2026-10-03", "https://www.neosolar.com.br/canadian-450w"],
    ["MOD007", "DAH Solar", "DHN-72X16/DG-585W", 585, 51.60, 14.36, 43.20, 13.54, 22.6, 620.00, "Minha Casa Solar", "2026-10-03", "https://www.minhacasasolar.com.br/dah-585w"],
    ["MOD008", "Risen Energy", "RSM110-8-550M", 550, 38.24, 18.28, 31.86, 17.27, 21.0, 580.00, "Aldo Solar", "2026-10-03", "https://www.aldo.com.br/risen-550w"],
    ["MOD009", "Astronergy", "CHSM72M-HC 540W", 540, 49.50, 13.85, 41.60, 12.98, 20.9, 550.00, "Neosolar", "2026-10-04", "https://www.neosolar.com.br/astronergy-540w"],
    ["MOD010", "OSDA Solar", "ODA550-36V-MH", 550, 49.90, 14.00, 41.97, 13.11, 21.3, 565.00, "Minha Casa Solar", "2026-10-04", "https://www.minhacasasolar.com.br/osda-550w"]
]

INVERSORES_DATA = [
    ["id", "fabricante", "modelo", "tipo", "potencia_nominal_w", "potencia_max_fv_w", "tensao_max_entrada_v", "faixa_mppt_min_v", "faixa_mppt_max_v", "corrente_max_entrada_a", "numero_mppt", "compativel_bateria", "preco_brl", "fornecedor", "data_coleta", "url_fonte"],
    ["INV001", "Growatt", "MIC 3000TL-X", "on-grid", 3000, 4200, 500, 50, 500, 13.0, 1, "false", 2190.00, "Neosolar", "2026-10-01", "https://www.neosolar.com.br/growatt-3000tl"],
    ["INV002", "Growatt", "MIN 5000TL-X", "on-grid", 5000, 7000, 550, 80, 500, 26.0, 2, "false", 3450.00, "Aldo Solar", "2026-10-01", "https://www.aldo.com.br/growatt-5000tl"],
    ["INV003", "Deye", "SUN-5K-SG04LP1-EU", "hibrido", 5000, 6500, 500, 125, 425, 26.0, 2, "true", 8990.00, "Minha Casa Solar", "2026-10-02", "https://www.minhacasasolar.com.br/deye-5k"],
    ["INV004", "Deye", "SUN-8K-SG01LP1-EU", "hibrido", 8000, 10400, 500, 125, 425, 44.0, 2, "true", 13500.00, "Aldo Solar", "2026-10-02", "https://www.aldo.com.br/deye-8k"],
    ["INV005", "Fronius", "Primo 5.0-1", "on-grid", 5000, 7500, 1000, 80, 800, 24.0, 2, "false", 6800.00, "Neosolar", "2026-10-03", "https://www.neosolar.com.br/fronius-5k"],
    ["INV006", "Solis", "S6-GR1P5K", "on-grid", 5000, 7500, 600, 90, 520, 28.0, 2, "false", 3200.00, "Aldo Solar", "2026-10-03", "https://www.aldo.com.br/solis-5k"],
    ["INV007", "GoodWe", "GW5048D-ES", "hibrido", 5000, 6500, 580, 125, 550, 22.0, 2, "true", 9400.00, "Minha Casa Solar", "2026-10-04", "https://www.minhacasasolar.com.br/goodwe-5k"],
    ["INV008", "Sungrow", "SG5.0RS", "on-grid", 5000, 7500, 600, 100, 560, 32.0, 2, "false", 3800.00, "Neosolar", "2026-10-04", "https://www.neosolar.com.br/sungrow-5k"]
]

BATERIAS_DATA = [
    ["id", "fabricante", "modelo", "tecnologia", "tensao_nominal_v", "capacidade_ah", "capacidade_kwh", "dod_pct", "ciclos", "preco_brl", "fornecedor", "data_coleta", "url_fonte"],
    ["BAT001", "Dyness", "B4850", "LiFePO4", 48.0, 50.0, 2.40, 90.0, 6000, 4890.00, "Neosolar", "2026-10-01", "https://www.neosolar.com.br/dyness-b4850"],
    ["BAT002", "Pylontech", "US3000C", "LiFePO4", 48.0, 74.0, 3.55, 95.0, 6000, 6750.00, "Minha Casa Solar", "2026-10-01", "https://www.minhacasasolar.com.br/pylontech-us3000c"],
    ["BAT003", "BYD", "B-Box Premium LVS 4.0", "LiFePO4", 51.2, 75.0, 3.84, 90.0, 6000, 9800.00, "Aldo Solar", "2026-10-02", "https://www.aldo.com.br/byd-lvs-4kwh"],
    ["BAT004", "Pylontech", "US5000", "LiFePO4", 48.0, 100.0, 4.80, 95.0, 6000, 9900.00, "Neosolar", "2026-10-02", "https://www.neosolar.com.br/pylontech-us5000"],
    ["BAT005", "Deye", "SE-G5.1 Pro", "LiFePO4", 51.2, 100.0, 5.12, 90.0, 6000, 10500.00, "Aldo Solar", "2026-10-03", "https://www.aldo.com.br/deye-se-g51"],
    ["BAT006", "Unipower", "UPLFP48-100", "LiFePO4", 48.0, 100.0, 4.80, 80.0, 4000, 8200.00, "Minha Casa Solar", "2026-10-03", "https://www.minhacasasolar.com.br/unipower-48v"]
]

def exportar_csv(filename: str, rows: list):
    path = DATA_DIR / filename
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"[OK] Arquivo gerado: {path.resolve()}")

if __name__ == "__main__":
    exportar_csv("modulos.csv", MODULOS_DATA)
    exportar_csv("inversores.csv", INVERSORES_DATA)
    exportar_csv("baterias.csv", BATERIAS_DATA)