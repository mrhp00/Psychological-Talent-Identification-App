# Standard library imports
import sys
import json
import os
from datetime import datetime
import jdatetime
# PyQt5 imports for GUI components
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView, QMenuBar, QAction, QFileDialog, QSpinBox, QTextEdit, QAbstractItemView, QProgressDialog
)
from PyQt5.QtCore import Qt, QTimer
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
        # Add Edit and Delete buttons for search results
        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton('Edit Selected')
        self.edit_btn.clicked.connect(self.edit_selected)
        self.delete_btn = QPushButton('Delete Selected')
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addWidget(self.query_input)
        layout.addWidget(search_btn)
        layout.addWidget(self.result_table)
        layout.addLayout(btn_layout)
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

    def edit_selected(self):
        """
        Edit the selected entry in the search results.
        """
        row = self.result_table.currentRow()
        if not hasattr(self, 'results') or row < 0 or row >= len(self.results):
            QMessageBox.warning(self, 'Edit Entry', 'Please select an entry to edit.')
            return
        entry = self.results[row]
        dlg = AddEntryDialog(self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        dlg.name_input.setText(entry['name'])
        dlg.phone_input.setText(entry['phone'])
        dlg.answers_input.setText(entry['answers'])
        if dlg.exec_() == QDialog.Accepted and dlg.result_entry:
            # Load entries from file, update the entry, save, and refresh
            if os.path.exists(ENTRIES_FILE):
                with open(ENTRIES_FILE, encoding='utf-8') as f:
                    all_entries = json.load(f)
            else:
                all_entries = []
            for i, e in enumerate(all_entries):
                if e['name'] == entry['name'] and e['phone'] == entry['phone'] and e['answers'] == entry['answers']:
                    all_entries[i] = dlg.result_entry
                    break
            with open(ENTRIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, ensure_ascii=False, indent=2)
            # Update self.entries and results
            self.entries = all_entries
            self.do_search()
            QMessageBox.information(self, 'Edit Entry', 'Entry updated successfully.')

    def delete_selected(self):
        """
        Delete the selected entry in the search results.
        """
        row = self.result_table.currentRow()
        if not hasattr(self, 'results') or row < 0 or row >= len(self.results):
            QMessageBox.warning(self, 'Delete Entry', 'Please select an entry to delete.')
            return
        entry = self.results[row]
        reply = QMessageBox.question(self, 'Delete Entry', f"Are you sure you want to delete entry for {entry['name']}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Load entries from file, remove the entry, save, and refresh
            if os.path.exists(ENTRIES_FILE):
                with open(ENTRIES_FILE, encoding='utf-8') as f:
                    all_entries = json.load(f)
            else:
                all_entries = []
            all_entries = [e for e in all_entries if not (e['name'] == entry['name'] and e['phone'] == entry['phone'] and e['answers'] == entry['answers'])]
            with open(ENTRIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, ensure_ascii=False, indent=2)
            # Update self.entries and results
            self.entries = all_entries
            self.do_search()
            QMessageBox.information(self, 'Delete Entry', 'Entry deleted successfully.')


class MergeEntitiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Merge Entity Files')
        self.setWindowIcon(QIcon('YASA.ico'))
        layout = QVBoxLayout()
        self.file_list = []
        self.select_btn = QPushButton('Select JSON Files')
        self.select_btn.clicked.connect(self.select_files)
        self.merge_btn = QPushButton('Merge and Save')
        self.merge_btn.clicked.connect(self.merge_and_save)
        self.merge_btn.setEnabled(False)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.merge_btn)
        self.setLayout(layout)
        self.setMinimumWidth(400)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select entity JSON files', '', 'JSON Files (*.json)')
        if files:
            self.file_list = files
            self.merge_btn.setEnabled(len(self.file_list) >= 2)

    def merge_and_save(self):
        all_entries = []
        seen = set()
        for file in self.file_list:
            try:
                with open(file, encoding='utf-8') as f:
                    entries = json.load(f)
                    for e in entries:
                        key = (e['name'], e['phone'], e['answers'])
                        if key not in seen:
                            seen.add(key)
                            all_entries.append(e)
            except Exception as ex:
                QMessageBox.warning(self, 'Error', f'Failed to read {file}: {ex}')
                return
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save merged entities', 'merged_entities.json', 'JSON Files (*.json)')
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(all_entries, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, 'Success', f'Merged {len(self.file_list)} files, total {len(all_entries)} unique entries saved.')
                self.accept()
                # --- FINAL FIX: always update ENTRIES_FILE and reload entries in main window ---
                if self.parent() and hasattr(self.parent(), 'set_and_reload_entries_file'):
                    self.parent().set_and_reload_entries_file(save_path)
            except Exception as ex:
                QMessageBox.warning(self, 'Error', f'Failed to save: {ex}')


class KeysEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Keys Editor')
        self.setWindowIcon(QIcon('YASA.ico'))
        self.keys = []
        self.descriptions = []
        self.load_keys()
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            'Q#', 'a (score)', 'a (desc)', 'b (score)', 'b (desc)', 'c (score)', 'c (desc)', 'd (score)', 'd (desc)'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)
        btns = QHBoxLayout()
        self.add_btn = QPushButton('Add Question')
        self.add_btn.clicked.connect(self.add_question)
        self.del_btn = QPushButton('Delete Selected')
        self.del_btn.clicked.connect(self.delete_selected)
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_keys)
        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)
        btns.addWidget(self.save_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.setMinimumWidth(800)
        self.refresh_table()

    def load_keys(self):
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, encoding='utf-8') as f:
                    data = json.load(f)
                    self.keys = data.get('keys', [])
                    self.descriptions = data.get('descriptions', [])
            except Exception:
                self.keys = []
                self.descriptions = []
        else:
            self.keys = []
            self.descriptions = []

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, (k, d) in enumerate(zip(self.keys, self.descriptions)):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(row+1)))
            for idx, key in enumerate(['a','b','c','d']):
                score_item = QTableWidgetItem(str(k.get(key, 0)))
                desc_item = QTableWidgetItem(d.get(key, ''))
                self.table.setItem(row, 1+idx*2, score_item)
                self.table.setItem(row, 2+idx*2, desc_item)

    def add_question(self):
        self.keys.append({'a':0,'b':0,'c':0,'d':0})
        self.descriptions.append({'a':'','b':'','c':'','d':''})
        self.refresh_table()

    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0 and row < len(self.keys):
            del self.keys[row]
            del self.descriptions[row]
            self.refresh_table()

    def save_keys(self):
        # Read from table to self.keys/self.descriptions
        for row in range(self.table.rowCount()):
            k = {}
            d = {}
            for idx, key in enumerate(['a','b','c','d']):
                try:
                    k[key] = int(self.table.item(row, 1+idx*2).text())
                except:
                    k[key] = 0
                d[key] = self.table.item(row, 2+idx*2).text()
            self.keys[row] = k
            self.descriptions[row] = d
        try:
            with open(KEYS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'keys': self.keys, 'descriptions': self.descriptions}, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, 'Saved', 'Keys saved successfully.')
            # --- ABSOLUTE FIX: Always recalculate and update all scores in entries.json after saving keys ---
            def recalc_scores():
                if os.path.exists(ENTRIES_FILE):
                    try:
                        with open(ENTRIES_FILE, encoding='utf-8') as f:
                            entries = json.load(f)
                        n = len(entries)
                        for i, e in enumerate(entries):
                            answers = e.get('answers', '')
                            total = 0
                            for idx, ans in enumerate(answers):
                                if idx < len(self.keys) and ans in self.keys[idx]:
                                    total += self.keys[idx][ans]
                            e['score'] = total
                        with open(ENTRIES_FILE, 'w', encoding='utf-8') as f2:
                            json.dump(entries, f2, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
            # Always update scores in file, then update main window UI if present
            def do_refresh():
                mainwin = self.parent()
                while mainwin and not isinstance(mainwin, QMainWindow):
                    mainwin = mainwin.parent()
                if not mainwin:
                    for widget in QApplication.topLevelWidgets():
                        if isinstance(widget, QMainWindow):
                            mainwin = widget
                            break
                if mainwin and hasattr(mainwin, 'recalculate_all_scores_and_reload_keys'):
                    mainwin.recalculate_all_scores_and_reload_keys()
            # First recalc scores, then refresh main window after a short delay
            recalc_scores()  # Update file immediately
            QTimer.singleShot(200, do_refresh)  # Then refresh main window after file update
            self.accept()
        except Exception as ex:
            QMessageBox.warning(self, 'Error', f'Failed to save: {ex}')


class MainWindow(QMainWindow):
    """
    Main application window. Shows the table of entries and provides access to add/search dialogs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Psychological Talent Identification')
        self.setWindowIcon(QIcon('YASA.ico'))
        # Load keys and descriptions from keys.json
        if not os.path.exists(KEYS_FILE):
            dlg = KeysEditorDialog(self)
            dlg.exec_()
        self.keys, self.descriptions = load_keys()
        # Load all entries from entries.json
        self.entries = load_entries()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        # Add Entry, Edit, Delete, Search, and Remove Duplicates buttons
        add_btn = QPushButton('Add Entry')
        add_btn.clicked.connect(self.open_add_entry)
        edit_btn = QPushButton('Edit Entry')
        edit_btn.clicked.connect(self.open_edit_entry)
        delete_btn = QPushButton('Delete Entry')
        delete_btn.clicked.connect(self.open_delete_entry)
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.open_search)
        dedup_btn = QPushButton('Remove Duplicates')
        dedup_btn.clicked.connect(self.remove_duplicates)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(search_btn)
        btn_layout.addWidget(dedup_btn)
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
        # Footer for last modified date
        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.footer_label)
        self.central.setLayout(layout)
        self.refresh_table()
        self.update_footer()
        self.setMinimumWidth(600)
        # Add menu bar and About action
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        # Add Tools menu for merge and keys editor
        tools_menu = menubar.addMenu('Tools')
        merge_action = QAction('Merge Entity Files', self)
        merge_action.triggered.connect(self.open_merge_entities)
        tools_menu.addAction(merge_action)
        edit_keys_action = QAction('Edit Keys', self)
        edit_keys_action.triggered.connect(self.open_keys_editor)
        tools_menu.addAction(edit_keys_action)
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


    def update_footer(self):
        try:
            mtime = os.path.getmtime(ENTRIES_FILE)
            dt = datetime.fromtimestamp(mtime)
            shamsi = jdatetime.datetime.fromgregorian(datetime=dt)
            total = len(self.entries)
            self.footer_label.setText(
                f"Last modified: {dt.strftime('%Y-%m-%d %H:%M:%S')} (Gregorian) / {shamsi.strftime('%Y-%m-%d %H:%M:%S')} (Shamsi) | Total entries: {total}"
            )
        except Exception:
            self.footer_label.setText('No entries file found.')


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
        self.update_footer()


    def remove_duplicates(self):
        entries = load_entries()
        seen = set()
        unique = []
        for e in entries:
            key = (e['name'], e['phone'], e['answers'])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        if len(unique) < len(entries):
            save_entries(unique)
            self.entries = load_entries()
            self.refresh_table()
            QMessageBox.information(self, 'Remove Duplicates', f"Removed {len(entries) - len(unique)} duplicate entries.")
        else:
            QMessageBox.information(self, 'Remove Duplicates', "No duplicates found.")

    def open_add_entry(self):
        """
        Open the Add Entry dialog and add the new entry if accepted.
        Refresh entries from file after adding.
        """
        dlg = AddEntryDialog(self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        if dlg.exec_() == QDialog.Accepted and dlg.result_entry:
            entries = load_entries()  # Reload from file to get latest
            entries.append(dlg.result_entry)
            save_entries(entries)
            self.entries = load_entries()  # Ensure self.entries is up to date
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
        self.entries = load_entries()  # Always reload before search
        dlg = SearchDialog(self.entries, self.keys, self.descriptions, self)
        dlg.setWindowIcon(QIcon('YASA.ico'))
        dlg.exec_()
        self.entries = load_entries()  # Reload in case of changes
        self.refresh_table()

    def open_merge_entities(self):
        dlg = MergeEntitiesDialog(self)
        dlg.exec_()
        # Always reload entries after dialog closes (in case user merged)
        self.entries = load_entries()
        self.refresh_table()

    def open_keys_editor(self):
        dlg = KeysEditorDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.keys, self.descriptions = load_keys()
            self.entries = load_entries()
            self.refresh_table()
# Entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
