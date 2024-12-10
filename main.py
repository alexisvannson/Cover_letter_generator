from dotenv import load_dotenv
import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader
import os
import requests
from fpdf import FPDF

# load the environment variables
load_dotenv()

def generate_cover_letter(cv, fiche_poste, api_key=None, model="mistral-medium", temperature=0.3):
    # Retrieve the API key from the environment if not provided
    api_key = os.getenv("MISTRAL_API_KEY") if api_key is None else api_key
    
    if not api_key:
        raise ValueError("API key not found. Please set the MISTRAL_API_KEY environment variable or pass it as an argument.")

    # Mistral API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Create the prompt
    prompt = f"""
    Generate a professional cover letter for the following job description:

    {fiche_poste}

    Use the following CV details to tailor the cover letter:

    {cv}

    The cover letter should be professional and directly highlight the relevant skills and experiences.
    """

    # Data payload for the API request
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    # Send the request
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=data
    )

    # Return the generated text or handle errors
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"
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
    pdf.cell(0, 10, "Application for ML Engineer Internship at Klark", ln=True, align="C")
    pdf.ln(5)

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
            cover_letter_txt = generate_cover_letter(extracted_text, job_description)
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
                file_name="output.pdf",
                mime="application/pdf"
            )

        except FileNotFoundError:
            st.error(f"The file '{file_path}' was not found. Please ensure it exists in the specified path.")