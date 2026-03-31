import os
import subprocess

def convert_all_ipynb_to_pdf():
    for file in os.listdir('.'):
        if file.endswith('.ipynb'):
            print(f"Converting: {file}")
            try:
                subprocess.run(
                    ["jupyter", "nbconvert", "--to", "pdf", file],
                    check=True
                )
                print(f"✔ Done: {file}")
            except Exception as e:
                print(f"✘ Failed: {file}")
                print(e)

if __name__ == "__main__":
    convert_all_ipynb_to_pdf()