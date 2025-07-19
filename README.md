# 🎬 Scriptwriting Predictive Text System

An AI-powered web application designed to assist screenwriters by generating contextual script continuations. This system leverages a local Large Language Model (LLM) served by **Ollama** to provide creative and relevant text based on user prompts. It offers customizable generation parameters and maintains a persistent history of all generated texts.

---

## ✨ Features

- **Contextual Text Generation:** Generate new script lines, character dialogues, or scene descriptions based on your input.
- **Local LLM Integration (Ollama):** Utilizes a locally run LLM via Ollama, ensuring privacy and potentially faster response times without relying on external APIs. The `scriptbot` model is designed to be used with a custom `Modelfile`.
- **Customizable Parameters:** Fine-tune the AI's output with adjustable generation parameters, including:
  - **Creativity (Temperature):** Controls the randomness of predictions.
  - **Vocabulary Size (Top-K):** Limits the number of most likely next words considered.
  - **Focus (Top-P):** Selects words from the smallest set whose cumulative probability exceeds `p`.
  - **Repetition Control (Repetition Penalty):** Discourages the model from repeating itself.
  - **Length (Max New Tokens):** Sets the maximum number of new words to generate.
- **Persistent Generation History:** All generated texts, along with their prompts and parameters, are saved to `history.json` for easy review across sessions. Each history entry includes unique IDs, timestamps, and detailed metrics like response time, tokens generated, tokens per second, and sentence count.
- **Real-time Generation Metrics:** Provides insights into the generation process, including response time, tokens generated, and tokens per second.
- **Automated Sentence Completion:** Ensures generated text ends with complete sentences and proper punctuation for better readability.
- **User-Friendly Interface:** An intuitive and responsive web interface built with Flask and Jinja2.

---

## 🚀 Getting Started

Follow these instructions to set up and run the application on your local machine.

### Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- **Java Runtime Environment (JRE)** (required for BFG if you ever clean your Git history)
- **Ollama:** A local LLM server. Download and install it from [ollama.com](https://ollama.com/).

---

### Setup Instructions

1. **Project Structure:**  
   Ensure your project directory is organized as follows. The `Modelfile` is crucial for setting up your custom `scriptbot` model in Ollama.

   ```
   your-project-folder/
   ├── .venv/                      # Python virtual environment (ignored by Git)
   ├── data/                       # Contains data files (e.g., for training/evaluation)
   │   ├── jsonl_to_modelfile.py
   │   ├── prompt.jsonl
   │   ├── test.jsonl
   │   └── train.jsonl
   ├── scripts/                    # Utility scripts (e.g., data splitting)
   │   └── split_data.py
   ├── templates/                  # HTML templates for the web interface
   │   ├── history.html
   │   └── index.html
   ├── app.py                      # Main Flask application logic
   ├── history.json                # Stores persistent generation history 
   ├── Modelfile                   # Ollama custom model definition for 'scriptbot' 
   ├── requirements.txt            # Python dependencies 
   └── .gitignore                  # Git ignore rules
   ```

2. **Create a Virtual Environment:**  
   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment:**  
   - **Windows:**

     ```bash
     .venv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source .venv/bin/activate
     ```

4. **Install Python Dependencies:**  
   The `requirements.txt` file lists the necessary Python packages.

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Ollama Model:**  
   You need to create and run the `scriptbot` model in Ollama using your `Modelfile`.

   - Ensure the `Modelfile` is in your project's root directory (the same level as `app.py`).
   - Run the following commands in your terminal (make sure Ollama is running):

     ```bash
     ollama create scriptbot -f Modelfile
     ollama run scriptbot
     ```

   > **Tip:** Keep the Ollama server running by executing `ollama serve` in a separate terminal while you use the Flask app.

6. **Run the Flask Application:**

   With your virtual environment active and Ollama running, start the Flask application:

   ```bash
   python app.py
   ```

   The application will typically run on `http://127.0.0.1:5000/` or `http://localhost:5000/`.

7. **Evaluate Model (Optional):**

   To evaluate the model using ROUGE scores, run:

   ```bash
   python evaluate_rouge.py
   ```

   This script will compare generated outputs to reference data and provide quantitative evaluation metrics.

---

## 🖥️ Usage

1. **Access the Application:**

   Open your web browser and go to the address displayed in your terminal (e.g., `http://127.0.0.1:5000/`).

2. **Generate Text:**

   - In the "Scene Context or Dialogue" text area, enter your starting prompt.
   - (Optional) Check "Adjust Generation Parameters" to reveal and modify advanced settings like `Creativity`, `Length`, and `Repetition Control`.
   - Click the "🚀 Generate Script Continuation" button.
   - The generated text and performance metrics will appear in the "Generated Script Continuation" section.

3. **View History:**

   Click the "📚 View Generation History" link at the bottom of the page to see a list of all your previous generations, along with the prompts, parameters, and detailed metrics used for each. You can also delete individual history items or clear all history from this page.

4. **Clear Form:**

   Click the "🔄 Clear Form" link on the main page to reset the input field and generated output.

---

## 🛠️ Technologies Used

- **Python**: Primary programming language.
- **Flask**: Lightweight Python web framework for the backend.
- **Jinja2**: Templating language for rendering HTML.
- **Requests**: For HTTP requests to interact with Ollama API.
- **Ollama**: Runs local large language models.
- **JSON**: Data storage and API communication.
  
---

## ⚠️ Important Notes

- Make sure your `.gitignore` file contains:

  ```
  .venv/
  __pycache__/
  *.pyc
  history.json
  ```

  to avoid committing large or unnecessary files.

- Keep Ollama server running (`ollama serve`) during your app usage.

- If you ever need to clean large files or `.venv` accidentally committed to Git history, consider using the [BFG Repo Cleaner](https://rtyley.github.io/bfg-repo-cleaner/).

---

## Contact

For questions or support, feel free to reach out!
