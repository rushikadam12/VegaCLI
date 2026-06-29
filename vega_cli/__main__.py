from vega_cli.cli.app import main

# Expose main as 'app' for the project scripts mapping if Typer/Click expectation varies
app = main

if __name__ == "__main__":
    main()
