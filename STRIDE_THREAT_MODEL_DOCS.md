# Documentação Técnica: STRIDE Threat Modeling Tool

## Visão Geral

O arquivo `stride_threat_model.py` contém uma solução automatizada para análise e modelagem de ameaças financeiras/sistêmicas baseada na metodologia STRIDE. Seu propósito principal é receber a imagem de um diagrama da arquitetura do sistema e, de forma autônoma, mapear o fluxo de dados, descobrir componentes e diagnosticar possíveis riscos e contramedidas.

## 1. Evolução do Desenvolvimento da Solução

### Fase Inicial: Abordagem com Modelo YOLO

Primeiramente, o time concebeu uma abordagem tradicional de visão computacional. Um modelo baseado na arquitetura **YOLO** (You Only Look Once) foi parcialmente treinado e desenvolvido para detectar e classificar caixas e ícones que representavam componentes arquiteturais nos diagramas. No entanto, percebeu-se que o treinamento de uma rede neural customizada para uma ampla gama de estilos de diagramas demandava um grande esforço na montagem dos datasets, alta capacidade computacional de GPUs e dificultava a extração da relação contextual e lógica de rede entre as partes detectadas.

### Transição e Adoção de IA Generativa

Após um entendimento maduro do problema e avaliação de custos, a estratégia pivotou em prol da **Inteligência Artificial Generativa (Vision LLMs)**. Constatou-se que utilizar uma IA Generativa Multimodal pronta, como o `GPT-4o` da OpenAI (por meio de LangChain), para interpretar a imagem, seria substancialmente mais **eficiente e mais barato**.
Ao invés de gastar recursos de máquinas virtuais e tempo de treinamento de reconhecimento de imagem rígido, a equipe focou o gasto apenas no **consumo de tokens das APIs**, ganhando de brinde um modelo capaz de raciocínio profundo sobre cibersegurança nativamente.

---

## 2. Fluxo de Execução da Solução Atual

O processo roda localmente através de um script Python CLI e o pipeline transcorre nos seguintes passos:

### Passo 1: Recebimento e Preparação da Imagem

- A ferramenta recebe a imagem (ex: `.png`, `.jpg`) de um diagrama de arquitetura de software/nuvem fornecida pelo usuário.
- O arquivo de entrada é codificado em **Base64** para permitir a transmissão como payload via HTTP para a API do provedor LLM.

### Passo 2: Extração de Componentes Arquiteturais (Análise Visual)

- O script monta um prompt sistêmico denso (LangChain `HumanMessage`) instruindo a IA como um Arquiteto de Software.
- A IA analisa o Base64 da imagem e devolve uma saída **JSON** catalogando todos os elementos do sistema.
- São extraídos, para cada elemento: **Nome, Tipo (Ex: DB, API, Load Balancer), Provedor (Ex: AWS, Genérico), Descrição** e suas **Conexões** formadoras do fluxo de dados.

### Passo 3: Análise de Ameaças Baseada na Metodologia STRIDE

- Usando as peças arquitetónicas recém geradas como contexto explícito numa nova requisição, é formulado um segundo e complexo prompt orientando o LLM para assumir a postura de Especialista Sênior em Cibersegurança.
- A IA diagnostica e mapeia ativamente as seis bases listadas pelo modelo, buscando riscos individualmente em cada componente mapeado:
  - **S**poofing (Falsificação de Identidade)
  - **T**ampering (Adulteração de Dados)
  - **R**epudiation (Repúdio/Não Rejeitabilidade)
  - **I**nformation Disclosure (Vazamento de Informação)
  - **D**enial of Service (Negação de Serviço / Indisponibilidade)
  - **E**levation of Privilege (Elevação de Privilégio)
- A saída deste estágio é um outro objeto **JSON** com vulnerabilidades estruturadas, categorizadas com prioridade/severidade de criticidade e atreladas a sugestões de contramedidas.

### Passo 4: Geração do Relatório (Report)

- Por fim, a lógica do sistema parseia todos esses JSONs gerados pela IA Generativa e monta um consolidado documento em formato de **Markdown** (`stride_report.md` ou nome definido via `--output`).
- O relatório embutirá matrizes de sumarização de risco (contagens categorizadas por ameaça), dados do fluxo da arquitetura, e quadros estruturados detalhando a anatomia exata do risco em cada nó do sistema auditado.

---

## 3. Instruções Base de Execução

Como o código consome LLMs, é obrigatória a declaração de credenciais de serviço, o que pode ser injetado via variáveis de ambiente (`.env`):

```bash
export OPENAI_API_KEY="sua_chave_de_api_openai_aqui"
```

A execução típica consiste em apontar o diagrama usando o argumento `--image`:

```bash
# Execução padrão gerando o relatório no arquivo 'stride_report.md'
python stride_threat_model.py --image arquitetura_aws.png

# Execução direcionando o nome do relatório de saída markdown
python stride_threat_model.py --image backend_diagram.jpg --output analise_risco.md
```
