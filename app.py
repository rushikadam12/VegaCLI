import os
import sys
from dotenv import load_dotenv


load_dotenv()

# Add workspace to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from vega_cli.cli.app import main
from rich.console import Console

console = Console()

console.print("Hello VegaCLI")


if __name__ == "__main__":
    main()
