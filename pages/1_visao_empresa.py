
# Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas necessárioas

import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

# Ajustar tela para wide
st.set_page_config( page_title= 'Visão Empresa', page_icon='📈', layout='wide')

#============================================
# Funções
#============================================

def clean_code( df1 ):
    
    """
        Esta Função tem a responsabilidade de limpar o dataframe
    
        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudanção do tipo das colunas de dados
        3. Remoção dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variavel numérica )
        
        Input: Dataframe
        Output: Dataframe
    
    """    

    # 1. convertando a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. convertando a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3. convertando a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 6. Removendo os espacos dentro de strings/texto/object

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return ( df1 )

def order_metric( df1 ):
    
    #1. Quantidade de pedidos por dia (barra)

    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    fig.update_layout(showlegend=False, height=600)
                      
    # margin={'1': 20, 'r': 60, 't': 0, 'b': 0}                      
    # ,legend=dict(yanchor="top", y=0.99, xanchor="right", z=0.99), barmode='stack')        
    # fig.update_traces(textposition='inside', textinfo='label+percent')
    return fig

def traffic_order_share( df1 ):
            
    #3. Distribuição dos pedidos por tipo de tráfego (Pizza)

    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()
    df_aux['percent'] = round(df_aux['ID'] / df_aux['ID'].sum(),3)
    fig = px.pie(df_aux, values='percent', names='Road_traffic_density',height=500)
    return fig

def traffic_order_city( df1 ):
            
    #4. Comparação do volume de pedidos por cidade e tipo de tráfego (Bolhas)          
    cols = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City', height=500)
    return fig

def order_by_week( df1 ):
    
    #2. Quantidade de pedidos por semana (linha)
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    df_aux = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID', height=500)
    return fig

def order_share_by_week( df1 ):
        
     #5. A quantidade de pedidos por entregador por semana (linha)

    df_aux01 = df1.loc[:, ['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux02 = df1.loc[:, ['week_of_year','Delivery_person_ID']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['entrega_por_entregador'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='entrega_por_entregador', height=500)
    return fig

def country_maps( df1 ):
    
    #6. A localização central de cada cidade por tipo de tráfego (Mapa)
    df_aux = df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]                         .groupby(['City','Road_traffic_density']).median().reset_index()

    # Usamos o head para não travar o pc, pois são 41 mil pinos rs
    df_aux = df_aux.head(10)
    map_ = folium.Map()

    #Tem que fazer um for com iterrows (critério de quem criou) para ele plotar todos
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], 
                           location_info['Delivery_location_longitude']],
                           popup=location_info[['City','Road_traffic_density']] ).add_to(map_)

    folium_static( map_, width=1024, height=600 )

    return None

#----------------------------------------------------- Inicio da Estrutura Lógica do Código ---------------------------------------------

#============================================
# Importar Dataset
#============================================

#df = pd.read_csv(r'C:\Users\israelguastalle-sao\repos_cds\FTC\train_prog_python\dataset\train.csv')
#df1 = clean_code( df )

#============================================
# Importar Para Cloud
#============================================

df = pd.read_csv( 'dataset\train.csv' )
df1 = clean_code( df )

#============================================
# BARRA LATERAL NO STREAMLIT
#============================================


st.header( 'Marketplace - Visão Entregadores' )

#----- Inserindo um Logo -----


#image_path = r'C:\Users\israelguastalle-sao\repos_cds\FTC\train_prog_python\arquivos_python\streamlit\logo3.png'
#image = Image.open( image_path )
#st.sidebar.image( image, width=120)

#============================================
# Para Cloud
#============================================

image = Image.open( 'logo3.png' )
st.sidebar.image( image, width=120)

#============================================


#----- Criando barra lateral de filtros -----


st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )

st.sidebar.markdown( """---""" )

st.sidebar.markdown('## Selecione uma data limite')


#----- Criando um filro de datas -----

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY') 

st.sidebar.markdown("""---""")

#----- Criando um filro de Tipo de Tráfego-----

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Trânsito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

#----- Criando um filro de Tipo de Clima-----

clima_options = st.sidebar.multiselect('Quais condições climáticas?', 
                                       ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
                                       default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Cloudy', 'conditions Fog', 'conditions Windy'])

#-------------------------------------------

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Israel Guastalle')

#-----Ativando o filtro de Datas-----

linhas_selecioandas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecioandas, :]


#-----Ativando o filtro de transito-----

linhas_selecioandas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecioandas, :]

#-----Ativando o filtro de clima-----

linhas_selecionadas = df1['Weatherconditions'].isin( clima_options )
df1 = df1.loc[linhas_selecionadas, :]

#st.dataframe ( df1 )


#============================================
# LAYOUT NO STREAMLIT
#============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','Visão Tática','Visão Geográfica'] )

with tab1: 
          
    with st.container():
        
        fig = order_metric( df1 )
        st.header( 'Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )   
           
    with st.container():
    
        col1, col2 = st.columns( 2 )
        
        with col1:
            
            fig = traffic_order_share( df1 )
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)                
                
        with col2:

            fig = traffic_order_city( df1 )
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)           
            
with tab2: 
  
    with st.container():
    
        st.header('Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
      
        st.header('Order Share Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)        
    
with tab3: 

    st.header('Country Maps')
    country_maps( df1 )
    

























