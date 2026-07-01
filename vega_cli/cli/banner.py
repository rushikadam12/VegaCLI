import time
from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.live import Live

# --- Configuration & Assets ---
GRADIENT_COLORS = ["#d946ef", "#c084fc", "#a855f7", "#818cf8", "#38bdf8", "#06b6d4"]

BANNER_LINES = [
    "██╗   ██╗███████╗ ██████╗  █████╗  ██████╗██╗     ██╗",
    "██║   ██║██╔════╝██╔════╝ ██╔══██╗██╔════╝██║     ██║",
    "██║   ██║█████╗  ██║  ███╗███████║██║     ██║     ██║",
    "╚██╗ ██╔╝██╔══╝  ██║   ██║██╔══██║██║     ██║     ██║",
    " ╚████╔╝ ███████╗╚██████╔╝██║  ██║╚██████╗███████╗██║",
    "  ╚═══╝  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝",
]

# New Static Premium AI Core Logo (Replaced the blinking mascot)
VEGA_LOGO = [
    "    ▄▄████▄▄    ",
    "  ▄██████████▄  ",
    "▄████▀    ▀████▄",
    "▀████▄    ▄████▀",
    "  ▀██████████▀  ",
    "    ▀▀████▀▀    "
]


def _get_wind_stream(frame_count: int, offset: int = 0) -> Text:
    """Generates a high-speed moving wind line using text shifting mechanics."""
    base_pattern = "═══»»»══≈≈   💨   ═══»»»»  ≈≈≈≈   💨   »»»»═══≈≈≈   💨  »»»»═══»»»"
    speed_multiplier = 4 
    shift = ((frame_count + offset) * speed_multiplier) % len(base_pattern)
    shifted_str = base_pattern[shift:] + base_pattern[:shift]
    
    final_line = shifted_str[:72]
    
    styled_wind = Text()
    for char in final_line:
        if char in ["💨", "»"]:
            styled_wind.append(char, style="bold bright_white")
        elif char in ["≈", "~"]:
            styled_wind.append(char, style="bold #06b6d4")
        else:
            styled_wind.append(char, style="dim #38bdf8")
            
    return styled_wind


def _build_frame(frame_count: int, status_text: str) -> Table:
    """Helper function to construct a single layout frame with a static logo."""
    # 1. Build Text Logo Side
    text_side = Text()
    for color, line in zip(GRADIENT_COLORS, BANNER_LINES):
        text_side.append(line + "\n", style=f"bold {color}")
    
    text_side.append("\n ⚡ VegaCLI", style="bold white")
    text_side.append("  •  ", style="dim pink")
    text_side.append("AI Terminal Companion", style="bold #06b6d4")
    text_side.append("  •  ", style="dim pink")
    text_side.append("v0.1.0\n", style="italic dim white")

    # 2. Build Static Logo Side (No frame switches, matches text height perfectly)
    logo_side = Text()
    logo_side.append("\n") 
    for line in VEGA_LOGO:
        logo_side.append(line + "\n", style="bold #a855f7")

    # 3. Combine into a side-by-side grid
    content_grid = Table.grid(padding=(0, 4))
    content_grid.add_column(justify="center", vertical="middle")
    content_grid.add_column(justify="left", vertical="middle")
    content_grid.add_row(logo_side, text_side)

    # 4. Progress System Bar Footer
    footer = Text.assemble(
        (f"[ {status_text} ]", "bold #03dac6"),
    )
    
    # 5. Master Layout (Stacking Wind, Content, and Footer)
    main_layout = Table.grid()
    # main_layout.add_row(Align.center(_get_wind_stream(frame_count, offset=0))) 
    main_layout.add_row(Text(""))                                            
    main_layout.add_row(Align.center(content_grid))                          
    main_layout.add_row(Text(""))                                            
    main_layout.add_row(Align.center(footer))                                
    main_layout.add_row(Text(""))                                            
    # main_layout.add_row(Align.center(_get_wind_stream(frame_count, offset=8))) 

    return main_layout


def render_banner(animate: bool = True, console: Console = None):
    """
    Renders the upgraded VegaCLI banner layout wrapped in high-speed air current visuals.
    """
    _console = console or Console()
    _console.print() 

    if not animate:
        _console.print(_build_frame(1, "System Ready"))
        return

    phases = ["Igniting Jetstreams...", "Syncing Core Elements...", "System Optimized!"]
    total_frames = 24  
    
    with Live(_build_frame(0, "Initializing..."), console=_console, refresh_per_second=12) as live:
        for frame in range(total_frames):
            time.sleep(0.08) 
            status = phases[min(frame // 8, len(phases) - 1)]
            live.update(_build_frame(frame, status))