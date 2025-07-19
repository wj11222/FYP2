import json
import subprocess
from rouge_score import rouge_scorer
from pathlib import Path

# Models to evaluate
models = ['llama2', 'llama2:latest', 'mistral', 'gemma']

# Load test data
test_data_path = Path("data/test.jsonl")
with open(test_data_path, "r", encoding="utf-8") as f:
    test_data = [json.loads(line) for line in f]

# Initialize ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

# Ollama generator
def generate_with_ollama(model_name, prompt):
    try:
        result = subprocess.run(
            ['ollama', 'run', model_name, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[Timeout]"

# Evaluation loop
print("\n=== ROUGE Score Summary ===")
for model in models:
    total_r1 = total_r2 = total_rl = 0
    count = 0

    for sample in test_data:
        prompt = sample.get("prompt", "")
        expected = sample.get("completion", "").strip()

        generated = generate_with_ollama(model, prompt)
        if generated == "[Timeout]":
            continue

        scores = scorer.score(expected, generated)
        total_r1 += scores['rouge1'].fmeasure
        total_r2 += scores['rouge2'].fmeasure
        total_rl += scores['rougeL'].fmeasure
        count += 1

    if count > 0:
        avg_r1 = total_r1 / count
        avg_r2 = total_r2 / count
        avg_rl = total_rl / count
    else:
        avg_r1 = avg_r2 = avg_rl = 0

    print(f"\nModel: {model}")
    print(f"ROUGE-1 (unigrams): {avg_r1:.4f}")
    print(f"ROUGE-2 (bigrams): {avg_r2:.4f}")
    print(f"ROUGE-L (longest match): {avg_rl:.4f}")
