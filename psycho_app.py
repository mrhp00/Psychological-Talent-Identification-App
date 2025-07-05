
# Standard library imports
import sys
import json
import os
# PyQt5 imports for GUI components
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView, QMenuBar, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


# File paths for keys and entries
KEYS_FILE = 'keys.json'
ENTRIES_FILE = 'entries.json'


def load_keys():
    """
    Load the keys and descriptions from the keys.json file.
    Returns:
        keys (list): List of dicts mapping answer letters to scores.
        descriptions (list): List of dicts mapping answer letters to descriptions.
    """
    with open(KEYS_FILE, encoding='utf-8') as f:
        data = json.load(f)
    return data['keys'], data['descriptions']


def load_entries():
    """
    Load all entries from entries.json. Returns an empty list if file does not exist.
    """
    if not os.path.exists(ENTRIES_FILE):
        return []
    with open(ENTRIES_FILE, encoding='utf-8') as f:
        return json.load(f)


def save_entries(entries):
    """
    Save the list of entries to entries.json.
    """
    with open(ENTRIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


class AddEntryDialog(QDialog):
    """
    Dialog for adding a new entry (person's answers to the test).
    """
    def __init__(self, keys, descriptions, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Entry')
        self.setWindowIcon(QIcon('YASA.ico'))
        self.keys = keys
        self.descriptions = descriptions
        self.result_entry = None
        layout = QVBoxLayout()
        # Input fields for name, phone, and answers
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Name')
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Phone')
        self.answers_input = QLineEdit()
        self.answers_input.setPlaceholderText(f'Answers ({len(self.keys)} letters, a-d)')
        self.result_label = QLabel()
        add_btn = QPushButton('Add')
        add_btn.clicked.connect(self.add_entry)
        layout.addWidget(QLabel('Name:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel('Phone:'))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel('Answers:'))
        layout.addWidget(self.answers_input)
        layout.addWidget(add_btn)
        layout.addWidget(self.result_label)
        self.setLayout(layout)
        self.setMinimumWidth(350)

    def add_entry(self):
        """
        Validate input and calculate the total score and descriptions for the answers.
        Save the result in self.result_entry and show a message box.
        """
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        answers = self.answers_input.text().strip().lower()
        # Validate: name, phone, answers length, and valid answer letters
        if not (name and phone and len(answers) == len(self.keys) and all(c in 'abcd' for c in answers)):
            self.result_label.setText('Invalid input!')
            return
        total = 0
        descs = []
        for i, ans in enumerate(answers):
            key = self.keys[i][ans]
            total += key
            descs.append(self.descriptions[i][ans])
        desc_text = '\n'.join(f'- {d}' for d in descs)
        self.result_label.setText(f'Total Score: {total}\nDescriptions:\n{desc_text}')
        self.result_entry = {'name': name, 'phone': phone, 'answers': answers, 'score': total}
        QMessageBox.information(self, 'Entry Added', f'Total Score: {total}\nDescriptions:\n{desc_text}')
        self.accept()


class SearchDialog(QDialog):
    """
    Dialog for searching entries by name or phone and viewing their details.
    """
    def __init__(self, entries, keys, descriptions, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Search Entry')
        self.setWindowIcon(QIcon('YASA.ico'))
        self.entries = entries
        self.keys = keys
        self.descriptions = descriptions
        layout = QVBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText('Enter name or phone')
        # Table to show search results
        self.result_table = QTableWidget(0, 3)
        self.result_table.setHorizontalHeaderLabels(['Name', 'Phone', 'Score'])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setSelectionMode(QTableWidget.SingleSelection)
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.do_search)
        self.result_table.cellDoubleClicked.connect(self.show_details)
        layout.addWidget(self.query_input)
        layout.addWidget(search_btn)
        layout.addWidget(self.result_table)
        self.setLayout(layout)
        self.setMinimumWidth(500)


    def do_search(self):
        """
        Search for entries where the query matches the name or phone.
        Populate the result table with matches.
        """
        q = self.query_input.text().strip()
        results = [e for e in self.entries if q in e['name'] or q in e['phone']]
        self.result_table.setRowCount(0)
        for e in results:
            row = self.result_table.rowCount()
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(e['name']))
            self.result_table.setItem(row, 1, QTableWidgetItem(e['phone']))
            self.result_table.setItem(row, 2, QTableWidgetItem(str(e['score'])))
        self.results = results


    def show_details(self, row, col):
        """
        Show a message box with details and descriptions for the selected entry.
        """
        if not hasattr(self, 'results') or row >= len(self.results):
            return
        entry = self.results[row]
        answers = entry['answers']
        descs = [self.descriptions[i][a] for i, a in enumerate(answers)]
        desc_text = '\n'.join(f'- {d}' for d in descs)
        QMessageBox.information(self, 'Entry Details', f"Name: {entry['name']}\nPhone: {entry['phone']}\nTotal Score: {entry['score']}\nDescriptions:\n{desc_text}")


class MainWindow(QMainWindow):
    """
    Main application window. Shows the table of entries and provides access to add/search dialogs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Psychological Talent Identification')
        self.setWindowIcon(QIcon('YASA.ico'))
        # Load keys and descriptions from keys.json
        self.keys, self.descriptions = load_keys()
        # Load all entries from entries.json
        self.entries = load_entries()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        # Add Entry, Edit, Delete, and Search buttons
        add_btn = QPushButton('Add Entry')
        add_btn.clicked.connect(self.open_add_entry)
        edit_btn = QPushButton('Edit Entry')
        edit_btn.clicked.connect(self.open_edit_entry)
        delete_btn = QPushButton('Delete Entry')
        delete_btn.clicked.connect(self.open_delete_entry)
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.open_search)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(search_btn)
        # Table to show all entries
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Name', 'Phone', 'Score'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.table.cellDoubleClicked.connect(self.show_details)
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.central.setLayout(layout)
        self.refresh_table()
        self.setMinimumWidth(600)
        # Add menu bar and About action
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder


    def show_about(self):
        """
        Show information about the app and author.
        """
        QMessageBox.information(self, 'About',
            'Made by: Mohammadreza Hassanpour\nEmail: engineer.mrhp@gmail.com')


    def show_details(self, row, col):
        """
        Show details and descriptions for the selected entry in the main table.
        """
        if row >= len(self.entries):
            return
        entry = self.entries[row]
        answers = entry['answers']
        descs = [self.descriptions[i][a] for i, a in enumerate(answers)]
        desc_text = '\n'.join(f'- {d}' for d in descs)
        QMessageBox.information(self, 'Entry Details', f"Name: {entry['name']}\nPhone: {entry['phone']}\nTotal Score: {entry['score']}\nDescriptions:\n{desc_text}")


    def sort_table(self, column):
        """
        Sort the table by the selected column (name or score).
        """
        if self.sort_column == column:
            # Toggle sort order
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_column = column
            self.sort_order = Qt.AscendingOrder
        if column == 0:
            self.entries.sort(key=lambda e: e['name'], reverse=self.sort_order == Qt.DescendingOrder)
        elif column == 2:
            self.entries.sort(key=lambda e: e['score'], reverse=self.sort_order == Qt.DescendingOrder)
        self.refresh_table()


    def refresh_table(self):
        """
        Refresh the main table with all entries.
        """
        self.table.setRowCount(0)
        for e in self.entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(e['name']))
            self.table.setItem(row, 1, QTableWidgetItem(e['phone']))
            self.table.setItem(row, 2, QTableWidgetItem(str(e['score'])))


    def open_add_entry(self):
        """
        Open the Add Entry dialog and add the new entry if accepted.
        Refresh entries from file after adding.
        """
        dlg = AddEntryDialog(self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        if dlg.exec_() == QDialog.Accepted and dlg.result_entry:
            entries = load_entries()
            entries.append(dlg.result_entry)
            save_entries(entries)
            self.entries = load_entries()  # Ensure entries are reloaded from file
            self.refresh_table()

    def open_edit_entry(self):
        """
        Edit the selected entry in the table.
        """
        row = self.table.currentRow()
        if row < 0 or row >= len(self.entries):
            QMessageBox.warning(self, 'Edit Entry', 'Please select an entry to edit.')
            return
        entry = self.entries[row]
        dlg = AddEntryDialog(self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        dlg.name_input.setText(entry['name'])
        dlg.phone_input.setText(entry['phone'])
        dlg.answers_input.setText(entry['answers'])
        if dlg.exec_() == QDialog.Accepted and dlg.result_entry:
            entries = load_entries()
            # Find and update the entry by unique fields (name+phone+answers)
            for i, e in enumerate(entries):
                if e['name'] == entry['name'] and e['phone'] == entry['phone'] and e['answers'] == entry['answers']:
                    entries[i] = dlg.result_entry
                    break
            save_entries(entries)
            self.entries = load_entries()
            self.refresh_table()

    def open_delete_entry(self):
        """
        Delete the selected entry in the table.
        """
        row = self.table.currentRow()
        if row < 0 or row >= len(self.entries):
            QMessageBox.warning(self, 'Delete Entry', 'Please select an entry to delete.')
            return
        entry = self.entries[row]
        reply = QMessageBox.question(self, 'Delete Entry', f"Are you sure you want to delete entry for {entry['name']}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            entries = load_entries()
            # Remove by unique fields (name+phone+answers)
            entries = [e for e in entries if not (e['name'] == entry['name'] and e['phone'] == entry['phone'] and e['answers'] == entry['answers'])]
            save_entries(entries)
            self.entries = load_entries()
            self.refresh_table()


    def open_search(self):
        """
        Open the Search dialog for searching entries.
        """
        dlg = SearchDialog(self.entries, self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        dlg.exec_()


# Entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
