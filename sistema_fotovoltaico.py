import csv
import math
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Modulo:
    id: str
    fabricante: str
    modelo: str
    potencia_wp: float
    voc_v: float
    isc_a: float
    vmp_v: float
    imp_a: float
    eficiencia_pct: float
    preco_brl: float
    fornecedor: str
    data_coleta: str
    url_fonte: str

@dataclass
class Inversor:
    id: str
    fabricante: str
    modelo: str
    tipo: str
    potencia_nominal_w: float
    potencia_max_fv_w: float
    tensao_max_entrada_v: float
    faixa_mppt_min_v: float
    faixa_mppt_max_v: float
    corrente_max_entrada_a: float
    numero_mppt: int
    compativel_bateria: bool
    preco_brl: float
    fornecedor: str
    data_coleta: str
    url_fonte: str

@dataclass
class Bateria:
    id: str
    fabricante: str
    modelo: str
    tecnologia: str
    tensao_nominal_v: float
    capacidade_ah: float
    capacidade_kwh: float
    dod_pct: float
    ciclos: int
    preco_brl: float
    fornecedor: str
    data_coleta: str
    url_fonte: str

@dataclass
class PropostaTecnica:
    consumo_referencia: float
    fracao_atendimento: float
    energia_mensal_desejada: float
    hsp_utilizado: float
    origem_hsp: str
    potencia_fv_calculada_kwp: float
    potencia_instalada_kwp: float
    modulo_selecionado: Modulo
    quantidade_modulos: int
    inversor_selecionado: Inversor
    has_armazenamento: bool
    autonomia_horas: float
    capacidade_armazenamento_calculada_kwh: float
    capacidade_armazenamento_instalada_kwh: float
    bateria_selecionada: Optional[Bateria]
    quantidade_baterias: int
    estimativa_geracao_mensal_kwh: float
    custo_modulos: float
    custo_inversor: float
    custo_baterias: float
    custo_equipamentos: float
    custo_adicionais: float
    custo_total: float

class EquipamentosRepository:
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir

    def carregar_modulos(self) -> List[Modulo]:
        path = self.data_dir / "modulos.csv"
        modulos = []
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                modulos.append(Modulo(
                    id=r["id"],
                    fabricante=r["fabricante"],
                    modelo=r["modelo"],
                    potencia_wp=float(r["potencia_wp"]),
                    voc_v=float(r["voc_v"]),
                    isc_a=float(r["isc_a"]),
                    vmp_v=float(r["vmp_v"]),
                    imp_a=float(r["imp_a"]),
                    eficiencia_pct=float(r["eficiencia_pct"]),
                    preco_brl=float(r["preco_brl"]),
                    fornecedor=r["fornecedor"],
                    data_coleta=r["data_coleta"],
                    url_fonte=r["url_fonte"]
                ))
        return modulos

    def carregar_inversores(self) -> List[Inversor]:
        path = self.data_dir / "inversores.csv"
        inversores = []
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                compativel = r["compativel_bateria"].strip().lower() in ("true", "1", "sim")
                inversores.append(Inversor(
                    id=r["id"],
                    fabricante=r["fabricante"],
                    modelo=r["modelo"],
                    tipo=r["tipo"],
                    potencia_nominal_w=float(r["potencia_nominal_w"]),
                    potencia_max_fv_w=float(r["potencia_max_fv_w"]),
                    tensao_max_entrada_v=float(r["tensao_max_entrada_v"]),
                    faixa_mppt_min_v=float(r["faixa_mppt_min_v"]),
                    faixa_mppt_max_v=float(r["faixa_mppt_max_v"]),
                    corrente_max_entrada_a=float(r["corrente_max_entrada_a"]),
                    numero_mppt=int(r["numero_mppt"]),
                    compativel_bateria=compativel,
                    preco_brl=float(r["preco_brl"]),
                    fornecedor=r["fornecedor"],
                    data_coleta=r["data_coleta"],
                    url_fonte=r["url_fonte"]
                ))
        return inversores

    def carregar_baterias(self) -> List[Bateria]:
        path = self.data_dir / "baterias.csv"
        baterias = []
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                dod_val = float(r.get("dod_pct") or r.get("dod_pet"))
                baterias.append(Bateria(
                    id=r["id"],
                    fabricante=r["fabricante"],
                    modelo=r["modelo"],
                    tecnologia=r["tecnologia"],
                    tensao_nominal_v=float(r["tensao_nominal_v"]),
                    capacidade_ah=float(r["capacidade_ah"]),
                    capacidade_kwh=float(r["capacidade_kwh"]),
                    dod_pct=dod_val,
                    ciclos=int(r["ciclos"]),
                    preco_brl=float(r["preco_brl"]),
                    fornecedor=r["fornecedor"],
                    data_coleta=r["data_coleta"],
                    url_fonte=r["url_fonte"]
                ))
        return baterias

class CompatibilidadeValidator:
    @staticmethod
    def validar_inversor(
        inversor: Inversor,
        modulo: Modulo,
        n_modulos: int,
        p_instalada_w: float,
        precisa_armazenamento: bool
    ) -> bool:
        if precisa_armazenamento and not inversor.compativel_bateria:
            return False

        if p_instalada_w > inversor.potencia_max_fv_w:
            return False

        if p_instalada_w < (inversor.potencia_nominal_w * 0.40):
            return False

        configs = [n_modulos]
        if n_modulos % 2 == 0 and inversor.numero_mppt >= 2:
            configs.append(n_modulos // 2)

        config_valida = False
        for modulos_por_string in configs:
            v_oc_string = modulos_por_string * modulo.voc_v
            v_mp_string = modulos_por_string * modulo.vmp_v

            if v_oc_string >= inversor.tensao_max_entrada_v:
                continue

            if inversor.faixa_mppt_min_v <= v_mp_string <= inversor.faixa_mppt_max_v:
                config_valida = True
                break

        return config_valida

class MotorDimensionamento:
    def __init__(self, repo: EquipamentosRepository):
        self.repo = repo
        self.modulos = repo.carregar_modulos()
        self.inversores = repo.carregar_inversores()
        self.baterias = repo.carregar_baterias()

    def processar(
        self,
        consumo_mensal: float,
        fracao_atendimento: float = 1.0,
        hsp: float = 4.37,
        origem_hsp: str = "CRESESB - São Paulo/SP",
        dias_mes: int = 30,
        rendimento_global: float = 0.75,
        com_armazenamento: bool = False,
        autonomia_horas: float = 0.0,
        eficiencia_bateria: float = 0.90,
        taxa_bos: float = 0.20
    ) -> PropostaTecnica:

        e_fv = consumo_mensal * fracao_atendimento
        p_fv_kwp = e_fv / (hsp * dias_mes * rendimento_global)

        modulo_escolhido = self.modulos[0]
        n_modulos = math.ceil((p_fv_kwp * 1000.0) / modulo_escolhido.potencia_wp)
        p_instalada_kwp = (n_modulos * modulo_escolhido.potencia_wp) / 1000.0
        p_instalada_w = p_instalada_kwp * 1000.0

        geracao_mensal_kwh = p_instalada_kwp * hsp * dias_mes * rendimento_global

        inversores_validos = [
            inv for inv in self.inversores
            if CompatibilidadeValidator.validar_inversor(
                inv, modulo_escolhido, n_modulos, p_instalada_w, com_armazenamento
            )
        ]

        if not inversores_validos:
            raise ValueError("Nenhum inversor compatível com a configuração dimensionada foi encontrado no dataset.")

        inversores_validos.sort(key=lambda x: x.preco_brl)
        inversor_escolhido = inversores_validos[0]

        cap_bat_calculada_kwh = 0.0
        cap_bat_instalada_kwh = 0.0
        bateria_escolhida = None
        n_baterias = 0

        if com_armazenamento and autonomia_horas > 0:
            e_d = consumo_mensal / 30.0
            e_autonomia = e_d * (autonomia_horas / 24.0)

            bateria_candidatas = []
            for bat in self.baterias:
                dod = bat.dod_pct / 100.0
                cap_necessaria = e_autonomia / (dod * eficiencia_bateria)
                cap_util = bat.capacidade_kwh * dod
                qtd = math.ceil(cap_necessaria / cap_util)
                custo_total_bat = qtd * bat.preco_brl
                bateria_candidatas.append((custo_total_bat, qtd, cap_necessaria, bat))

            bateria_candidatas.sort(key=lambda x: x[0])
            melhor_opcao = bateria_candidatas[0]

            bateria_escolhida = melhor_opcao[3]
            n_baterias = melhor_opcao[1]
            cap_bat_calculada_kwh = melhor_opcao[2]
            cap_bat_instalada_kwh = n_baterias * bateria_escolhida.capacidade_kwh

        custo_modulos = n_modulos * modulo_escolhido.preco_brl
        custo_inversor = inversor_escolhido.preco_brl
        custo_baterias = (n_baterias * bateria_escolhida.preco_brl) if bateria_escolhida else 0.0

        custo_equipamentos = custo_modulos + custo_inversor + custo_baterias
        custo_adicionais = custo_equipamentos * taxa_bos
        custo_total = custo_equipamentos + custo_adicionais

        return PropostaTecnica(
            consumo_referencia=consumo_mensal,
            fracao_atendimento=fracao_atendimento,
            energia_mensal_desejada=e_fv,
            hsp_utilizado=hsp,
            origem_hsp=origem_hsp,
            potencia_fv_calculada_kwp=p_fv_kwp,
            potencia_instalada_kwp=p_instalada_kwp,
            modulo_selecionado=modulo_escolhido,
            quantidade_modulos=n_modulos,
            inversor_selecionado=inversor_escolhido,
            has_armazenamento=com_armazenamento,
            autonomia_horas=autonomia_horas,
            capacidade_armazenamento_calculada_kwh=cap_bat_calculada_kwh,
            capacidade_armazenamento_instalada_kwh=cap_bat_instalada_kwh,
            bateria_selecionada=bateria_escolhida,
            quantidade_baterias=n_baterias,
            estimativa_geracao_mensal_kwh=geracao_mensal_kwh,
            custo_modulos=custo_modulos,
            custo_inversor=custo_inversor,
            custo_baterias=custo_baterias,
            custo_equipamentos=custo_equipamentos,
            custo_adicionais=custo_adicionais,
            custo_total=custo_total
        )

class RelatorioPresenter:
    @staticmethod
    def exibir(p: PropostaTecnica):
        tag_cenario = "HÍBRIDO COM BATERIAS" if p.has_armazenamento else "ON-GRID CONECTADO À REDE"
        print("=" * 72)
        print(f"RELATÓRIO DE PRÉ-DIMENSIONAMENTO FOTOVOLTAICO - {tag_cenario}")
        print("=" * 72)
        print("[ENTRADAS DE CONSUMO E LOCALIZAÇÃO]")
        print(f"  - Consumo Mensal de Referência (Cm):       {p.consumo_referencia:,.2f} kWh/mês")
        print(f"  - Fração de Atendimento Solicitada (f):    {p.fracao_atendimento * 100:,.1f} %")
        print(f"  - Energia Mensal Requerida (E_FV):         {p.energia_mensal_desejada:,.2f} kWh/mês")
        print(f"  - Recurso Solar Adotado (HSP):              {p.hsp_utilizado:.2f} h/dia ({p.origem_hsp})")
        if p.has_armazenamento:
            print(f"  - Autonomia em Baterias Solicitada (A):    {p.autonomia_horas:.1f} horas")

        print("\n[DIMENSIONAMENTO DO GERADOR SOLAR]")
        print(f"  - Potência Fotovoltaica Calculada (P_FV):  {p.potencia_fv_calculada_kwp:.2f} kWp")
        print(f"  - Módulo Selecionado:                       {p.modulo_selecionado.fabricante} {p.modulo_selecionado.modelo} ({p.modulo_selecionado.potencia_wp:.0f} Wp)")
        print(f"  - Quantidade de Módulos (N):               {p.quantidade_modulos} unidades")
        print(f"  - Potência Efetivamente Instalada:          {p.potencia_instalada_kwp:.2f} kWp")
        print(f"  - Estimativa Média de Geração Mensal:       {p.estimativa_geracao_mensal_kwh:,.2f} kWh/mês")

        print("\n[SELEÇÃO DO INVERSOR]")
        print(f"  - Inversor Selecionado:                     {p.inversor_selecionado.fabricante} {p.inversor_selecionado.modelo} ({p.inversor_selecionado.id})")
        print(f"  - Tipo do Equipamento:                      {p.inversor_selecionado.tipo.upper()}")
        print(f"  - Potência Nominal CA:                      {p.inversor_selecionado.potencia_nominal_w:.0f} W")
        print(f"  - Compatibilidade Elétrica / Bateria:       VALIDADA")

        if p.has_armazenamento and p.bateria_selecionada:
            print("\n[ARMAZENAMENTO POR BATERIAS]")
            print(f"  - Capacidade Nominal Necessária:           {p.capacidade_armazenamento_calculada_kwh:.2f} kWh")
            print(f"  - Bateria Selecionada:                      {p.bateria_selecionada.fabricante} {p.bateria_selecionada.modelo}")
            print(f"  - Tecnologia:                               {p.bateria_selecionada.tecnologia} (DoD: {p.bateria_selecionada.dod_pct:.0f}%)")
            print(f"  - Quantidade de Baterias (N_bat):           {p.quantidade_baterias} unidades")
            print(f"  - Capacidade Total Instalada:               {p.capacidade_armazenamento_instalada_kwh:.2f} kWh")
        else:
            print("\n[ARMAZENAMENTO POR BATERIAS]")
            print("  - Sistema de Armazenamento:                 NÃO SOLICITADO")

        print("\n[FORMAÇÃO DO ORÇAMENTO]")
        print(f"  - Módulos Fotovoltaicos:                    R$ {p.custo_modulos:,.2f}")
        print(f"  - Inversor CC/CA:                           R$ {p.custo_inversor:,.2f}")
        print(f"  - Banco de Baterias:                        R$ {p.custo_baterias:,.2f}")
        print(f"  - Subtotal Equipamentos Principais:         R$ {p.custo_equipamentos:,.2f}")
        print(f"  - BOS / Estrutura / Cabeamento / Instalação: R$ {p.custo_adicionais:,.2f}")
        print("-" * 72)
        print(f"VALOR TOTAL ESTIMADO DA SOLUÇÃO:              R$ {p.custo_total:,.2f}")
        print("=" * 72)