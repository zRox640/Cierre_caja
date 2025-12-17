import streamlit as st
import pandas as pd
from PIL import Image

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Gestor de Pagos",
    page_icon="💰",
    layout="centered"
)

# --- 2. LÓGICA MATEMÁTICA ---
def realizar_calculos(df):
    # Validación básica
    if df.shape[1] < 6:
        st.error("El archivo tiene menos de 6 columnas.")
        return None

    try:
        # Limpieza Columna E (Indice 4)
        df.iloc[:, 4] = df.iloc[:, 4].astype(str).str.lower().str.strip()
        
        # Limpieza Columna F (Indice 5)
        col_f_texto = df.iloc[:, 5].astype(str)
        col_f_texto = col_f_texto.str.replace("'", "", regex=False)
        col_f_texto = col_f_texto.str.replace(".", "", regex=False)
        df.iloc[:, 5] = pd.to_numeric(col_f_texto, errors='coerce').fillna(0)

        # Sumas
        total_efectivo = df.loc[df.iloc[:, 4].str.contains("efectivo", na=False)].iloc[:, 5].sum()
        total_debito = df.loc[df.iloc[:, 4].str.contains("debito|débito", na=False)].iloc[:, 5].sum()
        
        return {"efectivo": total_efectivo, "debito": total_debito, "total": total_efectivo + total_debito}

    except Exception as e:
        st.error(f"Error procesando los datos: {str(e)}")
        return None

# --- 3. INTERFAZ VISUAL ---

# Intentar cargar logo si existe (fondo.jpg)
try:
    image = Image.open('fondo.jpg')
    st.image(image, width=100) 
except:
    pass 

st.title("Procesador de Ventas Web")
st.write("Sube tu archivo Excel para calcular los totales.")

# WIDGET DE CARGA
archivo_subido = st.file_uploader("Elige tu archivo Excel", type=['xlsx', 'xls'])

if archivo_subido is not None:
    with st.spinner('Calculando...'):
        try:
            # Leer el archivo
            df = pd.read_excel(archivo_subido, header=None)
            
            # Calcular
            totales = realizar_calculos(df)
            
            if totales:
                st.markdown("---")
                st.subheader("📊 Resultados")
                
                # Columnas para diseño bonito
                col1, col2, col3 = st.columns(3)
                
                # Formatear números
                f_efectivo = "${:,.0f}".format(totales['efectivo']).replace(",", ".")
                f_debito = "${:,.0f}".format(totales['debito']).replace(",", ".")
                f_total = "${:,.0f}".format(totales['total']).replace(",", ".")

                with col1:
                    st.metric(label="💵 Efectivo", value=f_efectivo)
                
                with col2:
                    st.metric(label="💳 Débito", value=f_debito)
                    
                with col3:
                    st.metric(label="💰 TOTAL", value=f_total)
                    
                st.success("Cálculo realizado exitosamente.")
                
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")