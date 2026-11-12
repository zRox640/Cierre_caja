import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Gestor de Pagos", page_icon="💰", layout="centered")

def realizar_calculos(df):
    if df.shape[1] < 6:
        st.error("El archivo tiene menos de 6 columnas.")
        return None

    try:
        # Limpieza Columna E (Indice 4 - Tipo de Pago)
        df.iloc[:, 4] = df.iloc[:, 4].astype(str).str.lower().str.strip()
        
        # Limpieza Columna F (Indice 5 - Montos)
        col_f_texto = df.iloc[:, 5].astype(str).str.replace("'", "", regex=False).str.replace(".", "", regex=False)
        df.iloc[:, 5] = pd.to_numeric(col_f_texto, errors='coerce').fillna(0)

        # Filtros base
        mask_efectivo = df.iloc[:, 4].str.contains("efectivo", na=False)
        mask_debito = df.iloc[:, 4].str.contains("debito|débito", na=False)
        
        # Sumas originales
        total_efectivo = df.loc[mask_efectivo].iloc[:, 5].sum()
        total_debito = df.loc[mask_debito].iloc[:, 5].sum()
        
        # --- LÓGICA DE BOLETAS CORREGIDA ---
        col_a_texto = df.iloc[:, 0].astype(str).str.lower().str.strip()
        
        # Agregamos explícitamente el guion "-" a la lista de cosas que consideramos "vacío"
        mask_a_vacia = col_a_texto.isin(["", "nan", "none", "nat", "-"])
        
        # Columna B: verificamos que contenga un número válido
        col_b_texto = df.iloc[:, 1].astype(str).str.replace("'", "", regex=False).str.replace(".", "", regex=False)
        mask_b_numero = pd.to_numeric(col_b_texto, errors='coerce').notna()
        
        # Sumamos donde se cumplen todas las condiciones
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

# --- INTERFAZ VISUAL ---
try:
    image = Image.open('fondo.jpg')
    st.image(image, width=100) 
except:
    pass 

st.title("Procesador de Ventas Web")

archivo_subido = st.file_uploader("Elige tu archivo Excel", type=['xlsx', 'xls'])

if archivo_subido is not None:
    with st.spinner('Calculando...'):
        try:
            df = pd.read_excel(archivo_subido, header=None)
            
            # --- MODO DEBUG (RAYOS X) ---
            # Esto mostrará las primeras 15 filas de tu Excel directo en la página web
            # Así podremos ver si la columna 0 realmente está vacía y si la 1 tiene el número
            with st.expander("🔍 Ver datos leídos (Modo Rayos X)"):
                st.dataframe(df.head(15))
            # ---------------------------

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
                
                st.markdown("---")
                f_efectivo_boleta = "${:,.0f}".format(totales['efectivo_boleta']).replace(",", ".")
                st.info(f"🧾 **Detalle Especial:** Efectivo por **Boleta** es de **{f_efectivo_boleta}**")
                
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo: {e}")
