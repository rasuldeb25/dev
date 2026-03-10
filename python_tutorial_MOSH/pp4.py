#Project 4: Digit -> Word program

phone = input("Phone: ")
digits_mappinig = {
    "1": "One",
    "2": "Two",
    "3": "Three",
    "4": "Four",
    "5": "Five",
    "6": "Six",
    "7": "Seven",
    "8": "Eight",
    "9": "Nine",
    "0": "Zero"
}

output = ""
for char in phone:
    output += digits_mappinig.get(char, "!") + " "
print(output)  