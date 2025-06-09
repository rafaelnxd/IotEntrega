import streamlit as st
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --- Configurações ---
csv_path = '../data/processed/historico_interpolado.csv'
model_dir = '../models/'
horizon_default = 7
threshold_delta = 5.0
lags_daily = [1,2,3]

# --- Funções auxiliares ---
def prepare_daily_data(historico):
    daily = historico['Temperatura_interp'].resample('D').max().to_frame('temp_max')
    daily['mes'] = daily.index.month
    hist_month = daily.groupby('mes')['temp_max'].mean().rename('hist_mean')
    daily = daily.merge(hist_month, left_on='mes', right_index=True)
    daily['threshold'] = daily['hist_mean'] + threshold_delta
    daily['heat_label'] = (daily['temp_max'] >= daily['threshold']).astype(int)
    for lag in lags_daily:
        daily[f'max_lag_{lag}d'] = daily['temp_max'].shift(lag)
    return daily

@st.cache(allow_output_mutation=True)
def load_data_and_models():
    # Carrega CSV histórico
    df = pd.read_csv(csv_path, sep=';')
    cols = df.columns.tolist()
    if len(cols) < 2:
        st.error("CSV histórico precisa ter pelo menos duas colunas: data e temperatura")
        st.stop()
    # Detecta coluna de data (primeira) e coluna de temperatura (busca por 'temp')
    date_col = cols[0]
    temp_col = None
    for c in cols[1:]:
        if 'temp' in c.lower():
            temp_col = c
            break
    if temp_col is None:
        temp_col = cols[1]
    # Converter data e setar índice
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    historico = df.set_index(date_col)[[temp_col]]
    historico = historico.rename(columns={temp_col: 'Temperatura_interp'})
    # Preparar dados diários
    daily = prepare_daily_data(historico)
    # Carregar modelos
    reg = joblib.load(f'{model_dir}/daily_temp_regressor.pkl')
    clf = joblib.load(f'{model_dir}/heat_wave_classifier_{horizon_default}d.pkl')
    return historico, daily, reg, clf

# Previsão diária de temperatura
def forecast_daily_temp(start, end, daily_df, regressor):
    dates = pd.date_range(start=start, end=end, freq='D')
    history = daily_df.copy()
    preds = []
    for date in dates:
        mes = date.month
        hist_mean = history.loc[history.index.month==mes,'temp_max'].mean()
        lags = {}
        for lag in lags_daily:
            ld = date - pd.Timedelta(days=lag)
            lags[f'max_lag_{lag}d'] = history.at[ld,'temp_max'] if ld in history.index else hist_mean
        feat = {'mes':mes,'hist_mean':hist_mean,**lags}
        t_pred = regressor.predict(pd.DataFrame([feat]))[0]
        preds.append({'date':date,'temp_max_pred':t_pred})
        history.loc[date] = {'temp_max':t_pred,'mes':mes,'hist_mean':hist_mean,'threshold':hist_mean+threshold_delta,'heat_label':int(t_pred>=hist_mean+threshold_delta),**lags}
    return pd.DataFrame(preds).set_index('date')

# Previsão de onda de calor em período
def predict_heat_wave(start, end, daily_df, regressor, classifier):
    df = forecast_daily_temp(start, end, daily_df, regressor)
    df['mes'] = df.index.month
    df['hist_mean'] = df['mes'].map(daily_df['hist_mean'].groupby(daily_df.index.month).first())
    for lag in lags_daily:
        df[f'max_lag_{lag}d'] = df['temp_max_pred'].shift(lag)
    features = ['mes','hist_mean'] + [f'max_lag_{lag}d' for lag in lags_daily]
    Xp = df.dropna(subset=features)[features]
    df = df.loc[Xp.index]
    df['heat_pred'] = classifier.predict(Xp)
    return df

# --- Execução do app ---
# Carrega dados e modelos
historico, daily, reg_model, clf_model = load_data_and_models()

# Carrega shapefile de distritos e ajusta CRS
gdf_distritos = gpd.read_file("../data/raw/SIRGAS_SHP_distrito.shp")
gdf_distritos = gdf_distritos.set_crs("EPSG:31983", allow_override=True)
gdf_distritos = gdf_distritos.to_crs("EPSG:4326")
geo_gdf = gdf_distritos

st.title('Previsão de Temperatura e Ondas de Calor em SP')
start = st.sidebar.date_input('Data inicial', value=pd.to_datetime('today'))
end = st.sidebar.date_input('Data final', value=start + pd.Timedelta(days=horizon_default-1))

with st.spinner('Processando previsões...'):
    temp_pred = forecast_daily_temp(start, end, daily, reg_model)
    heat_df = predict_heat_wave(start, end, daily, reg_model, clf_model)

st.subheader('Previsão diária de temperatura')
st.dataframe(temp_pred)
st.subheader('Dias com previsão de onda de calor')
st.write(heat_df.index.date)

flag = 1 if not heat_df.empty else 0
mapa = folium.Map(location=[-23.55,-46.63], zoom_start=11)
colormap = folium.LinearColormap(['blue','red'], vmin=0, vmax=1)
for _, row in geo_gdf.iterrows():
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, val=flag: {
            'fillColor': colormap(val),
            'color': 'black', 'weight': 0.5, 'fillOpacity': 0.6
        }
    ).add_to(mapa)
colormap.caption = 'Nenhuma onda (azul) vs. Onda (vermelho)'
mapa.add_child(colormap)

st.subheader('Mapa de Onda de Calor (por distrito)')
st_folium(mapa, width=700)
