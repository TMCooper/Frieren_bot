import sys
import os
import traceback

print("Current working directory:", os.getcwd())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("Sys.path:", sys.path)

try:
    import commands
    print("Imported commands package")
except ImportError:
    print("Failed to import commands package")
    traceback.print_exc()

try:
    from commands.General import General
    print("Imported commands.General.General")
except ImportError:
    print("Failed to import commands.General.General")
    traceback.print_exc()
except Exception:
    print("Other error importing commands.General")
    traceback.print_exc()
