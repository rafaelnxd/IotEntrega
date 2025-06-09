Previsão de Ondas de Calor em São Paulo
=======================================

Este repositório implementa um **protótipo de detecção e previsão de ondas de calor** na cidade de São Paulo, utilizando dados meteorológicos do INMET e shapefile dos distritos da cidade.

🎥 Vídeo Demonstrativo
----------------------

[Assista ao vídeo no YouTube](https://www.youtube.com/watch?v=uOzpU0tkYqs)

* * * * *

⚙️ Pré-requisitos
-----------------

-   **Python** 3.8 ou superior

-   **Dependências**:

    ```
    pip install -r requirements.txt
    ```

-   Arquivos de dados originais (CSV do INMET e shapefile dos distritos) na pasta `data/raw/`.

* * * * *

📂 Estrutura do Repositório
---------------------------

```
├── assets/
├── data/
│   ├── raw/                     # Dados brutos CSV e shapefile
│   ├── processed/               # Dados processados (gerados pelo notebook)
│   └── tests/
├── models/                      # Modelos treinados (gerados pelo notebook)
├── notebooks/
│   └── simulando_dados.ipynb    # Notebook para processamento e treinamento
├── streamlit_app/
│   └── Home.py                  # Aplicação web
├── requirements.txt
└── README.md
```

* * * * *

🛠️ Processamento e Treinamento de Modelos
------------------------------------------

Todo o fluxo de **pré-processamento**, **geração de dados simulados** e **treinamento dos modelos** está concentrado no notebook:

```
jupyter notebook notebooks/simulando_dados.ipynb
```

Dentro dele você encontrará células para:

1.  Ler e combinar os arquivos CSV do INMET (raw).

2.  Realizar interpolação e limpeza dos dados meteorológicos.

3.  Gerar datasets de treino e teste (incluindo simulações realistas).

4.  Treinar os modelos de regressão e classificação (RandomForest).

5.  Salvar os artefatos em `data/processed/` e em `models/`.

* * * * *

🚀 Executando a Aplicação Streamlit
-----------------------------------

1.  Acesse a pasta da aplicação:

    ```
    cd streamlit_app
    ```

2.  Execute o Streamlit:

    ```
    streamlit run Home.py
    ```

3.  Na interface, selecione **data inicial** e **data final** para visualizar:

    -   Tabela com previsão diária de temperatura.

    -   Dias previstos com onda de calor.

    -   Mapa interativo dos distritos, destacando em vermelho os distritos com onda de calor.

* * * * *
