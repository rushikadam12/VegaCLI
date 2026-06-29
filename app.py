import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add workspace to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from cli.app import main

if __name__ == "__main__":
    main()
