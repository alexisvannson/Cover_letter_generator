import os
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
model = "mistral-small-latest"

def generate_coverLetter(cv_text, job_description):
    try:
        # Define the prompt for generating the cover letter
        prompt = f"""
            Generate a professional and engaging cover letter based on the following CV and job description:
            You must only include text content starting with 'Dear Hiring Manager,' and ending with 'Sincerely, NAME'.

            CV:
            {cv_text}

            Job Description:
            {job_description}
        """

        # Initialize the Mistral client
        client = Mistral(api_key=API_KEY)

        # Prepare the messages for the chat completion
        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        # Send the request to the Mistral API
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            response_format={
                "type": "text",  # Assuming the response is plain text
            },
            max_tokens=800
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while generating the cover letter: {e}"