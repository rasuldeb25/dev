#Project 3: Car Game

command = ""
started = False

while True:
    command = input("> ").lower()
    if command == "start":
        if started:
            print("The Engine is already running!")
        else:
            started = True
            print("Starting the Engine ...")
    elif command == "stop":
        if not started:
            print("The Engine is already turned off!")
        else:
            started = False
            print("Turning off the Engine ...")
    elif command == "help":
        print("""
        start - to start the engine
        stop - to stop the engine
        quit - to quit
        """)
    elif command == "quit":
        break
    else:
        print("Invalid input.")