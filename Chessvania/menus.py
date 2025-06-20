# menus.py

from rich.console import Console
from rich.text import Text

def show_main_menu(dev_mode = False):
    """
    Display the main menu and handle user input.
    """
    print("\nWelcome to:")
    print(" _____ _____ _____ _____ _____ _____ _____ _____ _____ _____ ")
    print("|     |  |  |   __|   __|   __|  |  |  _  |   | |     |  _  |")
    print("|   --|     |   __|__   |__   |  |  |     | | | |-   -|     |")
    print("|_____|__|__|_____|_____|_____|\___/|__|__|_|___|_____|__|__|\n")

    while True:
        print(f"1. Start Game {'(Dev Abilities Activated)' if dev_mode else ''}")
        print("2. Instructions")
        print(f"3. Toggle Dev Mode (Currently: {'ON' if dev_mode else 'OFF'})")
        print("4. Quit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            return dev_mode  # Return the dev mode state
        elif choice == "2":
            print("\nInstructions:")
            print(" - Enter moves in standard chess notation (e.g., 'e2 e4').")
            print(" - Type 'quit' to exit the game.")
            print(" - If Dev Mode is enabled, type 'upgrade' to instantly upgrade a piece.\n")
        elif choice == "3":
            dev_mode = not dev_mode  # Toggle Dev Mode
            print("\nDev Mode is now " + ("ON" if dev_mode else "OFF") + "!")
        elif choice == "4":
            print("Goodbye!")
            return None  # Quit game
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
