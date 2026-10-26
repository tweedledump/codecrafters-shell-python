import sys

def prompt_user():
    sys.stdout.write("$ ")
    return input()

def handle_invalid_command(command):
    print(f"{command}: command not found")

def evaluate_command(stream):
    command, *args = stream.split()
    if command == "exit":
        sys.exit(0)
    elif command == "echo":
        print(" ".join(args))
    else:
        handle_invalid_command(command)

def run_repl():
    command = prompt_user()
    evaluate_command(command)

def main():
    while True:
        run_repl()
        


if __name__ == "__main__":
    main()
