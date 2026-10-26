import sys
import os

path_dirs = os.environ.get("PATH", "").split(":")

def prompt_user():
    sys.stdout.write("$ ")
    return input()

def handle_invalid_command(command):
    print(f"{command}: command not found")

def exit_command(_args):
    sys.exit(0)

def echo_command(args):
    print(" ".join(args))

def type_command(args):
    if args[0] in builtin_commands:
        print(f"{args[0]} is a shell builtin")
    else:
        executable = find_executable(args) 
        if executable:
            print(f"{args[0]} is {executable}")
        else:
            print(f"{args[0]}: not found")

def find_executable(args):
    for path_dir in path_dirs:
            path_candidate = os.path.join(path_dir, args[0])
            if os.path.exists(path_candidate):
                if os.access(path_candidate, os.X_OK):
                    return path_candidate
    return None # os.execv(path_candidate, args[1:])
                
def pwd_command(_args):
    print(os.getcwd())

builtin_commands = {
    "exit": exit_command,
    "echo": echo_command,
    "type": type_command,
    "pwd": pwd_command,}

def evaluate_command(command_string):
    command, *args = command_string.split()
    if command in builtin_commands:
        builtin_commands[command](args)
    else:
        executable = find_executable([command])
        if executable:
            os.spawnv(os.P_WAIT, executable, [command] + args)
        else:                               
            handle_invalid_command(command_string)

def run_repl():
    command = prompt_user()
    evaluate_command(command)

def main():
    while True:
        run_repl()
        


if __name__ == "__main__":
    main()
