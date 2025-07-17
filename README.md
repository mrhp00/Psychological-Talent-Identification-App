# Psychological Talent Identification App

A simple, user-friendly desktop application for recording, scoring, and searching psychological test results. Built with Python and PyQt5, this app allows you to define your own test questions and scoring system via a JSON file, making it flexible for different psychological or talent assessment scenarios.

## Features
- Merge multiple entity JSON files, removing duplicates
- Create or edit keys/questions with a visual editor (auto-opens if keys.json missing)
- Add new test entries with name, phone, and answers
- Automatic scoring and answer description lookup
- Search and view entries by name or phone
- Sort entries by name or score (click table headers)
- Edit and delete entries (right-click or select entry)
- Remove duplicate entries (auto-removal tool)
- All data is stored in editable JSON files
- Easily customize the test by editing `keys.json`
- Footer shows last modified date (Gregorian/Shamsi) and total number of entries
- Search window allows editing and deleting entries directly

## Getting Started
1. Install Python 3 and PyQt5 (`pip install pyqt5`)
2. Clone this repository
3. Run `psycho_app.py`
4. If `keys.json` is missing, the app will prompt you to create it with a visual editor. You can also edit questions/keys later from the Tools menu.

## Customization
- The number and content of questions is fully customizable via `keys.json`.
- See `HELP.md` for detailed instructions on usage and customization.


## Version History
### v3.0.0
- New: Merge Entities tool to combine multiple entity files and remove duplicates
- New: Visual Keys Editor for creating/editing questions and answer keys (auto-opens if keys.json missing)

### v2.2.0
- Footer now shows total number of entries
- Search window allows editing and deleting entries directly
### v2.1.0
- New: Remove Duplicates tool to auto-remove duplicate entries
- Footer shows last modified date in both Gregorian and Shamsi (Persian) calendars
- Live update of entity list after add, edit, delete, and search actions

### v2.0.0
- Bug fixes: PyInstaller/PyQt5 packaging, icon support, and data handling
- New features: Edit and delete entries from the main table

## Author
Made by: Mohammadreza Hassanpour Koumeleh  
Email: engineer.mrhp@gmail.com
