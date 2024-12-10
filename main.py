from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader
from mistral import generate_coverLetter
from fpdf import FPDF
from datetime import datetime

# load the environment variables
load_dotenv()

def save_text_as_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()

    # Set font and margins
    pdf.set_font("Arial", "", 11)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_top_margin(15)

    # Add title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Cover Letter", ln=True, align="C")
    # Add date
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"{datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
    pdf.ln(5)  # Add spacing after title
    pdf.cell(0, 0, "", ln=True, border="T")  # Add a horizontal line
    pdf.ln(5)  # Add spacing after title
    
    # Reset font for body
    pdf.set_font("Arial", "", 11)

    # Split text into paragraphs and add to PDF
    paragraphs = text.strip().split("\n\n")
    for paragraph in paragraphs:
        pdf.multi_cell(0, 7, paragraph)
        pdf.ln(4)  # Add spacing between paragraphs

    # Save the PDF
    pdf.output(output_path)

# Title of the app
st.title("Cover Letter Generator")

# Upload a file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Read the uploaded file as binary
    pdf_data = uploaded_file.getvalue()

    # Process the PDF file and extract text
    def extract_text_from_pdf(pdf_data):
        reader = PdfReader(BytesIO(pdf_data))  # Convert binary data to a file-like object
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    try:
        extracted_text = extract_text_from_pdf(pdf_data)
        st.subheader("Extracted Text:")
        st.text_area("PDF Text Content", extracted_text, height=100)
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")

# User text input of the job description
st.subheader("Job Description")
job_description = st.text_area("Copy and paste the job description", height=200)

# Button to generate cover letter
if st.button("Generate Cover Letter"):
    if uploaded_file is None:
        st.warning("Please upload a PDF file first.")

    if not(len(job_description)):
        st.warning("Please enter the job description.")
        
    else:
        
        with st.spinner('Generating cover letter...'):
            cover_letter_txt = generate_coverLetter(extracted_text, job_description)
        st.success("Done!")
        
        file_path = "output.pdf"
        
        # Generate the PDF
        save_text_as_pdf(cover_letter_txt, file_path)
        
        st.subheader("Cover Letter")
        st.text_area("Generated Cover Letter", cover_letter_txt, height=200)
        
        # Path to the PDF file
        
        try:
            # Open the file in binary mode
            with open(file_path, "rb") as file:
                pdf_data = file.read()

            # Provide a download button
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="cover_letter.pdf",
                mime="application/pdf"
            )

        except FileNotFoundError:
            st.error(f"The file '{file_path}' was not found. Please ensure it exists in the specified path.")