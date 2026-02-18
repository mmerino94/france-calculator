import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# IMPORT FUNCTIONS
from tu_script import procesar_archivo, convertir_a_plantilla


# ============================================
# INITIAL CONFIGURATION
# ============================================

st.set_page_config(
    page_title="France Calculator Automation",
    page_icon="📊",
    layout="wide"
)

st.title("📊 France Calculator Automation")

st.markdown("""
This tool allows you to:

• Upload multiple France Template Excel files  
• Automatically process data from IGT and competitors  
• Generate the final output in corporate template format  
• View KPIs  
• Download results ready for upload  
""")


st.divider()


# ============================================
# SESSION STATE INIT
# ============================================

if "processed" not in st.session_state:
    st.session_state.processed = False

if "df_out_final" not in st.session_state:
    st.session_state.df_out_final = None

if "bloques2_final" not in st.session_state:
    st.session_state.bloques2_final = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


# ============================================
# FILE UPLOADER (dynamic key)
# ============================================

uploaded_files = st.file_uploader(
    "Select Excel files",
    accept_multiple_files=True,
    type=["xlsx"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if not uploaded_files and not st.session_state.processed:
    st.info("Waiting for Excel files...")
    st.stop()


# ============================================
# PROCESS BUTTON
# ============================================

if uploaded_files and not st.session_state.processed:

    if st.button("🚀 Process files", use_container_width=True):

        lista_bloques1 = []
        lista_bloques2 = []

        progress_bar = st.progress(0)
        status_text = st.empty()

        with st.spinner("Processing files..."):

            for i, file in enumerate(uploaded_files):

                status_text.write(f"Processing: {file.name}")

                try:

                    temp_path = f"temp_{file.name}"

                    df = pd.read_excel(file)
                    df.to_excel(temp_path, index=False)

                    b1, b2 = procesar_archivo(temp_path)

                    lista_bloques1.append(b1)
                    lista_bloques2.append(b2)

                    os.remove(temp_path)

                except Exception as e:

                    st.error(f"Error processing {file.name}")
                    st.exception(e)

                progress_bar.progress((i+1)/len(uploaded_files))


        bloques1_final = pd.concat(lista_bloques1, ignore_index=True)
        bloques2_final = pd.concat(lista_bloques2, ignore_index=True)

        bloques2_final["Month"] = pd.to_datetime(
            bloques2_final["Month"]
        ).dt.strftime("%Y-%m")

        df_out_final = convertir_a_plantilla(bloques1_final)


        # SAVE TO SESSION STATE
        st.session_state.df_out_final = df_out_final
        st.session_state.bloques2_final = bloques2_final
        st.session_state.processed = True


        # AUTOMATIC LOCAL EXPORT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_folder = "outputs"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        df_out_final.to_excel(
            f"{output_folder}/FranceCalculator_INPUT_FULL_{timestamp}.xlsx",
            index=False
        )

        bloques2_final.to_excel(
            f"{output_folder}/FranceCalculator_BLOCK2_FULL_{timestamp}.xlsx",
            index=False
        )

        st.success("Processing completed successfully")

        st.rerun()


# ============================================
# DISPLAY RESULTS
# ============================================

if st.session_state.processed:

    df_out_final = st.session_state.df_out_final
    bloques2_final = st.session_state.bloques2_final

    st.divider()

    st.subheader("⬇️ Download results")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    buffer1 = io.BytesIO()
    df_out_final.to_excel(buffer1, index=False)

    st.download_button(
        label="Download FranceCalculator_INPUT_FULL.xlsx",
        data=buffer1.getvalue(),
        file_name=f"FranceCalculator_INPUT_FULL_{timestamp}.xlsx",
        use_container_width=True
    )

    buffer2 = io.BytesIO()
    bloques2_final.to_excel(buffer2, index=False)

    st.download_button(
        label="Download FranceCalculator_BLOCK2_FULL.xlsx",
        data=buffer2.getvalue(),
        file_name=f"FranceCalculator_BLOCK2_FULL_{timestamp}.xlsx",
        use_container_width=True
    )


    # ============================================
    # RESET BUTTON
    # ============================================

    st.divider()

    if st.button("🔄 Reset application", use_container_width=True):

        st.session_state.processed = False
        st.session_state.df_out_final = None
        st.session_state.bloques2_final = None

        st.session_state.uploader_key += 1

        st.rerun()


    # ============================================
    # KPIs
    # ============================================

    st.divider()

    st.subheader("📈 KPIs")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total machines", f"{len(df_out_final):,}")
    col2.metric("Total casinos", df_out_final["CasinoName INPUT"].nunique())
    col3.metric("Average CIPUPD per machine", f"{df_out_final['CIPUPD'].mean():,.0f}")
    col4.metric("Average NWPUPD per machine", f"{df_out_final['NWPUPD'].mean():,.0f}")
    col5.metric("Average GPPUPD per machine", f"{df_out_final['GPPUPD'].mean():,.0f}")


    # ============================================
    # DATA PREVIEW
    # ============================================

    st.divider()

    st.subheader("🔎 Data Preview")

    st.dataframe(
        df_out_final.head(50),
        use_container_width=True
    )

    st.subheader("🔎 Competition Preview")

    st.dataframe(
        bloques2_final.head(50),
        use_container_width=True
    )
