## Evolução: Dimensionamento Fotovoltaico Residencial

Módulo de expansão do Sistema de Dimensionamento Energético Residencial destinado ao pré-dimensionamento de geração solar fotovoltaica conectada à rede (*on-grid*) e híbrida com armazenamento por baterias. O módulo consome diretamente o consumo de referência ($C_m$) apurado no cadastro e histórico da etapa anterior para dimensionar a potência de pico, filtrar equipamentos comerciais por compatibilidade elétrica e consolidar o orçamento da instalação.

---

### 1. Modelagem Matemática e Premissas de Cálculo

#### Geração Fotovoltaica
A demanda mensal projetada ($E_{FV}$) e a potência fotovoltaica de pico requerida ($P_{FV}$) são determinadas por:
$$E_{FV} = C_m \times f$$
$$P_{FV} = \frac{E_{FV}}{HSP \times D \times \eta}$$

A quantidade mínima de módulos fotovoltaicos ($N$) e a potência de pico instalada ($P_{\text{instalada}}$) são calculadas por:
$$N = \left\lceil \frac{P_{FV} \times 1000}{P_{\text{módulo}}} \right\rceil$$
$$P_{\text{instalada}} = \frac{N \times P_{\text{módulo}}}{1000}$$

A estimativa média de geração mensal efetiva do gerador instalado é dada por:
$$E_{\text{geração}} = P_{\text{instalada}} \times HSP \times D \times \eta$$

#### Armazenamento por Baterias (Opcional)
Para os cenários com armazenamento elétrico, o consumo médio diário ($E_d$) e a demanda energética no período de autonomia de $A$ horas ($E_{\text{autonomia}}$) são definidos por:
$$E_d = \frac{C_m}{30}$$
$$E_{\text{autonomia}} = E_d \times \left(\frac{A}{24}\right)$$

A capacidade nominal necessária de armazenamento ($C_{\text{bat}}$) e o número de unidades ($N_{\text{bat}}$) com base na capacidade útil individual ($C_{\text{útil}}$) consideram a profundidade de descarga ($DoD$) e a eficiência do ciclo de bateria ($\eta_{\text{bat}}$):
$$C_{\text{bat}} = \frac{E_{\text{autonomia}}}{DoD \times \eta_{\text{bat}}}$$
$$C_{\text{útil}} = C_{\text{nominal}} \times DoD$$
$$N_{\text{bat}} = \left\lceil \frac{C_{\text{bat}}}{C_{\text{útil}}} \right\rceil$$

#### Tabela de Premissas Técnicas Adotadas
| Parâmetro | Notação | Valor | Unidade | Justificativa / Fonte |
| :--- | :---: | :---: | :---: | :--- |
| Período Mensal de Referência | $D$ | 30 | dias | Padrão tarifário e contábil do setor elétrico. |
| Horas de Sol Pleno (São Paulo/SP) | $HSP$ | 4,37 | h/dia | Radiação média anual em plano inclinado (CRESESB / Atlas Brasileiro de Energia Solar). |
| Performance Ratio (Rendimento Global) | $\eta$ | 0,75 | adm. | Coeficiente de perdas elétricas, térmicas, sujeira e descasamento. |
| Eficiência do Ciclo de Armazenamento | $\eta_{\text{bat}}$ | 0,90 | adm. | Média operacional de sistemas com química Lítio Ferro Fosfato ($LiFePO_4$). |
| Profundidade Máxima de Descarga | $DoD$ | 0,95 | adm. | Limite seguro nominal certificado pelo fabricante (Pylontech US5000). |
| Taxa Adicional de Instalação e BOS | $C_{\text{demais}}$ | 20% | % | Estimativa para estruturas de fixação, condutores, proteções CC/CA e montagem. |

---

### 2. Estrutura dos Datasets de Equipamentos

Os equipamentos utilizados no dimensionamento são carregados a partir de ficheiros CSV situados no diretório `/data`, com rastreabilidade integral a distribuidores brasileiros e documentações técnicas dos fabricantes:

- **`modulos.csv` ($\ge 10$ itens):** `id`, `fabricante`, `modelo`, `potencia_wp`, `voc_v`, `isc_a`, `vmp_v`, `imp_a`, `eficiencia_pct`, `preco_brl`, `fornecedor`, `data_coleta`, `url_fonte`.
- **`inversores.csv` ($\ge 8$ itens):** `id`, `fabricante`, `modelo`, `tipo`, `potencia_nominal_w`, `potencia_max_fv_w`, `tensao_max_entrada_v`, `faixa_mppt_min_v`, `faixa_mppt_max_v`, `corrente_max_entrada_a`, `numero_mppt`, `compativel_bateria`, `preco_brl`, `fornecedor`, `data_coleta`, `url_fonte`.
- **`baterias.csv` ($\ge 6$ itens):** `id`, `fabricante`, `modelo`, `tecnologia`, `tensao_nominal_v`, `capacidade_ah`, `capacidade_kwh`, `dod_pct`, `ciclos`, `preco_brl`, `fornecedor`, `data_coleta`, `url_fonte`.

#### Regras de Validação de Compatibilidade Elétrica
1. **Capacidade do Gerador:** A potência total do arranjo fotovoltaico ($P_{\text{instalada}} \times 1000$) não excede a potência máxima CC suportada pelo inversor (`potencia_max_fv_w`).
2. **Faixa Operacional do MPPT:** A tensão de máxima potência da string ($V_{mp,\text{string}} = N_{\text{string}} \times V_{mp}$) opera estritamente dentro do intervalo `faixa_mppt_min_v` a `faixa_mppt_max_v` do inversor.
3. **Limite de Tensão de Circuito Aberto:** A tensão de circuito aberto da string ($V_{oc,\text{string}} = N_{\text{string}} \times V_{oc}$) permanece abaixo de `tensao_max_entrada_v` do inversor.
4. **Restrição Híbrida:** Apenas inversores com o atributo `compativel_bateria = true` são validados quando há solicitação de baterias.

---

### 3. Evidências dos Cenários de Teste

Para atendimento ao critério de validação do sistema, foram executados dois cenários de teste para a mesma residência de referência ($C_m = 450{,}00\text{ kWh/mês}$ e fração de atendimento $f = 100\%$):

#### Cenário 1: Conectado à Rede sem Armazenamento (On-Grid)
- **Comando executado:**
  ```bash
  python sistema_fotovoltaico.py --cenario on-grid --consumo 450 --f 1.0
  ```
- **Saída no terminal:**
  ```text
  ========================================================================
  RELATÓRIO DE PRÉ-DIMENSIONAMENTO FOTOVOLTAICO - ON-GRID CONECTADO À REDE
  ========================================================================
  [ENTRADAS DE CONSUMO E LOCALIZAÇÃO]
    - Consumo Mensal de Referência (Cm):       450.00 kWh/mês
    - Fração de Atendimento Solicitada (f):    100.0 %
    - Energia Mensal Requerida (E_FV):         450.00 kWh/mês
    - Recurso Solar Adotado (HSP):              4.37 h/dia (CRESESB - São Paulo/SP)

  [DIMENSIONAMENTO DO GERADOR SOLAR]
    - Potência Fotovoltaica Calculada (P_FV):  4.58 kWp
    - Módulo Selecionado:                       Canadian Solar CS6W-550MS (550 Wp)
    - Quantidade de Módulos (N):               9 unidades
    - Potência Efetivamente Instalada:          4.95 kWp
    - Estimativa Média de Geração Mensal:       486.71 kWh/mês

  [SELEÇÃO DO INVERSOR]
    - Inversor Selecionado:                     Solis S6-GR1P5K (INV006)
    - Tipo do Equipamento:                      ON-GRID
    - Potência Nominal CA:                      5000 W
    - Compatibilidade Elétrica / Bateria:       VALIDADA

  [ARMAZENAMENTO POR BATERIAS]
    - Sistema de Armazenamento:                 NÃO SOLICITADO

  [FORMAÇÃO DO ORÇAMENTO]
    - Módulos Fotovoltaicos:                    R$ 5,301.00
    - Inversor CC/CA:                           R$ 3,200.00
    - Banco de Baterias:                        R$ 0.00
    - Subtotal Equipamentos Principais:         R$ 8,501.00
    - BOS / Estrutura / Cabeamento / Instalação: R$ 1,700.20
  ------------------------------------------------------------------------
  VALOR TOTAL ESTIMADO DA SOLUÇÃO:              R$ 10,201.20
  ========================================================================
  ```

#### Cenário 2: Híbrido com Armazenamento por Baterias
- **Comando executado:**
  ```bash
  python sistema_fotovoltaico.py --cenario hibrido --consumo 450 --f 1.0 --autonomia 12
  ```
- **Saída no terminal:**
  ```text
  ========================================================================
  RELATÓRIO DE PRÉ-DIMENSIONAMENTO FOTOVOLTAICO - HÍBRIDO COM BATERIAS
  ========================================================================
  [ENTRADAS DE CONSUMO E LOCALIZAÇÃO]
    - Consumo Mensal de Referência (Cm):       450.00 kWh/mês
    - Fração de Atendimento Solicitada (f):    100.0 %
    - Energia Mensal Requerida (E_FV):         450.00 kWh/mês
    - Recurso Solar Adotado (HSP):              4.37 h/dia (CRESESB - São Paulo/SP)
    - Autonomia em Baterias Solicitada (A):    12.0 horas

  [DIMENSIONAMENTO DO GERADOR SOLAR]
    - Potência Fotovoltaica Calculada (P_FV):  4.58 kWp
    - Módulo Selecionado:                       Canadian Solar CS6W-550MS (550 Wp)
    - Quantidade de Módulos (N):               9 unidades
    - Potência Efetivamente Instalada:          4.95 kWp
    - Estimativa Média de Geração Mensal:       486.71 kWh/mês

  [SELEÇÃO DO INVERSOR]
    - Inversor Selecionado:                     Deye SUN-5K-SG04LP1-EU (INV003)
    - Tipo do Equipamento:                      HIBRIDO
    - Potência Nominal CA:                      5000 W
    - Compatibilidade Elétrica / Bateria:       VALIDADA

  [ARMAZENAMENTO POR BATERIAS]
    - Capacidade Nominal Necessária:           8.77 kWh
    - Bateria Selecionada:                      Pylontech US5000
    - Tecnologia:                               LiFePO4 (DoD: 95%)
    - Quantidade de Baterias (N_bat):           2 unidades
    - Capacidade Total Instalada:               9.60 kWh

  [FORMAÇÃO DO ORÇAMENTO]
    - Módulos Fotovoltaicos:                    R$ 5,301.00
    - Inversor CC/CA:                           R$ 8,990.00
    - Banco de Baterias:                        R$ 19,800.00
    - Subtotal Equipamentos Principais:         R$ 34,091.00
    - BOS / Estrutura / Cabeamento / Instalação: R$ 6,818.20
  ------------------------------------------------------------------------
  VALOR TOTAL ESTIMADO DA SOLUÇÃO:              R$ 40,909.20
  ========================================================================
  ```

---

### 4. Instruções para Reprodução

1. **Geração e Validação dos Datasets:**
   ```bash
   python gerador_datasets.py
   ```

2. **Execução Automatizada via Terminal:**
   ```bash
   # Cenário 1: On-grid padrão (sem armazenamento)
   python sistema_fotovoltaico.py --cenario on-grid --consumo 450 --f 1.0

   # Cenário 2: Híbrido com 12 horas de autonomia
   python sistema_fotovoltaico.py --cenario hibrido --consumo 450 --f 1.0 --autonomia 12
   ```

3. **Execução Interativa Integrada (Cadastro + Fotovoltaico):**
   ```bash
   python main.py
   ```

---

### 5. Rastreabilidade da Sprint e Gestão Ágil

- **Quadro no Trello:** `[Inserir link público do Trello da equipe]`
- **Mapeamento de Histórias:**
  - `US01`: Construção dos Datasets de Equipamentos Fotovoltaicos (`modulos.csv`, `inversores.csv`, `baterias.csv`).
  - `US02`: Integração de Consumo e Dimensionamento da Geração ($E_{FV}$, $P_{FV}$, Módulos).
  - `US03`: Seleção e Validação Técnica do Inversor (MPPT, Tensão Máx., Híbrido).
  - `US04`: Dimensionamento do Sistema de Armazenamento por Baterias ($E_d$, $E_{\text{autonomia}}$, $N_{\text{bat}}$).
  - `US05`: Formação do Orçamento e Emissão da Proposta Técnica.

---

### 6. Nota Técnica e Limitações

Este sistema executa um pré-dimensionamento preliminar e estimativa de custos para fins de estudo de viabilidade acadêmica. Ele não substitui o projeto elétrico executivo, o dimensionamento detalhado de queda de tensão em condutores, os diagramas unifilares com dispositivos de proteção contra surtos (DPS) e disjuntores, a análise estrutural da edificação nem a homologação de acesso junto à distribuidora de energia elétrica local.