import os
import json
import logging
import re
from datetime import datetime
import uuid
from typing import List, Tuple, Union

from flask import Flask, request, jsonify, render_template

import requests

# Optional rate limiting (uncomment if needed)
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Use environment variables for sensitive or deployment-specific settings
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama2")
HISTORY_FILE: str = os.getenv("HISTORY_FILE", "history.json")
MAX_HISTORY_ITEMS: int = int(os.getenv("MAX_HISTORY_ITEMS", "100")) # Max items to keep in history

# New default for top_k
DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "40")) # Common default for top_k

# Optional rate limiter setup (uncomment if flask-limiter is installed)
# limiter = Limiter(
#     app,
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"] # Example global limits
# )
# # Apply specific rate limit to the generate endpoint
# @limiter.limit("10/minute")


generation_history: List[dict] = []

# --- History Management Functions ---
def load_history() -> None:
    """
    Loads generation history from a JSON file.
    Initializes generation_history as an empty list if the file is not found
    or if there's an error decoding the JSON.
    """
    global generation_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                generation_history = json.load(f)
            app.logger.info(f"Loaded {len(generation_history)} history items from {HISTORY_FILE}")
            # Ensure history doesn't exceed max items even on load (e.g., if manually edited)
            generation_history = generation_history[:MAX_HISTORY_ITEMS]
        except json.JSONDecodeError as e:
            app.logger.error(f"Error decoding history JSON from {HISTORY_FILE}: {e}. Starting with empty history.")
            generation_history = []
        except Exception as e:
            app.logger.error(f"Error loading history from {HISTORY_FILE}: {e}. Starting with empty history.")
            generation_history = []
    else:
        app.logger.info(f"History file {HISTORY_FILE} not found. Starting with empty history.")
        generation_history = []

def save_history() -> None:
    """
    Saves the current generation history to a JSON file.
    Handles potential file writing errors.
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(generation_history, f, indent=4)
        app.logger.info(f"Saved {len(generation_history)} history items to {HISTORY_FILE}")
    except Exception as e:
        app.logger.error(f"Error saving history to {HISTORY_FILE}: {e}")

# Load history when the application starts
load_history()

# --- Text Processing Functions ---
def ensure_complete_sentences(text: str) -> str:
    """
    Ensures the given text ends with complete sentences, adding proper punctuation
    if necessary. Attempts to make intelligent guesses for punctuation.
    """
    if not text.strip():
        return text
    
    sentence_endings = ['.', '!', '?']
    text = text.strip()
    
    sentences = re.findall(r'[^.!?]+[.!?]*', text) # Finds sequences not containing .!? followed by optional .!?
    sentences = [s.strip() for s in sentences if s.strip()] # Clean and remove empty strings

    if not sentences:
        return text
    
    final_sentences = []
    for i, sentence in enumerate(sentences):
        if sentence and sentence[-1] in sentence_endings:
            final_sentences.append(sentence)
        else:
            if any(word in sentence.lower() for word in ['how', 'what', 'where', 'when', 'why', 'who']) and '?' not in sentence:
                final_sentences.append(sentence + '?')
            else:
                final_sentences.append(sentence + '.')

    result = ""
    for i, sentence in enumerate(final_sentences):
        if i == 0:
            result += sentence
        else:
            if result and result[-1] in sentence_endings:
                result += " " + sentence
            else:
                result += ". " + sentence

    if result and result[-1] not in sentence_endings:
        result += '.'
        
    return result

def analyze_sentences(text: str) -> Tuple[int, List[str]]:
    """
    Analyzes the sentence structure of the generated text, returning the count
    of sentences and a summary of the analysis.
    """
    sentence_endings = ['.', '!', '?']
    sentences = re.findall(r'[^.!?]*[.!?]', text)
    sentence_count = len(sentences)

    analysis_summary = [f"Total complete sentences: {sentence_count}"]

    if sentences:
        avg_length = sum(len(s.strip()) for s in sentences) / len(sentences)
        analysis_summary.append(f"Average sentence length: {avg_length:.1f} characters")
        
        periods = text.count('.')
        questions = text.count('?')
        exclamations = text.count('!')
        
        analysis_summary.append(f"Statements: {periods}, Questions: {questions}, Exclamations: {exclamations}")
    
    return sentence_count, analysis_summary

def call_ollama(
    prompt: str,
    model: str = MODEL_NAME,
    temperature: float = 0.7,
    max_tokens: int = 100,
    top_p: float = 0.9,
    top_k: int = DEFAULT_TOP_K # Added top_k parameter
) -> str:
    """
    Calls the Ollama API to generate text based on the given prompt and parameters.
    Includes an enhanced prompt to encourage complete sentences and handles API errors.
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/generate"
        
        enhanced_prompt = f"{prompt}\n\nPlease continue this text with complete sentences that end with proper punctuation (. ! or ?):"
        
        payload = {
            "model": model,
            "prompt": enhanced_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
                "top_k": top_k, # Included top_k in options
                "stop": ["</s>", "[/INST]"]
            },
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120) 
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "").strip()
        
        return ensure_complete_sentences(generated_text)
        
    except requests.exceptions.ConnectionError:
        app.logger.error(f"Failed to connect to Ollama server at {OLLAMA_BASE_URL}. Is Ollama running?")
        raise Exception("Failed to connect to the LLM. Please ensure Ollama is running.")
    except requests.exceptions.Timeout:
        app.logger.error(f"Ollama API request timed out after 120 seconds for model {model}.")
        raise Exception("LLM generation timed out. Please try again or reduce 'Max Tokens'.")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Ollama API error: {e}. Response: {e.response.text if e.response else 'N/A'}")
        raise Exception(f"An error occurred with the LLM API: {e}")
    except json.JSONDecodeError as e:
        app.logger.error(f"Error decoding JSON response from Ollama: {e}. Raw response: {response.text if response else 'N/A'}")
        raise Exception(f"Invalid response from LLM. Please check Ollama server.")
    except Exception as e:
        app.logger.error(f"Unexpected error during Ollama call: {e}")
        raise Exception(f"An unexpected error occurred during text generation: {e}")


# --- Flask Routes ---
@app.route('/')
def index() -> str:
    """Renders the main index page for text generation."""
    return render_template('index.html')

@app.route('/history')
def history() -> str:
    """Renders the history page to view past generations."""
    return render_template('history.html')

@app.route('/generate', methods=['POST'])
# @limiter.limit("10/minute")
def generate() -> Tuple[jsonify, int]:
    """
    Handles text generation requests from the frontend.
    Validates input, calls Ollama, processes response, and saves to history.
    """
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()
        model = data.get('model', MODEL_NAME)
        
        # --- Input Validation and Type Conversion ---
        try:
            temperature = float(data.get('temperature', 0.7))
            max_tokens = int(data.get('max_tokens', 150))
            top_p = float(data.get('top_p', 0.9))
            top_k = int(data.get('top_k', DEFAULT_TOP_K)) # Get top_k from request, with default
        except (ValueError, TypeError) as e:
            app.logger.error(f"Invalid input type for generation parameters: {e}")
            return jsonify({'error': 'Invalid format for temperature, max_tokens, top_p, or top_k. Please provide numbers.'}), 400

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        if not (1 <= max_tokens <= 1000):
            return jsonify({'error': 'max_tokens must be between 1 and 1000.'}), 400
        if not (0.0 <= temperature <= 2.0):
            return jsonify({'error': 'temperature must be between 0.0 and 2.0.'}), 400
        if not (0.0 <= top_p <= 1.0):
            return jsonify({'error': 'top_p must be between 0.0 and 1.0.'}), 400
        # Validation for top_k: should be non-negative integer. Ollama typically expects >=0.
        if not (0 <= top_k):
            return jsonify({'error': 'top_k must be a non-negative integer.'}), 400


        start_time = datetime.now()
        response_text = call_ollama(prompt, model, temperature, max_tokens, top_p, top_k) # Pass top_k
        end_time = datetime.now()
        response_time = int((end_time - start_time).total_seconds() * 1000)

        sentence_count, sentence_analysis = analyze_sentences(response_text)
        tokens_generated = len(response_text.split())
        tokens_per_second = round(tokens_generated / (response_time / 1000), 2) if response_time > 0 else 0

        history_item = {
            'id': str(uuid.uuid4()),
            'timestamp': start_time.isoformat(),
            'prompt': prompt,
            'response': response_text,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': top_p,
            'top_k': top_k, # Store top_k in history
            'response_time': response_time,
            'tokens_generated': tokens_generated,
            'tokens_per_second': tokens_per_second,
            'sentence_count': sentence_count
        }

        generation_history.insert(0, history_item)
        if len(generation_history) > MAX_HISTORY_ITEMS:
            generation_history.pop()

        save_history()

        return jsonify({
            'response': response_text,
            'model': model,
            'prompt': prompt,
            'sentence_count': sentence_count,
            'sentence_analysis': sentence_analysis,
            'response_time': response_time,
            'tokens_generated': tokens_generated,
            'tokens_per_second': tokens_per_second
        })
        
    except Exception as e:
        app.logger.exception(f"Unhandled error during text generation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history() -> jsonify:
    """Returns the full generation history as a JSON array."""
    return jsonify(generation_history)

@app.route('/api/history', methods=['DELETE'])
def clear_all_history() -> Tuple[jsonify, int]:
    """Clears all items from the generation history."""
    global generation_history
    generation_history = []
    save_history()
    app.logger.info("All history cleared.")
    return jsonify({'message': 'All history cleared'}), 200

@app.route('/api/history/<string:item_id>', methods=['DELETE'])
def delete_history_item(item_id: str) -> Tuple[jsonify, int]:
    """
    Deletes a specific history item by its ID.
    Returns 200 on success, 404 if item not found.
    """
    global generation_history
    initial_len = len(generation_history)
    generation_history = [item for item in generation_history if item['id'] != item_id]
    if len(generation_history) < initial_len:
        save_history()
        app.logger.info(f"History item with ID {item_id} deleted.")
        return jsonify({'message': f'Item {item_id} deleted'}), 200
    else:
        app.logger.warning(f"Attempted to delete non-existent history item with ID {item_id}.")
        return jsonify({'error': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))