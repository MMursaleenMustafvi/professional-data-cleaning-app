import pandas as pd
import json as js
import streamlit as st
import os

# --------- Page Config ---------
st.set_page_config(
    page_title="Professional Data Cleaning App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------- App Title ---------
st.markdown("<h1 style='text-align:center; color:#0B3D91;'>Data Cleaning App</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Step-by-step data cleaning with rename, description, and download</p>", unsafe_allow_html=True)
st.markdown("---")

# --------- File Input ---------
uploaded_file = st.text_input("Enter full file path (CSV, XLSX, JSON)")

df_dict = {}  # original data
cleaned_df_dict = {}  # cleaned sheets
sheet_name_selected = None
file_ext = None
df = None

if uploaded_file:
    file_ext = uploaded_file.split('.')[-1].lower()
    try:
        if file_ext == "csv":
            df_dict["Sheet1"] = pd.read_csv(uploaded_file)
        elif file_ext == "xlsx":
            xls = pd.ExcelFile(uploaded_file)
            sheet_name_selected = st.selectbox("Select Sheet to Clean", xls.sheet_names)
            df_dict[sheet_name_selected] = pd.read_excel(uploaded_file, sheet_name=sheet_name_selected)
        elif file_ext == "json":
            try:
                df_dict["Sheet1"] = pd.read_json(uploaded_file)
            except ValueError:
                with open(uploaded_file, "r", encoding="utf-8") as f:
                    data = js.load(f)
                df_dict["Sheet1"] = pd.json_normalize(data)
        else:
            st.error("Unsupported file format")
            df_dict = {}
    except Exception as e:
        st.error(f"Error reading file: {e}")

# --------- Main Actions ---------
if df_dict:
    sheet_name = list(df_dict.keys())[0]
    df = df_dict[sheet_name]

    st.markdown("<h3 style='color:#0B5345;'>Original Data</h3>", unsafe_allow_html=True)
    st.dataframe(df)

    # ---------- Rename Columns ----------
    if st.button("Rename Columns"):
        st.markdown("<h3 style='color:#C27C0E;'>Rename Columns</h3>", unsafe_allow_html=True)
        new_columns = df.columns.tolist()
        cols_to_rename = st.multiselect("Select columns to rename", df.columns.tolist())
        for col in cols_to_rename:
            new_name = st.text_input(f"Rename '{col}' to:", value=col, key=f"rename_{col}")
            idx = new_columns.index(col)
            new_columns[idx] = new_name

        if st.button("Apply Rename"):
            df.columns = new_columns
            st.success("Columns renamed successfully")
            st.dataframe(df)
            df_dict[sheet_name] = df

    # ---------- Clean Data ----------
    if st.button("Clean Data"):
        cleaned_df = df.copy()
        cleaned_df = cleaned_df.drop_duplicates()
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
                cleaned_df[col] = cleaned_df[col].str.lower()
                cleaned_df[col] = cleaned_df[col].replace("nan","")
            else:
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')

        # Drop rows if 'Name' or 'Email' exist
        drop_cols = [c for c in ['Name','Email'] if c in cleaned_df.columns]
        if drop_cols:
            cleaned_df.dropna(subset=drop_cols, inplace=True)

        st.markdown("<h3 style='color:#922B21;'>Cleaned Data</h3>", unsafe_allow_html=True)
        st.dataframe(cleaned_df)
        st.success("Data cleaned successfully")
        cleaned_df_dict[sheet_name] = cleaned_df

        # ---------- Show Description ----------
        st.markdown("<h3 style='color:#5D6D7E;'>Data Description & Info</h3>", unsafe_allow_html=True)
        st.write("### Description")
        st.write(cleaned_df.describe(include='all'))
        st.write("### Info")
        st.write(cleaned_df.info())

    # ---------- Download Button ----------
    if cleaned_df_dict:
        st.markdown("---")
        st.markdown("<h3 style='color:#0B5345;'>Download Cleaned File</h3>", unsafe_allow_html=True)
        file_name = os.path.basename(uploaded_file)
        output_name = f"cleaned_{file_name}"

        if file_ext == 'csv':
            cleaned_df_dict[sheet_name].to_csv(output_name, index=False)
        elif file_ext == 'xlsx':
            with pd.ExcelWriter(output_name, engine='openpyxl') as writer:
                for sheet, df_clean in cleaned_df_dict.items():
                    df_clean.to_excel(writer, index=False, sheet_name=sheet)
        else:
            cleaned_df_dict[sheet_name].to_json(output_name, orient="records", indent=4, force_ascii=False)

        with open(output_name, "rb") as f:
            st.download_button(
                label="Download Cleaned File",
                data=f,
                file_name=output_name
            )
        st.success(f"File ready for download: {output_name}")

# --------- Footer with Author ---------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Developed by Muhammad Mursaleen Mustafvi</p>",
    unsafe_allow_html=True
)
