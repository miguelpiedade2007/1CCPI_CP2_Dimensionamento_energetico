import json
from pathlib import Path
from typing import Dict, Any, List

JSON_PATH = Path("cadastros.json")

def criar_catalogo_padrao() -> Dict[int, Dict[str, Any]]:
    return {
        1: {"nome": "Chuveiro Elétrico", "categoria": "Banho", "potencia_w": 5500.0},
        2: {"nome": "Geladeira Frost Free", "categoria": "Refrigeração", "potencia_w": 250.0},
        3: {"nome": "Ar Condicionado", "categoria": "Climatização", "potencia_w": 900.0},
        4: {"nome": "Lâmpada LED", "categoria": "Iluminação", "potencia_w": 9.0},
        5: {"nome": "Televisor LED 50\"", "categoria": "Eletrônicos", "potencia_w": 100.0},
        6: {"nome": "Computador Desktop", "categoria": "Eletrônicos", "potencia_w": 350.0},
        7: {"nome": "Micro-ondas", "categoria": "Cozinha", "potencia_w": 1200.0},
        8: {"nome": "Máquina de Lavar Roupas", "categoria": "Lavanderia", "potencia_w": 500.0},
    }

def cadastrar_equipamento(catalogo: Dict[int, Dict[str, Any]], nome: str, categoria: str, potencia_w: float) -> int:
    novo_id = max(catalogo.keys(), default=0) + 1
    catalogo[novo_id] = {
        "nome": str(nome),
        "categoria": str(categoria),
        "potencia_w": float(potencia_w)
    }
    return novo_id

def criar_imovel(identificador: str, responsavel: str, endereco: str, localizacao: str = "São Paulo/SP") -> Dict[str, Any]:
    return {
        "identificador": str(identificador),
        "responsavel": str(responsavel),
        "endereco": str(endereco),
        "localizacao": str(localizacao),
        "itens": []
    }

def adicionar_item_imovel(imovel: Dict[str, Any], equipamento: Dict[str, Any], quantidade: int, horas_dia: float) -> None:
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")
    if horas_dia < 0 or horas_dia > 24:
        raise ValueError("O tempo de uso diário deve estar entre 0 e 24 horas.")

    imovel["itens"].append({
        "equipamento": equipamento,
        "quantidade": int(quantidade),
        "horas_dia": float(horas_dia)
    })

def calcular_consumo_kwh(potencia_w: float, quantidade: int, horas_dia: float, dias_mes: int = 30) -> float:
    return (potencia_w * quantidade * horas_dia * dias_mes) / 1000.0

def calcular_consumo_total_kwh(itens: List[Dict[str, Any]], dias_mes: int = 30) -> float:
    total = 0.0
    for item in itens:
        potencia = item["equipamento"]["potencia_w"]
        qtd = item["quantidade"]
        horas = item["horas_dia"]
        total += calcular_consumo_kwh(potencia, qtd, horas, dias_mes)
    return total

def formatar_relatorio(imovel: Dict[str, Any], dias_mes: int = 30) -> str:
    linhas = [
        "=" * 72,
        "RELATÓRIO DE CONSUMO ENERGÉTICO ESTIMADO",
        "=" * 72,
        f"Imóvel: {imovel['identificador']} | Responsável: {imovel['responsavel']}",
        f"Endereço: {imovel['endereco']} ({imovel.get('localizacao', 'São Paulo/SP')})",
        f"Período de referência: {dias_mes} dias",
        "-" * 72,
        f"{'Equipamento':<24} | {'Qtd':<4} | {'Uso (h/dia)':<11} | {'Consumo (kWh/mês)':<18}",
        "-" * 72,
    ]

    for item in imovel["itens"]:
        nome = item["equipamento"]["nome"]
        qtd = item["quantidade"]
        horas = item["horas_dia"]
        potencia = item["equipamento"]["potencia_w"]
        consumo = calcular_consumo_kwh(potencia, qtd, horas, dias_mes)
        linhas.append(
            f"{nome:<24} | "
            f"{qtd:<4} | "
            f"{horas:<11.1f} | "
            f"{consumo:>18.2f}"
        )

    linhas.append("-" * 72)
    total = calcular_consumo_total_kwh(imovel["itens"], dias_mes)
    linhas.append(f"CONSUMO TOTAL ESTIMADO: {total:.2f} kWh/mês")
    linhas.append("=" * 72)
    return "\n".join(linhas)

def carregar_base_cadastros() -> Dict[str, Any]:
    if not JSON_PATH.exists():
        return {"usuarios": {"imoveis": {}}}
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"usuarios": {"imoveis": {}}}

def salvar_imovel_base(imovel: Dict[str, Any]) -> None:
    base = carregar_base_cadastros()
    if "usuarios" not in base:
        base["usuarios"] = {}
    if "imoveis" not in base["usuarios"]:
        base["usuarios"]["imoveis"] = {}

    chave = imovel["identificador"]
    base["usuarios"]["imoveis"][chave] = imovel
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(base, f, indent=4, ensure_ascii=False)