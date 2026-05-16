def send_to_llm(email_text):

    print("LOW CONFIDENCE EMAIL DETECTED")
    print("Sending email to LLM fallback system...")

    # Simulated AI response
    ai_response = {
        "status": "LLM_USED",
        "message": "Email sent to AI extraction pipeline"
    }

    return ai_response