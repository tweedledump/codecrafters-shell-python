# IT'S A SHELL

This is Nick's Python solution to the
["Build Your Own Shell" Challenge](https://app.codecrafters.io/courses/shell/overview).

In this challenge, he built his own POSIX compliant shell that's capable of
interpreting shell commands, running external programs and builtin commands like
cd, pwd, echo and more. Along the way, he learned about shell command parsing,
REPLs, builtin commands, and more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.

## Goals
This was a super fun exercise, and a fine way to shake some rust off after a couple months break.

The goal was to get this finished within the week while running tests was still free (challenge of the month for Cctober), in which I expected to spend 20-25 hours coding, so I made some executive decisions:
- Focus on the happy paths
- Save robust error handling and io corner cases for a future revision
- Emphasize a procedural rather than object oriented approach, since there were shells before oop gained widespread traction
- See if I can get it done with less

Python's readline module already solved many of the challenge stages, if I wanted to dive deeper I'd look deeper into that package, maybe reengineer it.

## Workflow

Besides exploring enginnering a shell, I wanted to explore integrating AI into my workflow. 
I initially used the free version of Cursor as my IDE. 
As soon as I prohibited it from mangling --I mean editing-- my code, and focused on asking it to assemble documentation and examples, review test cases for bugs and to help me consider corner cases, I rather enjoyed my time with the tool until I ran out of free prompts.
Then I used google.com AI Mode for similar help. 
More copying and pasting, but only slightly less accurate assessments of code. 
Definitely more bugs in suggested outputs, but there were plenty of garbage suggestions with Cursor as well. 
I'd say in the context of this project about 7% of prompts gave responses whose value I estimate approached the environmental cost, and 5% gave grave misinformation.
Probably 5x better accuracy, and 8x fewer grave errors, than when I ask it for geo-political facts.

Anyway, Happy Halloween! If you'd to leave a time capsule full of spooky vibes to your maintainers, let cursor write all your code! *Not responsible if you mistake tricks for treats, or if your repo gets diabetes