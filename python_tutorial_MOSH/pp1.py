#Project 1: Weight Converter
#kilos to pounds
weight = input("Enter your weight: ")
unit = input('(L)bs or (K)g: ')
if unit.upper() == "L":
    converted = float(weight) * 0.45
    print(f"You are {converted} kilos")
else:
    converted = float(weight) / 0.45
    print(f"You are {converted} pounds")