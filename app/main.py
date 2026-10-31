import readline
import sys
import os
import subprocess
from contextlib import redirect_stdout, redirect_stderr, nullcontext

def handle_unraisable(args): #CI garbage collection is too aggressive and creates CI specific errors.
    if isinstance(args.exc_value, OSError) and args.exc_value.errno == 9: # I use both a high level wrapper and its low level file descriptor. I manually close fd, but CI garbage collection freaks out about not closing the high level. detach didn't work see handle_pipeline()
        return # just avoid this one error
    sys.__unraisablehook__(args)

sys.unraisablehook = handle_unraisable

IS_MAC = sys.platform == "darwin"
STDOUT = sys.stdout
STDERR = sys.stderr
PATH_DIRS = os.environ.get("PATH", "").split(":")

global_commands = None
completer_scripts = dict()
history=list()

jobs=list()
class Job():
    job_counter = 1
    def __init__(self, process, command_string):
        self.pid = process.pid
        self.process = process
        self.command_string = command_string
        if len(jobs) == 0:
            Job.job_counter = 1
        else: 
            Job.job_counter = 1 + max(j.job_number for j in jobs)
        self.job_number = Job.job_counter

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
    name = args[0]
    if "/" in name:
        path = name if os.path.isabs(name) else os.path.join(os.getcwd(), name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
        return None
    for path_dir in PATH_DIRS:
        path_candidate = os.path.join(path_dir, name)
        if os.path.isfile(path_candidate) and os.access(path_candidate, os.X_OK):
            return path_candidate
    return None
                
def pwd_command(_args):
    print(os.getcwd())

def cd_command(args):
    home = os.environ.get("HOME", "")
    if not args:
        return os.chdir(home)
    arg = args[0]
    if arg.startswith("~"):
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

# def parse_args(args):
    # flagged = dict()
    # ordered = []
    # i = 0
    # while i < len(args):
    #     arg = args[i]
    #     if arg.startswith("-"):
    #         i += 1
    #         flagged[arg[1:]] = args[i]
    #     else:
    #         ordered.append(arg)
    #     i += 1
    # return flagged, ordered

def complete_command(args):
    # flagged, _ordered = parse_args(args)
    if args[0] == "-p":
        if args[1] in completer_scripts:
            print(f"complete -C '{completer_scripts[args[1]]}' {args[1]} ")
        else:
            print(f"complete: {args[1]}: no completion specification")
    elif args[0] == "-C":
        completer_scripts[args[2]] = args[1]
    elif args[0] == "-r":
        completer_scripts.pop(args[1])

def jobs_command(autoreap=False):
    for j in jobs[:]:
        should_reap = j.process.poll() is not None
        recency = "+" if j is jobs[-1] else "-" if j is jobs[-2] else " "
        # if not autoreap or (autoreap and should_reap):
        if (not autoreap) or should_reap:
            print(f"[{j.job_number}]{recency}  {('Done' if should_reap else 'Running').ljust(24)}{j.command_string[:-1] if should_reap else j.command_string}")
        
        if should_reap:
            jobs.remove(j)
    
def history_command(args):
    if len(args) == 0:
        limit = None
    elif args[0] == "-r":
        history_path = args[1]
        with open(history_path, "r") as history_file:
            history.extend([h.rstrip() for h in history_file if h])
        return
    elif args[0] == "-w":
        history_path = args[1]
        with open(history_path, "w") as history_file:
            history_file.write("\n".join(history)+"\n")
        return 
    else:
        limit = int(args[0])
    for i, command in enumerate(history):
        if not limit or i >= len(history) - limit:
            print(f"{str(i+1).rjust(5)}  {command}")

builtin_commands = {
    "exit": exit_command,
    "echo": echo_command,
    "type": type_command,
    "pwd": pwd_command,
    "cd": cd_command,
    "complete": complete_command,
    "jobs": jobs_command,
    "history": history_command
}
def register_commands():
    global global_commands
    all_commands= set(builtin_commands.keys())
    for path_dir in PATH_DIRS:
        try:
            executables= os.listdir(path_dir)
            all_commands.update(executables)
        except:
            pass
    global_commands = sorted(all_commands)

def completer(text, state):
    buffer = readline.get_line_buffer()
    buffer_tokens = buffer.split()
    if buffer_tokens[0] in completer_scripts:
        if state == 0:
            result = subprocess.run(
                        [completer_scripts[buffer_tokens[0]], buffer_tokens[0], text, buffer_tokens[-2] if len(buffer_tokens) > 1 else "" ],
                        capture_output=True,  # Captures both stdout and stderr
                        text=True,  
                        env = {
                            "COMP_LINE": buffer,
                            "COMP_POINT": str(len(buffer))
                        }   
                        )
            completer._cleaned = [line.strip() + " " for line in result.stdout.splitlines() if line.startswith(text)]
        try: 
            return completer._cleaned[state]
        except:
            return None
    if readline.get_begidx() == 0:
        matches = [cmd + " " for cmd in global_commands if cmd.startswith(text)]
    elif "/" in text:
        path, prefix = text.rsplit("/", 1)
        matches = [(path + "/" + file + (" " if os.path.isfile(os.path.join(os.getcwd(),path, file)) else "/")) 
                    for file in os.listdir(os.path.join(os.getcwd(), path)) 
                    if file.startswith(prefix)]
    else: 
        matches = [file + (" " if os.path.isfile(os.path.join(os.getcwd(),file)) else "/") 
                    for file in os.listdir(os.getcwd()) 
                    if text in file]
    return matches[state] if state < len(matches) else None
completer.cleaned = []

def setup_readline():
    register_commands()
    readline.set_completer(completer)
    readline.set_completer_delims(" \t\n")
    readline.parse_and_bind("tab: complete")            # GNU readline
    if(IS_MAC):                                         # macOS libedit (Python's readline on Darwin)
        readline.parse_and_bind("bind ^I rl_complete")  # eats 'b's on the CI machine libedit implementation

def prompt_user():
    sys.stdout = STDOUT
    sys.stderr = STDERR
    jobs_command(autoreap= True)
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

def background_pass(peeled):
    if peeled[-1] == "&":
        return True, peeled[:-1]
    else:
        return False, peeled

def handle_pipeline(command_stages):
    prev_read_end = None
    prev_write_end = None
    for command_stage in command_stages:
        (r,w) = os.pipe()
        command, *args = command_stage
        if command in builtin_commands:
            pipe_write_stream = os.fdopen(w, "w")
            with redirect_stdout(pipe_write_stream):
                builtin_commands[command](args)
            pipe_write_stream.flush()
            # pipe_write_stream.detach()
        else:
            subprocess.Popen(command_stage, stdout=w, stdin = prev_read_end)
        if prev_write_end:
            os.close(prev_write_end)
        prev_read_end, prev_write_end = r, w
    os.close(prev_write_end)
    with os.fdopen(prev_read_end, "rb") as stream:
        for line in stream:
            print(line.decode('utf-8').rstrip())

def evaluate_command(command_string):
    history.append(command_string)
    if "|" in command_string:
        commands = command_string.split("|")
        lexed = [lex(command) for command in commands]
        return handle_pipeline(lexed)
    raw_tokens = lex(command_string)     
    peeled_tokens, out_path, append_out, err_path, append_err = peel_redirects(raw_tokens)
    is_background, bg_tokens = background_pass(peeled_tokens)
    command, *args = bg_tokens
    #set io context
    out = open(out_path, "a" if append_out else "w") if out_path else nullcontext()
    err = open(err_path, "a" if append_err else "w") if err_path else nullcontext()
    with (
    redirect_stdout(out) if out_path else nullcontext(),
    redirect_stderr(err) if err_path else nullcontext(),
    ):
        if command in builtin_commands:
            builtin_commands[command](args)
            # spawn a subshell to handle background process
        else:
            executable = find_executable([command])
            if executable:
                if is_background:
                    p = subprocess.Popen([command, *args],
                        executable=executable,
                        stdout=out if out_path else None,  # open file, or None = inherit
                        stderr=err if err_path else None,
                    )
                    new_job = Job(p, command_string)
                    jobs.append(new_job)
                    print(f"[{new_job.job_number}] {new_job.pid}")
                else:
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
    if command.strip() == "":
        return
    evaluate_command(command)

def main():
    setup_readline()
    while True:
        run_repl()
    
if __name__ == "__main__":
    main()
