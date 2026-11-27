# src/flyshell/main.py

import os
import sys


def main() -> None:
    os.system("")
    print("\033[H\033[2J", end="")
    print("\nLaunch process initiated. Flyshell is checking it is able to launch...")
    try:
        from flyshell import startup

        if startup.run_preflight():
            startup.launch()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nFlyshell session terminated, shutting down...\n")
        sys.exit(0)
    except Exception as e:
        print("\n❌❌❌ Oops! An unexpected error occurred.")
        print(f"Error details: {e}")
        print("We don't really know what happened there. Sorry about that.\n")
        print("Print traceback message? Default is N.")
        choice = input("[y/n]?: ")
        if choice.lower() == "y":
            import traceback

            raw = traceback.extract_tb(e.__traceback__)
            last_frame = raw[-1]
            print("\nTraceback details:")
            print(f"File: '{last_frame[0]}'")
            print(f"Line: {last_frame[1]}")
            print(f"Exception message: '{e}'")
        sys.exit(1)
    finally:
        try:
            from flyshell import startup

            startup.shutdown()
        except ImportError:
            pass


if __name__ == "__main__":
    main()
