import sys

def write_prompt():
    sys.stdout.write("$ ")

def get_input():
    return input()

def handle_invalid_command(command):
    print(f"{command}: command not found")

def run_repl():
    write_prompt()
    command = get_input()
    handle_invalid_command(command)

def main():
    while True:
        run_repl()
        


if __name__ == "__main__":
    main()
