# Ludex
Latin "ludus" (game) + dex (index)

This is a simple home page and collection of utilities for whatever game I'm currently obsessed with, built with Dash. I wanted to have a collection of interactive tools that help me understand game systems and make informed decisions, without having to dig through spreadsheets or wiki pages. 

I made a Dash AG Grid enemy database for Xenosaga a few years ago and found it really fun to build and actually super useful, so I decided to expand that concept into a more general project that can host tools for multiple games.

## What Ludex Includes

Current pages in this repository:

- `Xenosaga`
  - Enemy database with sortable, filterable AG Grid tables for Episodes I, II, and III
  - Row-click modal for full enemy details
- `Clair Obscur: Expedition 33`
  - Skill damage data browser (not that useful since I have the calculator below)
  - Skill damage calculator
  - Zone level reference table

## Stack

- `Dash` for routing, layout, and callbacks
- `dash-ag-grid` for interactive data tables
- `dash-bootstrap-components` and `dash-mantine-components` for UI
- `pandas` for data loading and shaping
- `gunicorn` for production serving
- `uv` for dependency management

## Project Layout

```text
.
├── app.py                         # Dash app entrypoint and home page
├── games/                         # Dash pages, grouped by game
│   ├── expedition33/
│   └── xenosaga/
├── assets/                        # CSS, JS, CSVs, SQLite DB, static helpers
├── helpers/                       # Shared utility code
├── pyproject.toml                 # Project metadata and dependencies
└── Dockerfile                     # Container build for deployment
```

`app.py` enables Dash Pages with `pages_folder="games"`, so any module under `games/` that calls `register_page(...)` becomes part of the site automatically.

## Running Locally

### With `uv`

```bash
uv sync
uv run python app.py
```

The development server starts on Dash's default local port.

### With Gunicorn

```bash
uv sync
uv run gunicorn -b 0.0.0.0:8080 --workers=4 --preload app:server
```

## Running With Docker

Build the image:

```bash
docker build -t ludex .
```

Run the container:

```bash
docker run --rm -p 8080:8080 ludex
```

Then open `http://localhost:8080`.

## Adding a New Game Page

1. Create a module under `games/<game_name>/`.
2. Define a `layout`.
3. Register the page with Dash using `register_page(...)`.
4. Restart the app.

Once registered, the home tree in `app.py` will automatically group the page under that game.

## Notes

- The top-level app is intentionally generic so multiple games can live in one project.
- Some game-specific pages have their own README files with deeper implementation notes and source attribution.
-- Clair Obscur: Expedition 33: see `games/expedition33/calculator/README.md` for details on the design and data sources for the Expedition 33 skill damage calculator.
-- Xenosaga: see `games/xenosaga/README.md` for details on the enemy database pages, including data sources and design notes.