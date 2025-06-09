Previsão de Ondas de Calor em São Paulo
=======================================

Este repositório contém a implementação de um **protótipo de detecção e previsão de ondas de calor** na cidade de São Paulo, usando dados meteorológicos do INMET e shapefile de distritos.

* * * * *

Vídeo:
https://www.youtube.com/watch?v=uOzpU0tkYqs



⚙️ Pré-requisitos
-----------------

-   Python 3.8+

-   Biblioteca e dependências:

    ```
    pip install pandas numpy scikit-learn geopandas folium streamlit streamlit-folium joblib
    ```

-   Dados:

    -   `data/raw/SIRGAS_SHP_distrito.shp` e arquivos auxiliares

    -   `data/processed/historico_interpolado.csv` (gerado pelo `preprocess_data.py`)

* * * * *

🛠️ Preparação dos Dados
------------------------

1.  **Download** dos dados meteorológicos do INMET (2022--2024) em formato CSV bruto.

2.  Executar `scripts/preprocess_data.py` para:

    -   Ler os CSVs horárias

    -   Concatenar, ordenar e definir índice `datetime`

    -   Interpolar valores faltantes de temperatura e umidade

    -   Salvar `historico_interpolado.csv` em `data/processed`

Exemplo:

```
python scripts/preprocess_data.py --input-dir data/raw_inmet --output data/processed/historico_interpolado.csv
```

* * * * *

📈 Treinamento dos Modelos
--------------------------

No diretório `scripts/`, execute:

```
python train_models.py\
  --input data/processed/historico_interpolado.csv\
  --outdir models/\
  --horizon 7
```

Isso irá gerar:

-   `daily_temp_regressor.pkl`: modelo de regressão para previsão de temperatura máxima diária.

-   `heat_wave_classifier_7d.pkl`: classificador que prevê ocorrência de onda de calor num horizonte de 7 dias.

* * * * *

🚀 Executando a Aplicação Streamlit
-----------------------------------

No diretório `streamlit_app`:

```
streamlit run Home.py
```

-   Interface na barra lateral para selecionar **data inicial** e **data final**.

-   Tabelas com previsão diária de temperatura e lista de dias com onda de calor.

-   Mapa interativo com distritos de SP coloridos:

    -   **Azul**: sem onda de calor.

    -   **Vermelho**: há onda de calor no período.

* * * * *

🗂️ Detalhes de Implementação
-----------------------------

### 1\. Preprocessamento

-   `preprocess_data.py` usa `pandas` para ler múltiplos arquivos CSV do INMET.

-   Concatena séries de 2022, 2023 e 2024.

-   Interpola por `timestamp` para preencher faltantes.

### 2\. Treinamento dos Modelos

-   **Regressor**: RandomForestRegressor com validação `TimeSeriesSplit` para `temp_max` diária.

-   **Classificador**: RandomForestClassifier para flag `future_heat` em janela de *horizon* dias, usando lags de 1--3 dias.

### 3\. Aplicação Web

-   Streamlit para UI simples.

-   `geopandas` e `folium` para leitura de shapefile e renderização de mapas.

-   Predição de temperatura e onda por período arbitrário.

* * * * *



*Desenvolvido por Rafael e equipe de IoT Global Solution.*
