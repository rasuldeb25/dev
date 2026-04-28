import  secrets
import  string

chars = " " + string.punctuation + string.digits + string.ascii_letters
chars = list(chars)

rng = secrets.SystemRandom()
key = chars.copy()
rng.shuffle(key)

while True:
    menu_choice = input("Do you want to encrypt or decrypt? (E/D): ").upper()

    if menu_choice == "E":
        plain_text = input("Enter a message to encrypt: ")
        cipher_text = ""

        for letter in plain_text:
            index = chars.index(letter)
            cipher_text += key[index]
        print(f"The encrypted message is: {cipher_text}")
        print(f"The original message is: {plain_text}")

    elif menu_choice == "D":
        cipher_text = input("Enter a message to dencrypt: ")
        plain_text = ""

        for letter in cipher_text:
            index = key.index(letter)
            plain_text += chars[index]
        print(f"The encrypted message is: {cipher_text}")
        print(f"The original message is: {plain_text}")
    else:
        print("Invalid choice. Please try again.")

    want_to_continue = input("Do you want to continue? (Y/N): ").upper()
    if want_to_continue != "Y":
        print("Goodbye!")
        break