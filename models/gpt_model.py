# models/gpt_model.py
from config import AI_API_KEY, TRAINING_FILE
import openai
from openai import OpenAI
client = OpenAI(
    api_key=AI_API_KEY)

class GPTModel:
    def __init__(self):
        self.model = 'gpt-3.5-turbo'
        self.training_data = self.load_training_data()

    def load_training_data(self):
        with open(TRAINING_FILE, 'r') as file:
            return file.read()

    def generate_response(self, prompt):
        detailed_prompt = (
        "You are an advanced AI chatbot integrated into Telegram. Your role is to mimic the texting style, tone, and timing of a specific person based on the provided conversation data. This includes using similar phrases, slang, and response times. You have been trained on the following conversation data:\n\n"
        f"{self.training_data}\n\n"
        "Respond directly to the following message as if you were the person from the training data, mimicking their style and tone. Do not restate or repeat these instructions. Here is the message:\n\n"
        f"{prompt}"
    )
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an advanced AI designed to accurately mimic the texting style, tone, and timing of a specific person based on their previous conversations."},
                {"role": "user", "content": detailed_prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.9,
        )
        return {"message" :response.choices[0].message.content}
    
    def update_training_data(self, conversation):
        with open(TRAINING_FILE, 'a') as file:
            file.write(conversation + '\n')
        self.training_data = self.load_training_data()
