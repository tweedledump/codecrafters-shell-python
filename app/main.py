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

def cd_command(args):
    arg = args[0]
    if arg.startswith("~"):
        home = os.environ.get("HOME", "")
        os.chdir(home)
        cd_command([arg[2:]])
    elif arg.startswith("/"):
        if os.path.exists(arg):
            os.chdir(arg)
        else:
            print(f"cd: {arg}: No such file or directory")
    elif arg.startswith("./"):
        cd_command([arg[2:]])
    elif arg.startswith(".."):
        os.chdir(os.pardir)
        cd_command([arg[3:]])
    else:
        target = os.path.join(os.getcwd(), arg)
        if os.path.exists(target):
            os.chdir(target)
        else:
            print(f"cd: {arg}: No such file or directory")    

builtin_commands = {
    "exit": exit_command,
    "echo": echo_command,
    "type": type_command,
    "pwd": pwd_command,
    "cd": cd_command,
}

def lex(stream: str)-> list[str]:
    tokens = []
    current_token = []
    in_single = False
    in_double = False
    i = 0
    while i < len(stream):
        ch = stream[i]
        if ch == "\\" and in_single:
            current_token.append(ch)
        elif ch == "\\": #and not in quotes
            i += 1
            next_ch = stream[i]
            current_token.append(next_ch)
        elif ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch.isspace() and not in_single and not in_double:
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
        else:
            current_token.append(ch)
        i += 1
    if current_token:
        tokens.append("".join(current_token))
    return tokens

def evaluate_command(command_string):
    command, *args = lex(command_string)
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
    # should i have a print phase and return all the messages

def main():
    while True:
        run_repl()
        


if __name__ == "__main__":
    main()
