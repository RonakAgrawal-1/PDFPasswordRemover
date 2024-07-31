import streamlit as st
import PyPDF2
import os
import zipfile
from io import BytesIO

def remove_pdf_password(input_pdf_file, password):
    try:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        if pdf_reader.is_encrypted:
            if pdf_reader.decrypt(password):
                pdf_writer = PyPDF2.PdfWriter()
                for page_num in range(len(pdf_reader.pages)):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output_pdf_file = os.path.splitext(input_pdf_file.name)[0] + "_decrypted.pdf"
                output_pdf_bytes = BytesIO()
                pdf_writer.write(output_pdf_bytes)
                output_pdf_bytes.seek(0)
                return output_pdf_file, output_pdf_bytes
            else:
                st.error(f"Incorrect password for file: {input_pdf_file.name}")
                return None, None
        else:
            st.warning(f"The file {input_pdf_file.name} is not encrypted.")
            return None, None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

# Streamlit UI
st.set_page_config(page_title="PDF Password Remover", layout="wide")

# Main title and description
st.title("🔐 PDF Password Remover")
st.write("**Easily decrypt your password-protected PDF files. Upload up to 12 files at once and download them in one go!**")

# Instructions tab
with st.expander("📝 Instructions"):
    st.markdown("""
    **How to use:**
    1. **Upload PDF files**: Click 'Browse files' to select up to 12 PDF files.
    2. **Enter the password**: Type in the password used to protect the PDF files.
    3. **Remove Password and Download**: Click the button to decrypt your files. If the password is correct, you'll be able to download all decrypted files as a single ZIP file.
    
    **Please note:**
    - The password must be the same for all uploaded files.
    - You can upload a maximum of 12 PDF files for proper usage.
    - If the password is incorrect for any file, you will be notified, and that file will not be decrypted.
    """)

# Layout for file uploader and password input
col1, col2 = st.columns(2)

with col1:
    uploaded_files = st.file_uploader("📁 Choose PDF files", type="pdf", accept_multiple_files=True)

with col2:
    password = st.text_input("🔑 Enter the password for the PDFs", type="password")

# Layout for processing and download button
st.markdown("---")

if st.button("Remove Password and Download"):
    if uploaded_files and password:
        if len(uploaded_files) > 12:
            st.warning("You have uploaded more than 12 files. Please reduce the number of files and try again.")
        else:
            decrypted_files = []
            for uploaded_file in uploaded_files:
                st.write(f"Processing {uploaded_file.name}...")
                output_pdf_file, output_pdf_bytes = remove_pdf_password(uploaded_file, password)
                if output_pdf_file:
                    decrypted_files.append((output_pdf_file, output_pdf_bytes))
            
            if decrypted_files:
                # Create a ZIP file to download all PDFs at once
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for output_pdf_file, output_pdf_bytes in decrypted_files:
                        zip_file.writestr(output_pdf_file, output_pdf_bytes.read())
                zip_buffer.seek(0)

                st.success(f"Successfully decrypted {len(decrypted_files)} files.")
                st.download_button(
                    label="📥 Download All Files",
                    data=zip_buffer,
                    file_name="decrypted_pdfs.zip",
                    mime="application/zip"
                )
            else:
                st.warning("No files were decrypted. Please check if the password is correct for all files.")
    else:
        st.warning("Please upload files and enter a password.")

# Custom styling for improved UI
st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #E63939;
        }
        .stFileUploader>label {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stTextInput>div>label {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stExpanderHeader {
            font-size: 18px !important;
            font-weight: bold !important;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
