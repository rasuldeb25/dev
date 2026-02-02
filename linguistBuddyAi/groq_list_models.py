import os
from groq import Groq, APIStatusError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Client
# Make sure GROQ_API_KEY is in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def check_real_access():
    print(f"{'Model Name':<40} | {'Status'}")
    print("-" * 65)
    
    try:
        # 1. Fetch the list of available models
        models = client.models.list()
        
        for m in models.data:
            model_id = m.id
            
            # Special handling for Whisper (Audio model)
            # We can't test it with text "Hi", so we assume success if listed
            if "whisper" in model_id:
                print(f"{model_id:<40} | ✅SUCCESS (Audio Only)")
                continue

            # 2. Test Text Models
            try:
                client.chat.completions.create(
                    messages=[{"role": "user", "content": "Hi"}],
                    model=model_id,
                    max_tokens=1
                )
                print(f"{model_id:<40} | ✅SUCCESS")
                
            except APIStatusError as e:
                if e.status_code == 429:
                    print(f"{model_id:<40} | ❌RATE LIMIT (Busy)")
                elif e.status_code == 404:
                    print(f"{model_id:<40} | ⚠️DEPRECATED / NOT FOUND")
                else:
                    print(f"{model_id:<40} | ⚠️ERROR: {e.message}")
            except Exception as e:
                print(f"{model_id:<40} | ⚠️FAILED: {type(e).__name__}")

    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to Groq. Check API Key. {e}")

if __name__ == "__main__":
    check_real_access()