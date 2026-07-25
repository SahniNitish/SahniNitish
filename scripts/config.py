# Shared config for the profile-art scripts.
# Change these and re-run the generators.

USERNAME = "SahniNitish"

# ---- ASCII portrait ----
# Source image for the portrait. If it doesn't exist locally, the script
# falls back to the GitHub avatar for USERNAME.
PORTRAIT_SOURCE = "source-photo.png"
ASCII_COLS = 84                 # character columns (width of the grid)
ASCII_FILL = "#c9d1d9"          # light gray glyphs
ASCII_BG = "#0d1117"            # terminal background
RAMP = " .`:-=+*cs#%@"          # bright (sparse) -> dark (dense)

# ---- Neofetch info card ----
# Edit freely. Each row is (key, value). Keep it to the story the
# contribution graph can't tell.
INFO_TITLE = "nitish@github"
INFO_ROWS = [
    ("Now",        "Technical Analyst — building like a developer"),
    ("Focus",      "Backend & system design · React front-ends"),
    ("Languages",  "C++ · Java · Python"),
    ("Frontend",   "React · Tailwind"),
    ("Infra",      "AWS · Redis"),
    ("AI",         "RAG pipelines · model training"),
]

# ---- Heatmap palette ----
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
