import os
import json
import random

def split_jsonl_data(input_file_path, output_dir, train_ratio=0.9):
    """
    Splits a JSONL file into training and test sets.

    Args:
        input_file_path (str): Path to the original JSONL file (e.g., 'data/prompt.jsonl').
        output_dir (str): Directory where the split files will be saved.
        train_ratio (float): Proportion of data for the training set.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read all lines (JSON objects) from the jsonl file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line.strip()) for line in f if line.strip()]

    random.shuffle(data)

    total = len(data)
    train_end = int(total * train_ratio)

    train_data = data[:train_end]
    test_data = data[train_end:]

    def save_jsonl(filename, content):
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            for item in content:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"{filename} saved with {len(content)} records")

    save_jsonl('train.jsonl', train_data)
    save_jsonl('test.jsonl', test_data)

if __name__ == "__main__":
    input_file_path = 'data/prompt.jsonl'  # Update with your actual path
    output_directory = 'data/'             # Output folder

    print(f"Splitting JSONL data from: {input_file_path}")
    split_jsonl_data(input_file_path, output_directory)
    print("Data splitting complete.")
