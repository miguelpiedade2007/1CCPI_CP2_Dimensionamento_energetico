import sys
import argparse
from cadastro import (
    criar_catalogo_padrao,
    cadastrar_equipamento,
    criar_imovel,
    adicionar_item_imovel,
    calcular_consumo_total_kwh,
    formatar_relatorio,
    salvar_imovel_base,
    carregar_base_cadastros,
)
from sistema_fotovoltaico import (
    EquipamentosRepository,
    MotorDimensionamento,
    RelatorioPresenter,
)

def cadastrar_novo_imovel_interativo() -> None:
    catalogo = criar_catalogo_padrao()

    print("\n--- CADASTRO DE NOVO IMÓVEL ---")
    identificador = input("Identificador do imóvel (ex: Apto 101, Casa Principal): ").strip()
    responsavel = input("Nome do responsável: ").strip()
    endereco = input("Endereço: ").strip()
    localizacao = input("Cidade/UF (ex: São Paulo/SP) [Padrão: São Paulo/SP]: ").strip()
    if not localizacao:
        localizacao = "São Paulo/SP"

    imovel = criar_imovel(identificador, responsavel, endereco, localizacao)

    while True:
        print("\n--- EQUIPAMENTOS DISPONÍVEIS NO CATÁLOGO ---")
        for id_eq, eq in catalogo.items():
            print(f"[{id_eq}] {eq['nome']:<25} | Categoria: {eq['categoria']:<15} | {eq['potencia_w']} W")
        print("[0] Concluir inserção de itens e salvar imóvel")
        print("[-1] Cadastrar novo tipo de equipamento no catálogo")

        entrada = input("\nSelecione o código desejado: ").strip()
        try:
            opcao = int(entrada)
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            continue

        if opcao == 0:
            break

        if opcao == -1:
            nome = input("Nome do equipamento: ").strip()
            categoria = input("Categoria: ").strip()
            try:
                potencia = float(input("Potência nominal (W): "))
                if potencia <= 0:
                    print("A potência deve ser maior que zero.")
                    continue
            except ValueError:
                print("Valor numérico inválido.")
                continue

            novo_id = cadastrar_equipamento(catalogo, nome, categoria, potencia)
            print(f"Equipamento '{nome}' registrado com código [{novo_id}].")
            continue

        if opcao not in catalogo:
            print("Código não encontrado.")
            continue

        try:
            qtd = int(input(f"Quantidade de '{catalogo[opcao]['nome']}': "))
            horas = float(input("Média diária de uso (horas/dia): "))
            adicionar_item_imovel(imovel, catalogo[opcao], qtd, horas)
            print("Item adicionado ao imóvel com sucesso.")
        except ValueError as e:
            print(f"Erro ao adicionar item: {e}")

    salvar_imovel_base(imovel)
    print("\n[OK] Imóvel salvo na base local (cadastros.json)!")
    print(formatar_relatorio(imovel))

def dimensionar_imovel_cadastrado() -> None:
    base = carregar_base_cadastros()
    imoveis = base.get("usuarios", {}).get("imoveis", {})

    if not imoveis:
        print("\nNenhum imóvel cadastrado na base. Cadastre um imóvel primeiro.")
        return

    print("\n--- IMÓVEIS DISPONÍVEIS NA BASE ---")
    lista_chaves = list(imoveis.keys())
    for idx, chave in enumerate(lista_chaves, start=1):
        im = imoveis[chave]
        cm = calcular_consumo_total_kwh(im.get("itens", []))
        print(f"[{idx}] {chave} - Responsável: {im.get('responsavel')} | Consumo: {cm:.2f} kWh/mês")

    entrada = input("\nSelecione o número do imóvel para dimensionamento solar: ").strip()
    try:
        idx_escolhido = int(entrada) - 1
        if idx_escolhido < 0 or idx_escolhido >= len(lista_chaves):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    imovel_selecionado = imoveis[lista_chaves[idx_escolhido]]
    consumo_referencia = calcular_consumo_total_kwh(imovel_selecionado.get("itens", []))

    if consumo_referencia <= 0:
        print("O imóvel selecionado não possui consumo registrado (0 kWh/mês).")
        return

    print(f"\nConsumo de Referência (Cm) importado: {consumo_referencia:.2f} kWh/mês")

    # Parâmetros fotovoltaicos da proposta
    try:
        f_input = input("Fração de atendimento desejada (0.1 a 1.0) [Padrão: 1.0 = 100%]: ").strip()
        f_val = float(f_input) if f_input else 1.0

        opc_bat = input("Deseja incluir armazenamento por baterias? (s/N): ").strip().lower()
        com_bateria = opc_bat in ("s", "sim")

        autonomia = 0.0
        if com_bateria:
            autonomia = float(input("Autonomia desejada em horas (ex: 12.0): ").strip())
    except ValueError:
        print("Entrada numérica inválida. Operação abortada.")
        return

    repo = EquipamentosRepository()
    motor = MotorDimensionamento(repo)
    proposta = motor.processar(
        consumo_mensal=consumo_referencia,
        fracao_atendimento=f_val,
        origem_hsp=f"CRESESB - {imovel_selecionado.get('localizacao', 'São Paulo/SP')}",
        com_armazenamento=com_bateria,
        autonomia_horas=autonomia
    )
    RelatorioPresenter.exibir(proposta)

def menu_principal():
    while True:
        print("\n" + "=" * 50)
        print(" SISTEMA DE ENERGIA E DIMENSIONAMENTO SOLAR")
        print("=" * 50)
        print("[1] Cadastrar novo imóvel e itens (Etapa 1)")
        print("[2] Listar imóveis e relatórios de consumo (Etapa 1)")
        print("[3] Dimensionar sistema fotovoltaico de imóvel cadastrado (Integração)")
        print("[0] Sair")

        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            cadastrar_novo_imovel_interativo()
        elif opcao == "2":
            base = carregar_base_cadastros()
            imoveis = base.get("usuarios", {}).get("imoveis", {})
            if not imoveis:
                print("\nNenhum imóvel cadastrado.")
            else:
                for im in imoveis.values():
                    print("\n" + formatar_relatorio(im))
        elif opcao == "3":
            dimensionar_imovel_cadastrado()
        elif opcao == "0":
            print("Encerrando o sistema.")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    # Suporte a argumentos CLI para reprodução automatizada de testes
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-h") and ("--cenario" in sys.argv or "--consumo" in sys.argv):
        parser = argparse.ArgumentParser(description="Dimensionamento Fotovoltaico Integrado")
        parser.add_argument("--consumo", type=float, default=450.0, help="Consumo médio mensal em kWh/mês")
        parser.add_argument("--f", type=float, default=1.0, help="Fração de atendimento")
        parser.add_argument("--cenario", choices=["on-grid", "hibrido"], default="on-grid")
        parser.add_argument("--autonomia", type=float, default=12.0)
        args = parser.parse_args()

        repo = EquipamentosRepository()
        motor = MotorDimensionamento(repo)
        com_bateria = (args.cenario == "hibrido")
        proposta = motor.processar(
            consumo_mensal=args.consumo,
            fracao_atendimento=args.f,
            com_armazenamento=com_bateria,
            autonomia_horas=args.autonomia if com_bateria else 0.0
        )
        RelatorioPresenter.exibir(proposta)
    else:
        menu_principal()