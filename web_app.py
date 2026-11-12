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
    if df.shape[1] < 6:
        st.error("El archivo tiene menos de 6 columnas.")
        return None

    try:
        # Limpieza Columna E (Indice 4 - Tipo de Pago)
        df.iloc[:, 4] = df.iloc[:, 4].astype(str).str.lower().str.strip()
        
        # Limpieza Columna F (Indice 5 - Montos)
        col_f_texto = df.iloc[:, 5].astype(str)
        col_f_texto = col_f_texto.str.replace("'", "", regex=False)
        col_f_texto = col_f_texto.str.replace(".", "", regex=False)
        df.iloc[:, 5] = pd.to_numeric(col_f_texto, errors='coerce').fillna(0)

        # Filtros base (Efectivo y Débito)
        mask_efectivo = df.iloc[:, 4].str.contains("efectivo", na=False)
        mask_debito = df.iloc[:, 4].str.contains("debito|débito", na=False)
        
        # Sumas originales
        total_efectivo = df.loc[mask_efectivo].iloc[:, 5].sum()
        total_debito = df.loc[mask_debito].iloc[:, 5].sum()
        
        # --- NUEVA LÓGICA: Detección de Boletas ---
        # Condición 1: Columna A (Índice 0) está vacía (pandas lo lee como NaN o texto vacío)
        mask_a_vacia = df.iloc[:, 0].isna() | (df.iloc[:, 0].astype(str).str.strip() == "") | (df.iloc[:, 0].astype(str).str.lower() == "nan")
        
        # Condición 2: Columna B (Índice 1) tiene un número
        # Al forzar la conversión a número, si tiene éxito no será un valor nulo (notna)
        mask_b_numero = pd.to_numeric(df.iloc[:, 1], errors='coerce').notna()
        
        # Sumamos donde sea Efectivo Y Columna A esté vacía Y Columna B sea número
        mask_es_boleta = mask_a_vacia & mask_b_numero
        total_efectivo_boleta = df.loc[mask_efectivo & mask_es_boleta].iloc[:, 5].sum()
        
        return {
            "efectivo": total_efectivo, 
            "debito": total_debito, 
            "total": total_efectivo + total_debito,
            "efectivo_boleta": total_efectivo_boleta
        }

    except Exception as e:
        st.error(f"Error procesando los datos: {str(e)}")
        return None

# --- 3. INTERFAZ VISUAL ---

try:
    image = Image.open('fondo.jpg')
    st.image(image, width=100) 
except:
    pass 

st.title("Procesador de Ventas Web")
st.write("Sube tu archivo Excel para calcular los totales.")

archivo_subido = st.file_uploader("Elige tu archivo Excel", type=['xlsx', 'xls'])

if archivo_subido is not None:
    with st.spinner('Calculando...'):
        try:
            df = pd.read_excel(archivo_subido, header=None)
            totales = realizar_calculos(df)
            
            if totales:
                st.markdown("---")
                st.subheader("📊 Resultados Generales")
                
                col1, col2, col3 = st.columns(3)
                
                f_efectivo = "${:,.0f}".format(totales['efectivo']).replace(",", ".")
                f_debito = "${:,.0f}".format(totales['debito']).replace(",", ".")
                f_total = "${:,.0f}".format(totales['total']).replace(",", ".")

                with col1:
                    st.metric(label="💵 Efectivo", value=f_efectivo)
                with col2:
                    st.metric(label="💳 Débito", value=f_debito)
                with col3:
                    st.metric(label="💰 TOTAL", value=f_total)
                
                # --- SECCIÓN: Efectivo en Boletas ---
                st.markdown("---")
                f_efectivo_boleta = "${:,.0f}".format(totales['efectivo_boleta']).replace(",", ".")
                
                st.info(f"🧾 **Detalle Especial:** El total de Efectivo ingresado exclusivamente por **Boleta** es de **{f_efectivo_boleta}**")
                
                st.success("Cálculo realizado exitosamente.")
                
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")
