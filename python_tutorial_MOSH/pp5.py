#Project 5: Emoji Converter

message = input(">")
words = message.split(" ")
emojies = {
    ":)": "😊",
    ":(": "🙁",
    ":|": "😐",
    ":D": "😃",
    ":P": "😛",
    ":O": "😮",
    ";)": "😉",
    ":/": "😕"
}

output = ""
for word in words:
    output += emojies.get(word, word) + " "
print(output)