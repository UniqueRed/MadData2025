import os
import pandas as pd
import openai
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset
from peft import LoraConfig, get_peft_model

# ----- Configuration -----
# Set your API keys/tokens here
OPENAI_API_KEY = "your_openai_api_key"
HF_TOKEN = "your_huggingface_token"

# Model names and file paths
GPT4_MODEL = "gpt-4"  # Used during supervision (assumed already done)
MISTRAL_MODEL = "mistralai/Mistral-7B-v0.1"
LABELED_CSV = "courses_labeled.csv"  # CSV must contain columns: gpa, prof_review, grad_contrib, admin_pref, target_score

# Initialize OpenAI API key (if needed for supervision)
openai.api_key = OPENAI_API_KEY


# ----- Step 1: Prepare the Fine-Tuning Dataset -----
def prepare_dataset(csv_file):
    """
    Loads the labeled CSV and creates input prompts and targets for fine-tuning.
    Each prompt is built from course attributes, and the target is the GPT-4 generated score (as text).
    """
    df = pd.read_csv(csv_file)

    def create_prompt(row):
        return (
            f"Course attributes: "
            f"Class average GPA: {row['gpa']}, "
            f"Professor review: {row['prof_review']}, "
            f"Contribution to graduation: {row['grad_contrib']}, "
            f"Admin's preference: {row['admin_pref']}. "
            f"Score: "
        )

    df["input_text"] = df.apply(create_prompt, axis=1)
    # Ensure target_score is cast as string (e.g., "8.5")
    df["target_text"] = df["target_score"].astype(str)

    # Create a dataset with only the necessary columns.
    dataset = Dataset.from_pandas(df[["input_text", "target_text"]])
    return dataset


def tokenize_function(examples, tokenizer, max_length=512):
    """
    Tokenizes each example by concatenating input prompt and target score.
    The model is trained to generate the score given the prompt.
    """
    # Concatenate the prompt and target
    inputs = [inp + target for inp, target in zip(examples["input_text"], examples["target_text"])]
    model_inputs = tokenizer(inputs, truncation=True, padding="max_length", max_length=max_length)
    return model_inputs


# ----- Step 2: Set Up LoRA Fine-Tuning on Mistral 7B -----
def setup_model_and_tokenizer(model_name, hf_token):
    """
    Loads the pre-trained Mistral 7B model and tokenizer from Hugging Face,
    and wraps the model with a LoRA adapter.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        use_auth_token=hf_token
    )

    # Define LoRA configuration
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],  # Adjust these based on model architecture
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Wrap the model with LoRA adapters
    model = get_peft_model(model, lora_config)
    print("LoRA model prepared:")
    model.print_trainable_parameters()

    return model, tokenizer


# ----- Step 3: Fine-Tune the LoRA-Enhanced Model -----
def fine_tune_model(dataset, model, tokenizer):
    """
    Fine-tunes the LoRA-adapted Mistral 7B model on the provided dataset.
    """
    # Tokenize dataset
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=["input_text", "target_text"]
    )

    training_args = TrainingArguments(
        output_dir="./mistral_lora_finetuned",
        per_device_train_batch_size=2,
        num_train_epochs=3,
        learning_rate=5e-5,
        logging_steps=10,
        save_steps=50,
        fp16=True,
        evaluation_strategy="no",
        overwrite_output_dir=True,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    trainer.train()
    # Save both the PEFT adapter and the base model configuration
    model.save_pretrained("./mistral_lora_finetuned")
    tokenizer.save_pretrained("./mistral_lora_finetuned")
    print("Fine-tuning complete and model saved to './mistral_lora_finetuned'.")


# ----- Main Execution -----
def main():
    # Step 1: Prepare the dataset for fine-tuning.
    dataset = prepare_dataset(LABELED_CSV)
    print("Dataset prepared. Number of examples:", len(dataset))

    # Step 2: Load the model & tokenizer and wrap with LoRA adapters.
    model, tokenizer = setup_model_and_tokenizer(MISTRAL_MODEL, HF_TOKEN)

    # Step 3: Fine-tune the model.
    fine_tune_model(dataset, model, tokenizer)


if __name__ == "__main__":
    main()
