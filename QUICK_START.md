# 🚀 Guia Rápido de Início

## Passos para Executar no Google Colab

### 1️⃣ Preparação (5 minutos)

1. **Acesse o Google Colab**: [colab.research.google.com](https://colab.research.google.com)

2. **Obtenha o Token do Kaggle**:
   - Acesse: https://www.kaggle.com/settings
   - Clique em "Create New API Token"
   - Baixe o arquivo `kaggle.json`

3. **Faça Upload do Notebook**:
   - No Colab: `Arquivo > Fazer upload do notebook`
   - Selecione `security_analysis_pipeline.ipynb`

### 2️⃣ Configuração Inicial (2 minutos)

1. **Ative a GPU**:
   ```
   Menu: Ambiente de Execução > Alterar tipo de ambiente de execução
   Selecione: T4 GPU (ou superior)
   Clique em: Salvar
   ```

2. **Execute as Primeiras Células**:
   - Execute a célula "Verificar GPU" - deve mostrar sua GPU
   - Execute a célula "Instalar dependências" - aguarde instalação
   - Execute a célula "Montar Google Drive" - autorize o acesso

### 3️⃣ Autenticação Kaggle (Opcional - 1 minuto)

1. **Execute a célula de autenticação**
2. **Faça upload do `kaggle.json`** quando solicitado (ou pressione Cancel para pular)
   - Para datasets públicos, você pode pular esta etapa
   - Recomendado para evitar limites de rate
3. Aguarde confirmação ou continue sem autenticação

### 4️⃣ Download do Dataset (5-10 minutos)

1. **Execute a célula de download**:
   - Usa `kagglehub.dataset_download()` automaticamente
   - Funciona sem autenticação para datasets públicos
2. Aguarde o download e extração completarem

### 5️⃣ Treinamento (30-60 minutos)

1. **Execute todas as células de preparação de dados**
2. **Execute a célula de treinamento**:
   - O treinamento pode levar 30-60 minutos dependendo da GPU
   - Você verá métricas em tempo real
   - Gráficos serão gerados automaticamente

### 6️⃣ Teste e Uso (5 minutos)

1. **Execute a célula de inferência** para testar o modelo
2. **Execute a célula da interface Gradio** (opcional):
   - Uma URL será gerada
   - Acesse a URL para usar a interface web
   - Faça upload de imagens e receba relatórios STRIDE

## ⚡ Comandos Úteis

### Verificar GPU
```python
!nvidia-smi
```

### Ver estrutura do dataset
```python
!ls -la /content/dataset
```

### Carregar modelo treinado (em nova sessão)
```python
from ultralytics import YOLO
model = YOLO('/content/drive/MyDrive/security_analysis/models/final_model.pt')
```

## 🐛 Problemas Comuns

### GPU não detectada
- Verifique se ativou a GPU no menu
- Execute: `!nvidia-smi` para confirmar

### Erro ao baixar dataset
- O `kagglehub` funciona sem autenticação para datasets públicos
- Se necessário, configure o `kaggle.json` (opcional)
- Verifique se aceitou os termos do dataset no Kaggle (se solicitado)

### Memória insuficiente
- Reduza `batch` size no treinamento (de 16 para 8)
- Use `imgsz=416` em vez de `640`

### Modelo não encontra dados
- Verifique se o dataset foi extraído corretamente
- Confirme que o `data.yaml` aponta para os caminhos corretos

## 📊 Onde Encontrar Resultados

Todos os arquivos são salvos no Google Drive:

```
MyDrive/security_analysis/
├── models/
│   └── security_analysis_model/
│       └── weights/
│           └── best.pt          ← Modelo treinado
└── reports/
    ├── stride_report_*.md       ← Relatórios gerados
    └── detection_result.png      ← Imagens anotadas
```

## 💡 Dicas

- **Primeira execução**: Reserve 1-2 horas para setup completo
- **Reutilizar modelo**: Após treinar, você pode usar o modelo salvo sem retreinar
- **Interface Gradio**: Use para demonstrações rápidas
- **Relatórios**: Todos são salvos automaticamente no Drive

## 🎯 Próximos Passos

Após o treinamento inicial:
1. Teste com suas próprias imagens
2. Ajuste hiperparâmetros se necessário
3. Expanda as classes de componentes
4. Personalize as análises STRIDE

---

**Precisa de ajuda?** Consulte o `README.md` completo para mais detalhes.
