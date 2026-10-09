import string
import random

try:
    import pyperclip
    CLIPBOARD_WORKING = True
except ImportError:
    CLIPBOARD_WORKING = False

session_history = []

WORD_BANK = ["correct", "horse", "battery", "staple", "apple", "river", "stone", "planet", "guitar", "area"]

def validate_digit(digit: str):
    if not digit.isdigit():
        return None, ValueError('Input must be a whole number')
    
    return int(digit), None

def validate_password_length(user_input: str):
    passwd_length, err = validate_digit(user_input)

    if err:
        return None, err

    if passwd_length < 4:
        return None, ValueError('Minimum of password length is 4') 
    
    return passwd_length, None

def validate_options(user_input: str, options: tuple[str, ...]):
    option = user_input.lower().strip()
    error_message = f"Answer must be {', '.join(options[:-1])}, or {options[-1]}"

    if option not in options:
        return None, ValueError(error_message)

    return option, None

def get_valid_input(prompt: str, validation_fn, options=None):
    while True:
        user_input = input(prompt)

        if options is not None:
            value, err = validation_fn(user_input, options)
        else:
            value, err = validation_fn(user_input)

        if err is None:
            return value

        print(f"Error! {err}\n")

def validate_criteria() -> list[str]:
    criteria = [
        "Include uppercase letters? (y/n): ",
        "Include lowercase letters? (y/n): ",
        "Include digits? (y/n): ",
        "Include special characters? (y/n): "
    ]

    options = []

    for prompt in criteria:
        option = get_valid_input(prompt, validate_options, ('y', 'n'))
        options.append(option)

    return options

def build_charsets(criteria: list[str]) -> tuple[str, list[str]]:
    char_bucket, first_charset = "", []
    charsets = [string.ascii_uppercase, string.ascii_lowercase, string.digits, string.punctuation]

    for criterion, charset in zip(criteria, charsets):
        if criterion == 'y':
            char_bucket += charset
            first_charset.append(random.choice(charset))

    return char_bucket, first_charset

def copy_to_clipboard(output: str):
    if CLIPBOARD_WORKING:
        pyperclip.copy(output)
        print("Password automatically copied to clipboard!")
    else:
        print("Cannot copy to clipboard.")

def display_and_copy(results: list[str]):
    output = "\n".join(results)
    print(f"Generated Password(s):\n\n{output}\n")
    copy_to_clipboard(output)

def rate_password(weak_condition, medium_condition) -> str:
    if weak_condition:
        return "\nPassword Strength: Weak\n"
    elif medium_condition:
        return "\nPassword Strength: Medium\n"
    else:
        return "\nPassword Strength: Strong\n"

def save_pass_to_file(password: str) -> None:
    with open("password.txt", "w") as file:
        file.write(password)

def generate_and_rate_passwords(passwd_length, passwd_count, criteria):
    passwd_history = []

    # Generate password the requested number of times
    while len(passwd_history) < passwd_count: 
        char_bucket, first_charset = build_charsets(criteria)
        remaining_length = passwd_length - len(first_charset)
        
        if remaining_length != 0:
            first_charset.extend(random.choices(char_bucket, k=remaining_length))
        
        random.shuffle(first_charset)
        
        password = "".join(first_charset)
        # The uniqueness gate_keeper
        if password not in session_history:
            passwd_history.append(password)
            session_history.append(password)

    # Rating the password strength
    passwd_features = len([option for option in criteria if option == 'y'])
    password_strength = rate_password(
        passwd_length >= 4 and passwd_features <= 2,
        passwd_length >= 4 and passwd_features == 3
    )

    print(password_strength)
    display_and_copy(passwd_history)

def generate_and_rate_passphrases(word_count, passphrase_count):
    passphrase_history = []
    while len(passphrase_history) < passphrase_count:
        passphrase = random.choices(WORD_BANK, k=word_count)
        random.shuffle(passphrase)
        passphrases = "-".join(passphrase)
        if passphrases not in session_history:
            passphrase_history.append(passphrases)
            session_history.append(passphrases)

    password_strength = rate_password(
        word_count == 4,
        word_count <= 6
    )
    print(password_strength)
    display_and_copy(passphrase_history)

def history_manager():
    while True:
        if not session_history:
            print("History is currently empty!")
            break
        
        history_options = ('save', 'view', 'select', 'delete', 'exit')
        
        action = get_valid_input(
        f"Choose history action ({"/".join(history_options)}): ", 
        validate_options, history_options)

        if action == 'view':
            print("\n".join([f"{index + 1}. {password}" for index, password in enumerate(session_history)]))

        elif action == 'select':
            choice = get_valid_input("Enter the number of the password to copy: ", validate_digit)

            #check if number is in the history
            if 1 <= choice <= len(session_history):
                target_password = session_history[choice -1] # Converts human counting to Python index math
                copy_to_clipboard(target_password)
                print("Password automatically copied to clipboard!")
            else:
                print("Error! That number does not exist in history.\n")

        elif action == 'delete':
            choice = get_valid_input("Enter the number of the password to delete: ", validate_digit)
        
            if 1 <= choice <= len(session_history):
                # Remove the item cleanly from your list using its index
                session_history.pop(choice - 1)
                save_pass_to_file("\n".join(session_history))
                print(f"Success! Permanently deleted item {choice} from history.\n")
            else:
                print("Error! That number does not exist in history.\n")
        elif action == "save":
            answer = get_valid_input("Warning: Saving to a file is risky\nAre you sure? (y/n): ", validate_options, ('y', 'n'))

            if answer == 'y':
                save_pass_to_file("\n".join(session_history))
                print("Success! Go to password.txt to see your password(s)\n")

        elif action == 'exit':
            print("Exiting history manager.\n")
            break

while True:
    mode = get_valid_input("Choose mode: character, passphrase or exit (c/p/x): ", validate_options, ('c', 'p', 'x'))

    if mode == 'p':
        word_count = get_valid_input('How many word count? ', validate_password_length)

        passphrase_count = get_valid_input('How many passphrases do you need?: ', validate_digit)

        generate_and_rate_passphrases(word_count, passphrase_count)

    elif mode == 'c': 
        passwd_length = get_valid_input('Enter password length: ', validate_password_length)

        criteria = validate_criteria()

        if all(option == 'n' for option in criteria):
            print('Error! Please select atleast one feature.\n')
            continue

        passwd_count = get_valid_input('How many passwords do you need?: ', validate_digit)

        generate_and_rate_passwords(passwd_length, passwd_count, criteria)

    elif mode == 'x':
        print("Thank you for using our product!\n")
        break

    #Save to File
    manage_history = get_valid_input("\nWould you like to manage password history? (y/n): ", validate_options, ('y', 'n'))
    if manage_history == 'y':
        history_manager()
    
    print("-" * 30 + "\n")
        