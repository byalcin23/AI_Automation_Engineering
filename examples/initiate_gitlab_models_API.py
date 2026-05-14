from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory's .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings. 
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

def main():
    # OpenAI kütüphanesi otomatik olarak OPENAI_API_KEY'i okur
    client = OpenAI(
        base_url="https://models.github.ai/inference"
    )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": "Say some jokes about programming."}
        ],
        model="openai/gpt-4o-mini",
        temperature=1,
        max_tokens=4096,
        top_p=1
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"The sample encountered an error: {err}")