# Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas necessárioas

import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static


# Ajustar tela para wide
st.set_page_config( page_title= 'Visão Restaurante', page_icon='📈', layout='wide')


#============================================
# Funções
#===========================================


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
            
def distance( df1, fig ):
            
    #2. A distância média dos resturantes e dos locais de entrega (é uma coluna)
    
    if fig == False:
    
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

        df1['distance'] = df1.loc[:, cols].apply( lambda x:  
                                                    haversine( 
                                                        ( x['Delivery_location_latitude'], x['Delivery_location_longitude'] ),
                                                        ( x['Restaurant_latitude'], x['Restaurant_longitude'])), axis=1 )

        avg_distance = np.round(df1['distance'].mean(), 2)
        
        return avg_distance
    
    else:
        
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

        df1['distance'] = df1.loc[:, cols].apply( lambda x:  
                                                haversine( 
                                                    ( x['Delivery_location_latitude'], x['Delivery_location_longitude'] ),
                                                    ( x['Restaurant_latitude'], x['Restaurant_longitude'])), axis=1 )

        avg_distance = df1.loc[:, ['City','distance']].groupby( ['City'] ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

        return fig
        
        
        



def avg_std_time_delivery( df1, op, festival ):
                
                """
                
                    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
                    Parametros:
                        Input:
                            - df: Dataframe com os dados necessários para o cálculo
                            - op: Tipo de operação que precisa ser calculado
                                'avg_time': Calcula o tempo médio
                                'std_time': Calcula o desvio padrão do tempo
                        Output:     
                            - df: Dataframe com 2 colunas e 1 linha
                    
                """
            
                # 6. O tempo médio de entrega durantes os Festivais.
                
                df_aux = ( df1.loc[:, ['Time_taken(min)','Festival']]
                              .groupby( ['Festival'] )
                              .agg( {'Time_taken(min)': ['mean','std']} ))

                df_aux.columns = ['avg_time','std_time']

                df_aux = df_aux.reset_index()
                linhas_selecionadas = df_aux['Festival'] == festival
                df_aux = df_aux.loc[linhas_selecionadas, op]
                df_aux = np.round(df_aux, 2)
                
                return df_aux                

def avg_std_time_graph( df1 ):               

                #3. O tempo médio e o desvio padrão de entrega por cidade.

                aux = df1.loc[:, ['City','Time_taken(min)']].groupby( ['City'] ).agg( {'Time_taken(min)': ['mean','std']} )
                aux.columns = ['avg_time','std_time']
                aux = aux.reset_index()

                fig = go.Figure()
                fig.add_trace( go.Bar( name='Control', x=aux['City'], y=aux['avg_time'], error_y=dict( type='data', array=aux['std_time'])))
                fig.update_layout(barmode='group')    
                return fig           
            
            
def avg_time_on_traffic( df1 ):
            
                #5. O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.

                aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                           .groupby( ['City','Road_traffic_density'] )
                           .agg( {'Time_taken(min)': ['mean','std']} ))

                aux.columns = ['avg_time','std_time']
                aux = aux.reset_index()


                fig = px.sunburst(aux, path=['City','Road_traffic_density'], values='avg_time', 
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(aux['std_time'] ) )
            
                return fig           
            

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

tab1, tab2, tab3 = st.tabs (['Visão Gerencial','_','_'])

with tab1:
    
    with st.container():
        st.title( 'Overal Metrics' )
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
                  
            #1. A quantidade de entregadores únicos.

            unicos = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos',  unicos)            
            
        with col2:
            
            #A primeira chamada da distancia tem que ser false por causa da função. Aqui não quero figura, então mando ela direto pro else.
            avg_distance = distance( df1, fig=False)      
            col2.metric('Distância média das entregas', avg_distance)
            
        with col3:
            
            df_aux = avg_std_time_delivery( df1, 'avg_time', 'Yes')
            col3.metric( 'Tempo Médio de Entrega c/ Festival', df_aux)                
                        
        with col4:
            
            df_aux = avg_std_time_delivery( df1, 'std_time', 'Yes')
            col4.metric( 'STD de Entrega c/ Festival', df_aux)                   
           
                 
        with col5:
            
            df_aux = avg_std_time_delivery( df1, 'avg_time', 'No')
            col5.metric( 'Tempo Médio de Entrega s/ Festival', df_aux)             
            
        with col6: 
  
            df_aux = avg_std_time_delivery( df1, 'std_time', 'No')
            col6.metric( 'STD de Entrega s/ Festival', df_aux)       
           
        
    with st.container():
       
        st.markdown("""___""")
        st.title( 'Tempo Medio de Entrega por Cidade' )
        col1, col2 = st.columns( 2 )
        
        with col1:            

            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig )
            
        with col2:
            
            tmp = ( df1.loc[:,['City','Time_taken(min)', 'Type_of_order']]
                   .groupby( ['City','Type_of_order'] )
                   .agg( {'Time_taken(min)': ['mean','std']} ))


            tmp.columns = ['tmp_media','tmp_std']
            tmp = tmp.reset_index()

            st.dataframe( tmp )
                
    with st.container():
        st.markdown("""___""")
        st.title( 'Distribuição do tempo' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:

            fig = distance( df1, fig=True )
            st.plotly_chart( fig )
            
        with col2:

            fig = avg_time_on_traffic( df1 )
            st.plotly_chart( fig )

    
    
    
