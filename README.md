# Psychological Talent Identification App

A simple, user-friendly desktop application for recording, scoring, and searching psychological test results. Built with Python and PyQt5, this app allows you to define your own test questions and scoring system via a JSON file, making it flexible for different psychological or talent assessment scenarios.

## Features
- Add new test entries with name, phone, and answers
- Automatic scoring and answer description lookup
- Search and view entries by name or phone
- Sort entries by name or score (click table headers)
- Edit and delete entries (right-click or select entry)
- All data is stored in editable JSON files
- Easily customize the test by editing `keys.json`

## Getting Started
1. Install Python 3 and PyQt5 (`pip install pyqt5`)
2. Clone this repository
3. Run `psycho_app.py`
4. Edit `keys.json` to define your own questions, scoring, and descriptions

## Customization
- The number and content of questions is fully customizable via `keys.json`.
- See `HELP.md` for detailed instructions on usage and customization.

## Version History

### v2.0.0
- Bug fixes: PyInstaller/PyQt5 packaging, icon support, and data handling
- New features: Edit and delete entries from the main table

## Author
Made by: Mohammadreza Hassanpour Koumeleh  
Email: engineer.mrhp@gmail.com
