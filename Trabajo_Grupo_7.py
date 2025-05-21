# Importamos las bibliotecas necesarias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

##########################################################
# CONFIGURACIÓN DEL DASHBOARD
##########################################################

# Configuración básica de la página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Configuración simple para los gráficos
sns.set_style("whitegrid")

# Título principal del dashboard
st.title('📊 Dashboard Supermarket Sales')

##################################################
# CARGA DE DATOS
##################################################

# Función para cargar datos con cache para mejorar rendimiento
@st.cache_data
def cargar_datos():
    # Carga el archivo CSV con datos macroeconómicos
    df = pd.read_csv("data.csv")
    # Asegúrate de quitar espacios en los nombres de columnas si es necesario
    df = df.rename(columns=lambda x: x.strip())

    # Convertir Fecha a datetime
    df['Date'] = pd.to_datetime(df['Date'])
    #df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')#
    return df

# Cargamos los datos
df = cargar_datos()

##############################################
# CONFIGURACIÓN DE LA BARRA LATERAL
##############################################

# Simplificamos la barra lateral con solo lo esencial
st.sidebar.header('Filtros del Dashboard')
##############################################

#### FILTROS###

st.sidebar.header('Filtros del Dashboard')
F_linea = st.sidebar.multiselect(
    "Líneas de Producto",
    options=df["Product line"].unique().tolist(),
    default=df["Product line"].unique().tolist(),
    help="Selecciona la o las categorías que se desean visualizar"
)

# FILTRO APLICADO
if F_linea:
    df_filtrado = df[df["Product line"].isin(F_linea)]
else:
    st.info("Seleccione al menos una línea de producto.")
    st.stop()




    ##### PRIMERA LINEA VISUALIZACIONES####

# Sección: Ventas e ingreso
st.subheader('Ingresos Supermarket Sales')
#Declaración columnas para dividir primera parte de graficos
c1,c2=st.columns([50,50])
with c1:

    Fig1=plt.figure(figsize=(10,5))
    df.groupby('Date')['Total'].count().plot(kind='line')
    plt.xlabel('Fecha')
    plt.title('Evolución de las ventas totales en el tiempo')
    plt.ylabel('Monto total de Ventas (USD)')
    plt.grid(True)
    st.pyplot(Fig1) 
    st.write("El gráfico muestra la evolución de las ventas totales a lo largo del tiempo. Se observa que las ventas diarias no siguen una tendencia clara de crecimiento o disminución sostenida, lo que sugiere un comportamiento relativamente estable de la demanda durante el período analizado. No obstante, se identifican varios picos significativos de ventas, especialmente durante los meses de febrero y marzo. Estos aumentos podrían estar relacionados con promociones, eventos especiales o días de alta demanda, como fines de semana o fechas festivas. Tras estos picos, se observa una disminución temporal en las ventas, lo cual es un comportamiento típico luego de jornadas con alta actividad comercial.")
with c2:
    # Agrupar el total vendido por línea de producto
    ingresos_por_producto = df_filtrado.groupby("Product line")["Total"].sum().sort_values()
    colores = sns.color_palette("pastel", n_colors=len(ingresos_por_producto))
    # Crear gráfico con colores distintos por barra
    Fig2 = plt.figure(figsize=(10, 5))
    plt.barh(ingresos_por_producto.index, ingresos_por_producto.values, color=colores)
    plt.title('Ingresos por Línea de Producto')
    plt.xlabel('Total Vendido (USD)')
    plt.ylabel('Línea de Producto')
    plt.tight_layout()
    st.pyplot(Fig2)
    st.write("El gráfico permite identificar que la línea Food and Beverages genera el mayor ingreso total, mientras que Health and Beauty presenta el menor. Esta información es crucial para definir estrategias comerciales, ya que permite focalizar esfuerzos en las líneas más rentables o reforzar aquellas con menor desempeño para equilibrar la oferta y la demanda.")
### sector de comportamiento clientes
st.subheader('Comportamiento Clientes')
#Declaración columnas para dividir primera parte de graficos
c1,c2=st.columns([50,50])
with c1:
    Fig3 = plt.figure(figsize=(8, 4))
    sns.histplot(data=df, x='Rating', kde=True, bins=20, color='skyblue')
    plt.title('Distribución de la Calificación de Clientes')
    plt.xlabel('Calificación (Rating)')
    plt.ylabel('Frecuencia')
    plt.tight_layout()
    st.pyplot(Fig3)
    st.write('La distribución muestra que la mayoría de las calificaciones otorgadas por los clientes se concentran entre los valores de 6 y 8. Esto sugiere que, si bien no se alcanza con frecuencia la puntuación máxima, la percepción general del servicio y productos ofrecidos es positiva. Lo cual evidencia una oportunidad de mejora en la experiencia del cliente para incrementar los niveles de satisfacción hacia rangos superiores.')
with c2:
    Fig4 = plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x='Customer type', y='Total', palette='Set2')
    plt.title('Comparación del Gasto por Tipo de Cliente')
    plt.xlabel('Tipo de Cliente')
    plt.ylabel('Total Vendido (USD)')
    plt.tight_layout()
    st.pyplot(Fig4)
    st.write('En el gráfico se puede visualizar que los clientes del tipo Member tienden a realizar un mayor gasto promedio en comparación con los clientes Normal. No obstante, se identifican valores atípicos elevados en ambos grupos, lo que indica que clientes Normal también pueden efectuar compras significativas. Esta información puede ser útil para diseñar campañas de fidelización dirigidas a ambos segmentos.')
#Comportamiento de ingresos brutos en la tienda
st.subheader('Comportamiento ingresos brutos')
c1,c2=st.columns([50,50])
with c1:
    Fig5=plt.figure(figsize=(8,5))
    sns.scatterplot(data=df_filtrado, x='cogs', y='gross income')
    plt.title('Relación entre el costo de los productvos vendidos e ingreso Bruto')
    plt.xlabel('Total costo productos')
    plt.ylabel('Ingreso Bruto')
    st.pyplot(Fig5)
    st.write('El gráfico muestra una relación lineal positiva entre el costo de los productos vendidos (cogs) y el ingreso bruto (gross income), lo cual sugiere que el ingreso se genera de forma proporcional al costo. Adicionalmente, no se observan variaciones significativas fuera de la línea, por lo cual se puede asumir que los ingresos fueron relativamente proporcionales al costo.')
with c2:
    # Agrupar por Sucursal y Línea de Producto, sumando el ingreso bruto
    df_grouped = df_filtrado.groupby(['Branch', 'Product line'])['gross income'].sum().unstack(fill_value=0)

    # Crear gráfico de barras apiladas
    fig6,ax= plt.subplots(figsize=(10, 6))

    df_grouped.plot(kind='bar',
                    stacked=True,
                    ax=ax,
                    colormap='Pastel2')  
    ax.tick_params(axis='x', rotation=0)
    ax.set_title('Ingreso Bruto por Sucursal y Línea de Producto')
    ax.set_xlabel('Sucursal')
    ax.set_ylabel('Ingreso Bruto (USD)')
    ax.legend(title='Línea de Producto', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig6)
    st.write('El gráfico evidencia que la sucursal C genera mayores ingresos brutos totales. Además, se observa que en cada sucursal hay líneas de productos predominantes: Home and Lifestyle y Sports and Travel en la sucursal A; Health and Beauty y Sports and Travel en la B; y una distribución más equilibrada en la C. Estas diferencias podrían estar relacionadas con características demográficas o de consumo en las zonas geográficas donde operan las sucursales.')

#Relación variables y metodos de pagos utilizados
st.subheader('Correlación númerica y Métodos de pago utilizados')
c1,c2=st.columns([50,50])
with c1:
    #primero se creara un nuevo df el cual solamente contendra las variables númericas, ya que para los modelos matematicos solamente se trabaja con valores númericos.
    df_correlación=df.drop(['Branch','Customer type','Gender','Product line','Date','Time','Invoice ID','Payment','City','gross margin percentage'], axis=1)
    
    
    Fig7=plt.figure(figsize=(10,10))
    sns.heatmap(df_correlación.corr(), annot=True,cmap='RdYlGn',square=True)
    plt.title('Matriz de correlación de variables numéricas')    
    st.pyplot(Fig7)
    st.write('El gráfico de correlación númerica, podemos interpretar que existen correlaciones muy fuertes entre las variables Total, cogs e ingreso bruto, lo cual es coherente, ya que el total de venta se basa en el precio por cantidad, y tanto el costo como el ingreso bruto dependen directamente de esos valores. En cambio, variables como Rating tienen correlación prácticamente nula con las demás, lo que indica que la calificación del cliente no está relacionada directamente con el monto de la venta ni la cantidad de productos comprados, dado que es una apreciación subjetiva del cliente.')

with c2:
    metodos_pago = df['Payment'].value_counts().reset_index()
    metodos_pago.columns = ['Método de Pago', 'Cantidad']
    fig8 = px.pie(metodos_pago,
                        names='Método de Pago',
                        values='Cantidad',
                        title='Distribución de Métodos de Pago',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2)

    fig8.update_traces(textinfo='percent+label')
    st.plotly_chart(fig8)
    st.write('El gráfico muestra que el método de pago mas utilizado por los clientes de la tienda de conveniencia son las Ewallet, seguidas del efectivo y finalmente las tarjetas de crédito, esta infomación es relevante para realizar futuras promociones de acuerdo a los medios de pago utilizados por los clientes.')