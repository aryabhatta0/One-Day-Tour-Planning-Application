import openai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config import OPENAI_API_KEY


class LLMManager:
    def __init__(self, mode="openai", api_key=OPENAI_API_KEY, model_name=None, device="cpu"):
        self.mode = mode
        self.device = device

        if self.mode == "openai":
            openai.api_key = api_key
        elif self.mode == "transformers":
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)

    def query(self, prompt, max_length=200):
        if self.mode == "openai":
            return self._query_openai(prompt)
        elif self.mode == "transformers":
            return self._query_transformers(prompt, max_length)
        else:
            raise ValueError("Invalid mode. Choose either 'openai' or 'transformers'.")

    def _query_openai(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "You are a travel assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]

    def _query_transformers(self, prompt, max_length):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(inputs, max_length=max_length, num_return_sequences=1, do_sample=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


# Example Usage
if __name__ == "__main__":
    # Using OpenAI API
    print("Using OpenAI API:")
    openai_llm = LLMManager()
    response = openai_llm.query("Plan a one-day trip in Rome with a $100 budget.")
    print(response)

    # Using Hugging Face Transformers
    print("\nUsing Hugging Face Transformers:")
    hf_llm = LLMManager(mode="transformers", model_name="gpt2", device="cuda" if torch.cuda.is_available() else "cpu")
    response = hf_llm.query("Plan a one-day trip in Rome with a $100 budget.")
    print(response)
