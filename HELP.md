# Psychological Talent Identification App

This application is a desktop GUI tool for recording, scoring, and searching psychological test results. It is built with Python and PyQt5.

## Features
- Merge multiple entity JSON files, removing duplicates
- Visual editor for creating/editing keys/questions (auto-opens if keys.json missing)
- Add new test entries (name, phone, answers)
- Automatic scoring and description lookup based on answers
- Search entries by name or phone
- View details and descriptions for each entry
- Sort entries by name or score (click table headers)
- Edit and delete entries (right-click or select entry)
- Remove duplicate entries (auto-removal tool)
- Data is saved in JSON files for persistence
- Footer shows last modified date (Gregorian/Shamsi) and total number of entries

## How It Works

### Main Files
- `merged_entities.json`: Example output from the Merge Entities tool
- `psycho_app.py`: Main application code (PyQt5 GUI)
- `keys.json`: Defines the scoring and descriptions for each question and answer
- `entries.json`: Stores all user entries (created automatically)
- `YASA.ico`: Application icon (optional)

### Adding an Entry
If `keys.json` is missing, the app will prompt you to create it with a visual editor before you can add entries.
1. Click **Add Entry**.
2. Enter the person's name, phone, and answers (one letter per question, e.g. `abccbadcda`).
   - The number of answers must match the number of questions in `keys.json`.
   - Each answer must be one of `a`, `b`, `c`, or `d`.
3. The app calculates the total score and shows descriptions for each answer.
4. The entry is saved to `entries.json`.

- Click **Search** and enter a name or phone number.
- Double-click a result to see full details and answer descriptions.
Click **Search** and enter a name or phone number.
Double-click a result to see full details and answer descriptions.
- Click **Search** and enter a name or phone number.
- Double-click a result to see full details and answer descriptions.

### Sorting
Click the table headers to sort by name or score.
### Editing, Deleting, and Removing Duplicates
To merge entity files:
- Go to Tools > Merge Entity Files, select two or more JSON files, and merge them into one file (duplicates are removed automatically).
## Keys Editor Window

The Keys Editor allows you to create or edit the questions, answer keys, and descriptions used for scoring. It opens automatically if `keys.json` is missing, or can be accessed from Tools > Edit Keys.

- Each row is a question. For each answer (a, b, c, d), enter the score and a description.
- Use Add Question to add more questions, or Delete Selected to remove a question.
- Click Save to write changes to `keys.json`.
To edit or delete an entry:
- Right-click an entry in the main table (or select and use the context menu)
- Choose **Edit** to modify the entry's details and answers
- Choose **Delete** to remove the entry from the list
- In the Search window, select a result and use the Edit or Delete buttons to modify or remove entries directly from the search results.

To remove duplicate entries:
- Click the **Remove Duplicates** button on the main page
- The tool will automatically find and remove duplicate entries (same name, phone, and answers)
- A message will show how many duplicates were removed

All changes are saved automatically.

## How to Change `keys.json` for Different Questions

The `keys.json` file defines the scoring and descriptions for each question. Its structure is:

```
{
  "keys": [
    {"a": 1, "b": 2, "c": 3, "d": 4},
    ... (one dict per question)
  ],
  "descriptions": [
    {"a": "desc for a", "b": "desc for b", "c": "desc for c", "d": "desc for d"},
    ... (one dict per question)
  ]
}
```

- Each element in `keys` and `descriptions` corresponds to one question.
- Each question must have all four answer keys: `a`, `b`, `c`, `d`.
- The number of questions is determined by the length of the `keys` (and `descriptions`) list.

#### Example for 3 questions:
```
{
  "keys": [
    {"a": 1, "b": 0, "c": 2, "d": 3},
    {"a": 2, "b": 1, "c": 0, "d": 3},
    {"a": 0, "b": 2, "c": 1, "d": 3}
  ],
  "descriptions": [
    {"a": "Low", "b": "Medium", "c": "High", "d": "Very High"},
    {"a": "Type A", "b": "Type B", "c": "Type C", "d": "Type D"},
    {"a": "Red", "b": "Blue", "c": "Green", "d": "Yellow"}
  ]
}
```

## Can I Extend or Shorten the Number of Questions?

**Yes!**
- The app is **not** hardcoded to 10 questions.
- The number of questions is determined by the length of the `keys` and `descriptions` lists in `keys.json`.
- When adding an entry, the number of answer letters you enter must match the number of questions.
- To change the number of questions:
  1. Edit `keys.json` and add or remove question objects in both `keys` and `descriptions`.
  2. Make sure both lists are the same length and each answer (`a`-`d`) is present for every question.

**Note:** Existing entries in `entries.json` may not match the new question count if you change it after data has been entered.

## Version History

### v4.0.0 (Class Management)
- New: Class Management menu available under the menu bar. Use Tools -> Class Management -> Classes to open the Classes manager.
- Data persistence: Classes, class students, class dates and attendance are stored in a separate SQLite database named `class.sqlite3`. The database is created automatically when you first open Class Management. If you prefer not to include this DB in your Git repository, add `class.sqlite3` to your `.gitignore` file.
- Classes dialog: Create, edit, delete classes and double-click a class to open the Class View.
- Class View features:
  - Student Picker: a searchable list of entries from `entries.json` allowing selective addition of students to a class (no automatic importing of all students).
  - Dates: Add or delete dates (rows). Each date row lets you mark a student present and enter a small numeric score.
  - Totals: A summary row is displayed at the top showing per-student totals across recorded dates.
  - Save: Persists attendance and scores into `class.sqlite3`.
  - Timer/Alarm: A simple toolbar in Class View provides a countdown timer (enter seconds) with Start/Pause/Reset and an audible beep + popup when time expires.

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

## Using Class Management

1. Open the menu: Tools -> Class Management -> Classes.
2. Create a new class using Add Class and define name, days, start/end times.
3. Double-click a class row to open Class View.
4. In Class View use "Import Students" to open the Student Picker and search/select students from `entries.json`.
5. Use Add Date to record a new session date. For each student/date mark Present and/or enter a score. Click Save to persist.
6. Totals are shown at the top. Use Delete Student to remove a student from a class (this also deletes attendance records for that student in the class).

## Notes for developers
- The class feature was added in a non-invasive way so existing JSON-based entry flows are unchanged. All class-related data is kept in `class.sqlite3`.
- Minimal dialog implementations were added for AddEntry and Search to ensure compatibility; you can replace or enhance those dialogs as needed.

## Author
Made by: Mohammadreza Hassanpour Koumeleh 
Email: engineer.mrhp@gmail.com
