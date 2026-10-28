import readline
import sys
import os
import subprocess
from contextlib import redirect_stdout, redirect_stderr, nullcontext

IS_MAC = sys.platform == "darwin"
STDOUT = sys.stdout
STDERR = sys.stderr
path_dirs = os.environ.get("PATH", "").split(":")


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
all_commands= set(builtin_commands.keys())
for path_dir in path_dirs:
    try:
        executables= os.listdir(path_dir)
        all_commands.update(executables)
    except:
        pass
all_commands = sorted(all_commands)

def completer(text, state):
    whole_line = readline.get_line_buffer()
    if len(text) == len(whole_line):
        matches = [cmd + " " for cmd in all_commands if cmd.startswith(text)]
    else: 
        matches = [file[len(text):] + " " for file in os.listdir(os.getcwd()) if file.startswith(text)]
    return matches[state] if state < len(matches) else None

def setup_readline():
    readline.set_completer(completer)
    # GNU readline
    readline.parse_and_bind("tab: complete")
    # macOS libedit (Python's readline on Darwin)
    if(IS_MAC):
        readline.parse_and_bind("bind ^I rl_complete") #this eats 'b's mysteriously on the CI machine, comment for CI

def prompt_user():
    sys.stdout = STDOUT
    sys.stderr = STDERR
    line = input("$ ")
    return line




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
        elif ch == "\\": #escaping is same in or out of double quotes
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

def peel_redirects(raw):
    peeled = []
    out_path = None
    err_path = None
    append_out=False
    append_err = False
    i = 0
    while i < len(raw):
        token = raw[i]
        if token in [">>", "1>>"]:
            i += 1
            out_path = raw[i]
            append_out = True
        elif token in [">", "1>"]:
            i += 1
            out_path = raw[i]
        elif token == "2>>":
            i += 1
            err_path = raw[i]  
            append_err = True          
        elif token == "2>":
            i += 1
            err_path = raw[i]            
        else:
            peeled.append(token)
        i += 1 
    return peeled, out_path, append_out, err_path, append_err

def evaluate_command(command_string):
    raw_tokens = lex(command_string)
    peeled_tokens, out_path, append_out, err_path, append_err = peel_redirects(raw_tokens)
    command, *args = peeled_tokens
    #set io context
    out = open(out_path, "a" if append_out else "w") if out_path else nullcontext()
    err = open(err_path, "a" if append_err else "w") if err_path else nullcontext()
    with (
    redirect_stdout(out) if out_path else nullcontext(),
    redirect_stderr(err) if err_path else nullcontext(),
    ):
        if command in builtin_commands:
            builtin_commands[command](args)
        else:
            executable = find_executable([command])
            if executable:
                subprocess.run(
                    [command, *args],
                    executable=executable,
                    stdout=out if out_path else None,  # open file, or None = inherit
                    stderr=err if err_path else None,
                )
            else:                               
                handle_invalid_command(command_string)

def run_repl():
    command = prompt_user()
    evaluate_command(command)

def main():
    setup_readline()
    while True:
        run_repl()
    
if __name__ == "__main__":
    main()
