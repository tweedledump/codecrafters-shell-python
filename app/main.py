import sys

def prompt_user():
    sys.stdout.write("$ ")
    return input()

def handle_invalid_command(command):
    print(f"{command}: command not found")

def exit_command(_args)):
    sys.exit(0)

def echo_command(args):
    print(" ".join(args))

def type_command(args):
    if args[0] in builtin_commands:
        print(f"{args[0]} is a shell builtin")
    else:
        print(f"{args[0]}: not found")

builtin_commands = {
    "exit": exit_command,
    "echo": echo_command,
    "type": type_command,
}

def evaluate_command(command):
    command, *args = command.split()
    if command in builtin_commands:
        builtin_commands[command](args)
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
