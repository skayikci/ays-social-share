import anthropic
import os
from flask import current_app

def generate_anthropic_completion(prompt):
    client = anthropic.Anthropic(api_key=current_app.config['ANTHROPIC_API_KEY'])
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error calling Anthropic API: {str(e)}")
        return f"Error: Unable to generate completion. {str(e)}"
