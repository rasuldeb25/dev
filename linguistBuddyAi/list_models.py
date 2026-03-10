from google import genai
from google.genai import errors

client = genai.Client(api_key="")

def check_real_access():
    print(f"{'Model Name':<40} | {'Status'}")
    print("-" * 60)
    
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            try:
                client.models.generate_content(
                    model=m.name,
                    contents="Hi",
                    config={'max_output_tokens': 1}
                )
                print(f"{m.name:<40} |✅SUCCESS")
            except errors.ClientError as e:

                if "429" in str(e):
                    print(f"{m.name:<40} |❌NO QUOTA (Free Tier restricted)")
                else:
                    print(f"{m.name:<40} |⚠️ERROR: {e}")
            except Exception as e:
                print(f"{m.name:<40} |⚠️FAILED: {type(e).__name__}")

if __name__ == "__main__":
    check_real_access()