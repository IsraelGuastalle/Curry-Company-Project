
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
st.set_page_config( page_title= 'Visão Entregadores', page_icon='📈', layout='wide')

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
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return ( df1 )

#Colocamos o parâmetro top_asc para poder reutilizar a função
def top_delivers( df1, top_asc ):          

    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
              .groupby( [ 'City', 'Delivery_person_ID' ])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending=top_asc) 
              .reset_index())
    
    aux_01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    aux_02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    aux_03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [aux_01, aux_02, aux_03] ).reset_index( drop=True )
            
    return df3         

#============================================
# Importar Dataset
#============================================

#df = pd.read_csv(r'C:\Users\israelguastalle-sao\repos_cds\FTC\train_prog_python\dataset\train.csv')
#df1 = clean_code( df )

#============================================
# Importar Para Cloud
#============================================

df = pd.read_csv( 'dataset/train.csv' )
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','_','_'] )

with tab1:
    
    #Primeira Linha--------------------------------------
    #Não vale a pena fazer função por ser poucas linhas
    with st.container():
        
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        
        with col1:
           
            #1. A maior idade dos entregadores          
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade )
            
        with col2:
            
            #1. A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade )
              
        with col3:
             
            #2. A melhor condição de veículos.

            melhor_concicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_concicao)
        
        with col4:
            
            #2. A pior condição de veículos.
            
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)            
    
    #Segunda Linha--------------------------------------
    with st.container(): 
        
        st.markdown("""---""")
        st.title( 'Avaliações' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Avaliação Média por Entregador' )
            
            #3. A avaliação média por entregador.

            #average_per_deliver = ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
            #                           .groupby(['Delivery_person_ID'])
            #                           .mean()
            #                           .reset_index() )
            
            #st.dataframe( average_per_deliver, height=500 )
            #st.dataframe( average_per_deliver, width=700,  height=500)         
            
            average_per_deliver = ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                       .groupby(['Delivery_person_ID'])
                                       .agg( {'Delivery_person_Ratings': ['mean']} ))
                                   
            average_per_deliver.columns = ['Ratings_mean']
            average_per_deliver = average_per_deliver.reset_index()                      
            
            st.dataframe( average_per_deliver, height=500 )
            
        
        with col2:
            
            #Linha1 da col2
            st.markdown( '##### Avaliação Média por Trânsito' )
            
            #4. A avaliação média e o desvio padrão por tipo de tráfego.

            average_by_trafic =  ( df1.loc[:, ['Road_traffic_density','Delivery_person_Ratings']]
                                      .groupby(['Road_traffic_density'])
                                      .agg( {'Delivery_person_Ratings': ['mean','std']}) )    

            average_by_trafic.columns = ['Ratings_mean', 'Ratings_std']
            average_by_trafic = average_by_trafic.reset_index()
            
            st.dataframe( average_by_trafic )
            
            #5. A avaliação média e o desvio padrão por condições climáticas.

            cond_clim = ( df1.loc[:, ['Weatherconditions','Delivery_person_Ratings']]
                             .groupby(['Weatherconditions'])
                             .agg( {'Delivery_person_Ratings': ['mean', 'std'] }) )

            cond_clim.columns = ['Ratings_mean','Ratings_std']
            cond_clim = cond_clim.reset_index()

            st.dataframe( cond_clim )
            
            
    #Terceira Linha:
    with st.container():
        
        st.markdown("""---""")
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            
            #usamos a mesma função com parâmetros diferentes
            st.markdown( '##### Top Entregadores Mais Rápidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3, height=500)       
           
        with col2:
            
            #usamos a mesma função com parâmetros diferentes
            st.markdown( '##### Top Entregadores Mais Lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3, height=500)
 

