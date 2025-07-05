# Psychological Talent Identification App

This application is a desktop GUI tool for recording, scoring, and searching psychological test results. It is built with Python and PyQt5.

## Features
- Add new test entries (name, phone, answers)
- Automatic scoring and description lookup based on answers
- Search entries by name or phone
- View details and descriptions for each entry
- Sort entries by name or score (click table headers)
- Edit and delete entries (right-click or select entry)
- Data is saved in JSON files for persistence

## How It Works

### Main Files
- `psycho_app.py`: Main application code (PyQt5 GUI)
- `keys.json`: Defines the scoring and descriptions for each question and answer
- `entries.json`: Stores all user entries (created automatically)
- `YASA.ico`: Application icon (optional)

### Adding an Entry
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
### Editing and Deleting Entries
To edit or delete an entry:
- Right-click an entry in the main table (or select and use the context menu)
- Choose **Edit** to modify the entry's details and answers
- Choose **Delete** to remove the entry from the list

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

### v2.0.0
- Bug fixes: PyInstaller/PyQt5 packaging, icon support, and data handling
- New features: Edit and delete entries from the main table

## Author
Made by: Mohammadreza Hassanpour Koumeleh 
Email: engineer.mrhp@gmail.com
