import os

from openai import OpenAI

from dotenv import load_dotenv


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def send_to_llm(email_text):

    try:

        prompt = f"""

        Extract maritime shipment information
        from this email.

        Return:
        - cargo
        - load port
        - discharge port
        - dwt
        - laycan

        Email:
        {email_text}

        """

        response = client.chat.completions.create(

            model="gpt-3.5-turbo",

            messages=[

                {
                    "role": "system",
                    "content": "You are a maritime extraction AI."
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        result = response.choices[0].message.content

        return {

            "llm_response": result
        }

    except Exception as e:

        return {

            "llm_response": "LLM fallback unavailable",

            "error": str(e)
        }
    

    