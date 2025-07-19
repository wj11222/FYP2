import json

def jsonl_to_modelfile(jsonl_path, modelfile_path):
    with open(jsonl_path, 'r', encoding='utf-8') as f_in, open(modelfile_path, 'w', encoding='utf-8') as f_out:
        f_out.write('from llama2\n\n')
        f_out.write('system "You are a helpful scriptwriting assistant."\n\n')
        
        for line in f_in:
            if not line.strip():
                continue
            data = json.loads(line)
            prompt = data.get("prompt", "")
            completion = data.get("completion", "")

            f_out.write('message user """\n')
            f_out.write(f'{prompt}\n')
            f_out.write('"""\n\n')

            f_out.write('message assistant """\n')
            f_out.write(f'{completion}\n')
            f_out.write('"""\n\n')

    print(f"Modelfile generated at: {modelfile_path}")

if __name__ == "__main__":
    jsonl_file = "data/train.jsonl"    # Adjust path if needed
    modelfile_out = "Modelfile"

    jsonl_to_modelfile(jsonl_file, modelfile_out)
