# Pipeline de Análise de Segurança Automatizada (AIOps)

Sistema completo de análise de segurança usando visão computacional para detectar componentes em diagramas de arquitetura e gerar relatórios STRIDE automatizados.

## 🚀 Características

- **Detecção de Componentes**: Usa YOLOv8 para identificar componentes em diagramas de arquitetura
- **Análise STRIDE**: Gera automaticamente análise de ameaças usando metodologia STRIDE
- **Geração de Relatórios**: Cria relatórios em Markdown com recomendações de segurança
- **Interface Gradio**: Interface web simples para upload e análise de imagens
- **Integração Kaggle**: Download automático do dataset
- **Persistência**: Salva modelos e relatórios no Google Drive

## 📋 Pré-requisitos

1. **Google Colab**: Acesse [colab.research.google.com](https://colab.research.google.com)
2. **GPU**: Ative T4 GPU em `Ambiente de Execução > Alterar tipo de ambiente de execução`
3. **Kaggle API Token**: 
   - Acesse [Kaggle Settings](https://www.kaggle.com/settings)
   - Clique em "Create New API Token"
   - Baixe o arquivo `kaggle.json`

## 🔧 Configuração

### Passo 1: Upload do Notebook
1. Faça upload do arquivo `security_analysis_pipeline.ipynb` para o Google Colab
2. Abra o notebook no Colab

### Passo 2: Ativar GPU
1. No menu: `Ambiente de Execução > Alterar tipo de ambiente de execução`
2. Selecione **T4 GPU** (ou superior)
3. Clique em Salvar

### Passo 3: Executar Células
Execute as células na ordem:

1. **Configuração do Ambiente**: Instala dependências e monta Google Drive
2. **Autenticação Kaggle** (Opcional): Faça upload do `kaggle.json` quando solicitado
   - Para datasets públicos, você pode pular esta etapa
   - Recomendado para evitar limites de rate
3. **Download Dataset**: Baixa automaticamente o dataset usando `kagglehub`
4. **Exploração**: Visualiza amostras do dataset
5. **Treinamento**: Treina o modelo YOLOv8 (pode levar 30-60 minutos)
6. **Inferência**: Testa o modelo em imagens
7. **Interface Gradio**: (Opcional) Lança interface web

## 📁 Estrutura de Arquivos

Após a execução, os seguintes diretórios serão criados no Google Drive:

```
MyDrive/security_analysis/
├── models/
│   ├── security_analysis_model/
│   │   ├── weights/
│   │   │   └── best.pt          # Melhor modelo treinado
│   │   ├── results.png           # Gráficos de treinamento
│   │   └── confusion_matrix.png  # Matriz de confusão
│   └── final_model.pt            # Cópia do modelo final
├── reports/
│   ├── dataset_samples.png       # Amostras do dataset
│   ├── detection_result.png      # Resultado de detecção
│   └── stride_report_*.md        # Relatórios STRIDE gerados
└── README.md                     # Este arquivo
```

## 🎯 Uso

### Análise de Imagem Individual

```python
# Carregar modelo treinado
from ultralytics import YOLO
model = YOLO('/content/drive/MyDrive/security_analysis/models/final_model.pt')

# Analisar imagem
components, graph, annotated_img = detect_components_and_build_graph(
    'caminho/para/imagem.jpg', 
    model
)

# Gerar relatório
report = generate_stride_report(
    components, 
    graph, 
    'caminho/para/imagem.jpg',
    'relatorio.md'
)
```

### Interface Gradio

A interface Gradio permite:
- Upload de imagens via interface web
- Visualização imediata das detecções
- Geração automática de relatório STRIDE
- Compartilhamento via link público

## 🔍 Componentes Detectados

O modelo detecta os seguintes componentes:
- **Server**: Servidores de aplicação
- **Database**: Bancos de dados
- **User**: Usuários/clientes
- **LoadBalancer**: Balanceadores de carga
- **API**: APIs e endpoints

## 🛡️ Metodologia STRIDE

O sistema analisa cada componente detectado usando a metodologia STRIDE:

- **Spoofing**: Falsificação de identidade
- **Tampering**: Modificação não autorizada
- **Repudiation**: Negação de ações
- **Information Disclosure**: Exposição de informações
- **Denial of Service**: Negação de serviço
- **Elevation of Privilege**: Elevação de privilégios

Para cada ameaça, o sistema fornece:
- Descrição da ameaça específica
- Contramedidas sugeridas
- Recomendações de implementação

## 📊 Métricas de Treinamento

O notebook gera automaticamente:
- Gráficos de loss (treino/validação)
- Métricas de precisão e recall
- Matriz de confusão
- Curvas de aprendizado

## 🔧 Personalização

### Adicionar Novas Classes

1. Edite o arquivo `data.yaml` com as novas classes
2. Retreine o modelo com o dataset atualizado
3. Atualize o dicionário `STRIDE_THREATS` com ameaças específicas

### Ajustar Hiperparâmetros

Modifique a célula de treinamento:

```python
results = model.train(
    data=data_yaml_path,
    epochs=100,        # Mais épocas para melhor precisão
    imgsz=1280,        # Maior resolução
    batch=32,          # Batch maior se GPU permitir
    # ... outros parâmetros
)
```

## ⚠️ Troubleshooting

### GPU não detectada
- Verifique se ativou a GPU no Colab
- Execute: `!nvidia-smi` para verificar

### Erro ao baixar dataset Kaggle
- O `kagglehub` funciona sem autenticação para datasets públicos
- Se necessário, configure o `kaggle.json` (veja célula de autenticação)
- Confirme que aceitou os termos do dataset no Kaggle (se solicitado)

### Memória insuficiente
- Reduza o `batch` size no treinamento
- Use `imgsz=416` em vez de `640`
- Use modelo `yolov8n.pt` (nano)

### Modelo não encontra dataset
- Verifique a estrutura de diretórios
- Confirme que o `data.yaml` aponta para os caminhos corretos

## 📚 Referências

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [STRIDE Methodology](https://en.wikipedia.org/wiki/STRIDE_(security))
- [Kaggle Dataset](https://www.kaggle.com/datasets/carlosrian/software-architecture-dataset)

## 📝 Licença

Este projeto é fornecido como está, para fins educacionais e de pesquisa.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Áreas de melhoria:
- Adicionar mais classes de componentes
- Melhorar análise de conexões no grafo
- Expandir contramedidas STRIDE
- Adicionar exportação para PDF
- Implementar análise de dependências mais sofisticada
