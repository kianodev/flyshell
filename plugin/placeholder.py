# \plugin\placeholder.py
# This file functions as a placeholder for future plugins
# Right now, it literally just returns the context and args. That's it

def run(context, args):
    print("\nPlaceholder Plugin")
    print(context)
    if args:
        print(args)
    print("\nReturning...\n")