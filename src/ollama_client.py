import requests
import json

DEFAULT_MODEL = "mistral"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def check_connection():
    """Checks if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def generate_response(prompt, model=DEFAULT_MODEL, stream=False):
    """Generates a response from the Ollama model."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        if stream:
            # Handle streaming if needed, for now assuming non-streaming for simplicity in core logic
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded = json.loads(line.decode('utf-8'))
                    full_response += decoded.get('response', '')
                    if decoded.get('done'):
                        break
            return full_response
        else:
            return response.json().get('response', '')
            
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {str(e)}"

def generate_json(prompt, model=DEFAULT_MODEL):
    """
    Generates a structured JSON response.
    Appends instructions to force JSON output.
    """
    json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON. Do not include markdown formatting or explanations."
    response_text = generate_response(json_prompt, model=model)
    
    # Simple cleanup to find JSON blob if model chatters
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            return json.loads(json_str)
        else:
            return {"error": "No JSON found in response", "raw_response": response_text}
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_response": response_text}
