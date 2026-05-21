# Pokémon Sleep Skill Trigger Tracker

Windows desktop app for tracking skill trigger records in Pokémon Sleep.

## Features

- System tray resident app with **Ctrl+Alt+P** global hotkey to show/hide
- Pokémon cards in a responsive 16:9 grid
- Create Pokémon, view details, add trigger records (team of up to 5)
- View history, statistics, and trigger time distribution chart

## Requirements

- Python 3.10+
- Windows 10/11

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Package (Windows exe)

```bash
pyinstaller pokemon_sleep_tracker.spec
```

Output: `dist/PokemonSleepSkillTracker.exe`

Database is stored in `data/pokemon_sleep.db` next to the executable (or project root when running from source).

## Project layout

```
main.py
app/
  application.py      # Tray, hotkey, lifecycle
  models.py
  database.py
  services.py
  styles/
  system/
  widgets/
  windows/
```
