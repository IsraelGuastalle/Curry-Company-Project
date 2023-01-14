import streamlit as st
from PIL import Image

#Função para juntar no streamlit. Ele entende que ele precisa buscar algo em uma pasta pages.

st.set_page_config(
    page_title="Home",
    page_icon="📈"
    #,layout="wide"
)

#image_path = r'C:\Users\israelguastalle-sao\repos_cds\FTC\train_prog_python\arquivos_python\streamlit\logo3.png'
#image = Image.open( image_path )
#st.sidebar.image( image, width=120)

#============================================
# Para Cloud
#============================================

image = Image.open( 'logo3.png' )
st.sidebar.image( image, width=120)

#============================================

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write('# Curry Company Growth Dashboard')

st.markdown( 
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semaais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    
    
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    
    - Visão Restaurante:
        - Indicadores semaias de crescimento dos restauranete.
    
    ### Ask for Help:
        - Israel Guastalle  
    
    """)


 
















