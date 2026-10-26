import sys

def prompt_user():
    sys.stdout.write("$ ")
    return input()

def handle_invalid_command(command):
    print(f"{command}: command not found")

def evaluate_command(command):
    match command:
        case "exit":
            sys.exit(0)
        case _:
            handle_invalid_command(command)

def run_repl():
    command = prompt_user()
    evaluate_command(command)

def main():
    while True:
        run_repl()
        


if __name__ == "__main__":
    main()
