# Standard library imports
import sys
import json
import os
from datetime import datetime
import jdatetime
# PyQt5 imports for GUI components
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView, QMenuBar, QAction, QFileDialog, QSpinBox, QTextEdit, QAbstractItemView, QProgressDialog, QInputDialog
)
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QCheckBox
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
                except Exception:
                    k[key] = 0
                d[key] = self.table.item(row, 2+idx*2).text()
            self.keys[row] = k
            self.descriptions[row] = d

        try:
            with open(KEYS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'keys': self.keys, 'descriptions': self.descriptions}, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, 'Saved', 'Keys saved successfully.')

            # Recalculate scores in entries.json
            def recalc_scores():
                if os.path.exists(ENTRIES_FILE):
                    try:
                        with open(ENTRIES_FILE, encoding='utf-8') as f:
                            entries = json.load(f)
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

            # Refresh main window after a short delay
            def do_refresh():
                mainwin = self.parent()
                while mainwin and not isinstance(mainwin, QMainWindow):
                    mainwin = mainwin.parent()
                if not mainwin:
                    for widget in QApplication.topLevelWidgets():
                        if isinstance(widget, QMainWindow):
                            mainwin = widget
                recalc_scores()
                QTimer.singleShot(200, lambda: None)

            self.accept()
            # schedule UI refresh; main window will reload entries when keys editor closes
            QTimer.singleShot(250, do_refresh)
        except Exception as ex:
            QMessageBox.warning(self, 'Error', f'Failed to save: {ex}')

        # --- Classes dialog and helpers (non-invasive, uses SQLite) ---
class ClassEditDialog(QDialog):
    def __init__(self, parent=None, name='', detail='', days='', start_time='', end_time=''):
        super().__init__(parent)
        self.setWindowTitle('Edit Class')
        layout = QVBoxLayout()
        self.name_input = QLineEdit(name)
        self.detail_input = QLineEdit(detail)
        days_layout = QHBoxLayout()
        self.days_checks = []
        days_of_week = ['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday']
        for d in days_of_week:
            cb = QCheckBox(d)
            if d in days.split(','):
                cb.setChecked(True)
            self.days_checks.append(cb)
            days_layout.addWidget(cb)
        self.start_time_input = QLineEdit(start_time)
        self.end_time_input = QLineEdit(end_time)
        layout.addWidget(QLabel('Name:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel('Detail:'))
        layout.addWidget(self.detail_input)
        layout.addWidget(QLabel('Days of Week:'))
        layout.addLayout(days_layout)
        layout.addWidget(QLabel('Start Time:'))
        layout.addWidget(self.start_time_input)
        layout.addWidget(QLabel('End Time:'))
        layout.addWidget(self.end_time_input)
        btns = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def accept(self):
        self.name = self.name_input.text().strip()
        self.detail = self.detail_input.text().strip()
        self.days = ','.join([cb.text() for cb in self.days_checks if cb.isChecked()])
        self.start_time = self.start_time_input.text().strip()
        self.end_time = self.end_time_input.text().strip()
        if not self.name:
            QMessageBox.warning(self, 'Error', 'Name required')
            return
        super().accept()


class ClassesDialog(QDialog):
    """List/add/edit/delete classes stored in class.sqlite3"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Classes')
        self.setMinimumWidth(600)
        layout = QVBoxLayout()
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(['Name','Detail','Days','Start','End'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.open_class_view)
        layout.addWidget(self.table)
        btns = QHBoxLayout()
        add_btn = QPushButton('Add Class')
        add_btn.clicked.connect(self.add_class)
        edit_btn = QPushButton('Edit Class')
        edit_btn.clicked.connect(self.edit_class)
        del_btn = QPushButton('Delete Class')
        del_btn.clicked.connect(self.delete_class)
        sort_btn = QPushButton('Sort by Name')
        sort_btn.clicked.connect(lambda: self.load_classes(order_by='name'))
        btns.addWidget(add_btn)
        btns.addWidget(edit_btn)
        btns.addWidget(del_btn)
        btns.addWidget(sort_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.db_path = 'class.sqlite3'
        self.load_classes()

    def load_classes(self, order_by='id'):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        q = 'SELECT id,name,detail,days,start_time,end_time FROM classes'
        if order_by=='name':
            q += ' ORDER BY name COLLATE NOCASE'
        c.execute(q)
        rows = c.fetchall()
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            for col, val in enumerate(r[1:]):
                self.table.setItem(i, col, QTableWidgetItem(str(val)))
        conn.close()

    def add_class(self):
        dlg = ClassEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('INSERT INTO classes (name,detail,days,start_time,end_time) VALUES (?,?,?,?,?)',
                      (dlg.name, dlg.detail, dlg.days, dlg.start_time, dlg.end_time))
            conn.commit()
            conn.close()
            self.load_classes()

    def edit_class(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Edit', 'Select a class')
            return
        name = self.table.item(row,0).text()
        detail = self.table.item(row,1).text()
        days = self.table.item(row,2).text()
        start = self.table.item(row,3).text()
        end = self.table.item(row,4).text()
        dlg = ClassEditDialog(self, name, detail, days, start, end)
        if dlg.exec_() == QDialog.Accepted:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('UPDATE classes SET name=?,detail=?,days=?,start_time=?,end_time=? WHERE name=?',
                      (dlg.name, dlg.detail, dlg.days, dlg.start_time, dlg.end_time, name))
            conn.commit()
            conn.close()
            self.load_classes()

    def delete_class(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Delete', 'Select a class')
            return
        name = self.table.item(row,0).text()
        reply = QMessageBox.question(self, 'Delete', f'Delete class {name}?', QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM classes WHERE name=?', (name,))
            conn.commit()
            conn.close()
            self.load_classes()

    def open_class_view(self, row, col):
        # placeholder for part 2: open class-specific view
        cid_item = None
        # try to fetch id by name
        name = self.table.item(row,0).text()
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id FROM classes WHERE name=?', (name,))
        r = c.fetchone()
        conn.close()
        if r:
            cid = r[0]
            dlg = ClassViewDialog(self, class_id=cid)
            dlg.exec_()
        else:
            QMessageBox.information(self, 'Class View', 'Class not found')


class ClassViewDialog(QDialog):
    """Manage students (from entries.json), class dates, attendance (present + score).
    Layout: dates as rows, students as columns. Total row is shown at top for easy access.
    Persists to class.sqlite3 tables created by setup_class_db()."""

    def __init__(self, parent=None, class_id=None):
        super().__init__(parent)
        self.class_id = class_id
        self.db_path = 'class.sqlite3'
        self.setWindowTitle('Class View')
        self.setMinimumWidth(900)

        # Build UI
        main = QVBoxLayout()

        # Top controls
        top = QHBoxLayout()
        self.import_btn = QPushButton('Import Students from entries.json')
        self.delete_student_btn = QPushButton('Delete Student')
        self.add_date_btn = QPushButton('Add Date')
        self.del_date_btn = QPushButton('Delete Selected Date')
        top.addWidget(self.import_btn)
        top.addWidget(self.delete_student_btn)
        top.addWidget(self.add_date_btn)
        top.addWidget(self.del_date_btn)
        top.addStretch()
        main.addLayout(top)

        # Table
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        main.addWidget(self.table)

        # Footer
        footer = QHBoxLayout()
        save_btn = QPushButton('Save')
        close_btn = QPushButton('Close')
        footer.addStretch()
        footer.addWidget(save_btn)
        footer.addWidget(close_btn)
        main.addLayout(footer)

        self.setLayout(main)

        # Connect signals
        self.import_btn.clicked.connect(self.import_students)
        self.delete_student_btn.clicked.connect(self.delete_student)
        self.add_date_btn.clicked.connect(self.add_date)
        self.del_date_btn.clicked.connect(self.delete_date)
        save_btn.clicked.connect(self.save_all)
        close_btn.clicked.connect(self.accept)

        # Add timer UI after layout exists
        self._timer_added = False
        self.add_timer_ui()

        # Load data
        self.load_students()
        self.load_dates()
        self.build_table()

    def connect_db(self):
        import sqlite3
        return sqlite3.connect(self.db_path)

    def load_students(self):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT id,name,phone,answers FROM class_students WHERE class_id=?', (self.class_id,))
        rows = c.fetchall()
        conn.close()
        self.students = [{'id': r[0], 'name': r[1], 'phone': r[2], 'answers': r[3]} for r in rows]

    def load_dates(self):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT id,date FROM class_dates WHERE class_id=? ORDER BY id', (self.class_id,))
        rows = c.fetchall()
        conn.close()
        self.dates = [{'id': r[0], 'date': r[1]} for r in rows]

    def build_table(self):
        cols = len(self.students)
        rows = len(self.dates) + 1
        if cols == 0:
            self.table.setColumnCount(1)
            self.table.setRowCount(1)
            self.table.setHorizontalHeaderLabels(['No students'])
            self.table.setItem(0, 0, QTableWidgetItem('No students. Use Import Students.'))
            return

        self.table.clear()
        self.table.setColumnCount(cols)
        self.table.setRowCount(rows)
        headers = [s['name'] for s in self.students]
        self.table.setHorizontalHeaderLabels(headers)

        # Total row
        for c_idx, student in enumerate(self.students):
            total = self.calculate_student_total(student['id'])
            item = QTableWidgetItem(str(total))
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(0, c_idx, item)

        # Dates rows
        for r_idx, date in enumerate(self.dates, start=1):
            for c_idx, student in enumerate(self.students):
                widget = QWidget()
                layout = QHBoxLayout()
                cb = QCheckBox()
                score_edit = QLineEdit()
                score_edit.setFixedWidth(60)
                att = self.load_attendance(date['id'], student['id'])
                cb.setChecked(bool(att and att.get('present')))
                score_edit.setText(str(att.get('score')) if att and att.get('score') is not None else '')
                layout.addWidget(cb)
                layout.addWidget(score_edit)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                self.table.setCellWidget(r_idx, c_idx, widget)

        vlabels = ['Total'] + [d['date'] for d in self.dates]
        self.table.setVerticalHeaderLabels(vlabels)
        self.table.resizeColumnsToContents()

    def import_students(self):
        dlg = StudentPickerDialog(self)
        if dlg.exec_() != QDialog.Accepted or not hasattr(dlg, 'selected'):
            return
        to_add = dlg.selected
        conn = self.connect_db()
        c = conn.cursor()
        inserted = 0
        for e in to_add:
            name = e.get('name')
            phone = e.get('phone')
            answers = e.get('answers', '')
            c.execute('SELECT id FROM class_students WHERE class_id=? AND name=? AND phone=?', (self.class_id, name, phone))
            if c.fetchone():
                continue
            c.execute('INSERT INTO class_students (class_id,name,phone,answers) VALUES (?,?,?,?)', (self.class_id, name, phone, answers))
            inserted += 1
        conn.commit()
        conn.close()
        self.load_students()
        self.build_table()
        QMessageBox.information(self, 'Import Students', f'Added {inserted} students.')

    def add_timer_ui(self):
        if getattr(self, '_timer_added', False):
            return
        toolbar = QHBoxLayout()
        self.timer_label = QLabel('Timer: 00:00')
        self.timer_duration = QLineEdit()
        self.timer_duration.setPlaceholderText('Seconds (e.g. 300)')
        self.timer_start = QPushButton('Start')
        self.timer_pause = QPushButton('Pause')
        self.timer_reset = QPushButton('Reset')
        toolbar.addWidget(self.timer_label)
        toolbar.addWidget(QLabel('Duration:'))
        toolbar.addWidget(self.timer_duration)
        toolbar.addWidget(self.timer_start)
        toolbar.addWidget(self.timer_pause)
        toolbar.addWidget(self.timer_reset)
        toolbar.addStretch()
        # Insert at top of layout
        lay = self.layout()
        if lay is not None:
            lay.insertLayout(0, toolbar)
        self._timer_seconds = 0
        self._timer_running = False
        self._timer_target = None
        self._qtimer = QTimer(self)
        self._qtimer.setInterval(1000)
        self._qtimer.timeout.connect(self._timer_tick)
        self.timer_start.clicked.connect(self._timer_start)
        self.timer_pause.clicked.connect(self._timer_pause)
        self.timer_reset.clicked.connect(self._timer_reset)
        self._timer_added = True

    def _timer_tick(self):
        if not self._timer_running:
            return
        if self._timer_target is not None:
            self._timer_seconds -= 1
            secs = max(0, self._timer_seconds)
            m, s = divmod(secs, 60)
            self.timer_label.setText(f'Time left: {m:02d}:{s:02d}')
            if secs <= 0:
                self._timer_running = False
                self._qtimer.stop()
                try:
                    QApplication.beep()
                except Exception:
                    pass
                QMessageBox.information(self, 'Timer', 'Time is up!')
                self._timer_target = None
        else:
            self._timer_seconds += 1
            m, s = divmod(self._timer_seconds, 60)
            self.timer_label.setText(f'Timer: {m:02d}:{s:02d}')

    def _timer_start(self):
        if not getattr(self, '_timer_added', False):
            self.add_timer_ui()
        dur_text = self.timer_duration.text().strip()
        if dur_text:
            try:
                secs = int(dur_text)
                self._timer_seconds = secs
                self._timer_target = secs
            except Exception:
                self._timer_target = None
        else:
            self._timer_target = None
        self._timer_running = True
        self._qtimer.start()

    def _timer_pause(self):
        self._timer_running = False
        self._qtimer.stop()

    def _timer_reset(self):
        self._timer_running = False
        self._qtimer.stop()
        self._timer_target = None
        self._timer_seconds = 0
        if hasattr(self, 'timer_label'):
            self.timer_label.setText('Timer: 00:00')

    def delete_student(self):
        col = self.table.currentColumn()
        if col < 0 or col >= len(self.students):
            QMessageBox.warning(self, 'Delete Student', 'Select a student column to delete')
            return
        student = self.students[col]
        reply = QMessageBox.question(self, 'Delete Student', f'Remove {student["name"]} from class? This will delete attendance records.', QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('DELETE FROM class_students WHERE id=?', (student['id'],))
        c.execute('DELETE FROM attendance WHERE student_id=? AND class_id=?', (student['id'], self.class_id))
        conn.commit()
        conn.close()
        self.load_students()
        self.build_table()

    def add_date(self):
        text, ok = QInputDialog.getText(self, 'Add Date', 'Enter date (YYYY-MM-DD):')
        if not ok or not text:
            return
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('INSERT INTO class_dates (class_id,date) VALUES (?,?)', (self.class_id, text))
        conn.commit()
        conn.close()
        self.load_dates()
        self.build_table()

    def delete_date(self):
        row = self.table.currentRow()
        if row <= 0 or row > len(self.dates):
            QMessageBox.warning(self, 'Delete Date', 'Select a date row to delete')
            return
        date = self.dates[row - 1]
        reply = QMessageBox.question(self, 'Delete Date', f'Delete date {date["date"]}?', QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('DELETE FROM class_dates WHERE id=?', (date['id'],))
        c.execute('DELETE FROM attendance WHERE date_id=?', (date['id'],))
        conn.commit()
        conn.close()
        self.load_dates()
        self.build_table()

    def load_attendance(self, date_id, student_id):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT present,score FROM attendance WHERE date_id=? AND student_id=?', (date_id, student_id))
        r = c.fetchone()
        conn.close()
        if r:
            return {'present': r[0], 'score': r[1]}
        return None

    def save_all(self):
        if len(self.students) == 0:
            QMessageBox.information(self, 'Save', 'No students to save')
            return
        conn = self.connect_db()
        c = conn.cursor()
        for r_idx, date in enumerate(self.dates, start=1):
            for c_idx, student in enumerate(self.students):
                widget = self.table.cellWidget(r_idx, c_idx)
                if not widget:
                    continue
                cb = widget.layout().itemAt(0).widget()
                score_edit = widget.layout().itemAt(1).widget()
                present = 1 if cb.isChecked() else 0
                score_text = score_edit.text().strip()
                score_val = score_text if score_text != '' else None
                c.execute('SELECT id FROM attendance WHERE date_id=? AND student_id=?', (date['id'], student['id']))
                if c.fetchone():
                    c.execute('UPDATE attendance SET present=?, score=? WHERE date_id=? AND student_id=?', (present, score_val, date['id'], student['id']))
                else:
                    c.execute('INSERT INTO attendance (class_id,date_id,student_id,present,score) VALUES (?,?,?,?,?)', (self.class_id, date['id'], student['id'], present, score_val))
        conn.commit()
        conn.close()
        self.build_table()
        QMessageBox.information(self, 'Saved', 'Attendance saved.')

    def calculate_student_total(self, student_id):
        conn = self.connect_db()
        c = conn.cursor()
        c.execute('SELECT score FROM attendance WHERE student_id=? AND class_id=?', (student_id, self.class_id))
        rows = c.fetchall()
        conn.close()
        total = 0
        for r in rows:
            try:
                val = float(r[0]) if r[0] is not None and r[0] != '' else 0
            except Exception:
                val = 0
            total += val
        return total


class StudentPickerDialog(QDialog):
    """Searchable dialog to pick students from entries.json to add to a class."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Students')
        self.resize(480, 400)
        self._entries = load_entries()
        self.selected = []

        v = QVBoxLayout()
        h = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search by name or phone...')
        self.find_btn = QPushButton('Find')
        h.addWidget(self.search)
        h.addWidget(self.find_btn)
        v.addLayout(h)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_widget.setLayout(self.list_layout)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.list_widget)
        v.addWidget(self.scroll)

        btns = QHBoxLayout()
        self.add_btn = QPushButton('Add Selected')
        self.cancel_btn = QPushButton('Cancel')
        btns.addStretch()
        btns.addWidget(self.add_btn)
        btns.addWidget(self.cancel_btn)
        v.addLayout(btns)

        self.setLayout(v)

        self._checkboxes = []
        self.find_btn.clicked.connect(self._do_search)
        self.search.returnPressed.connect(self._do_search)
        self.add_btn.clicked.connect(self._add_selected)
        self.cancel_btn.clicked.connect(self.reject)

        # initial populate
        self._do_search()

    def _do_search(self):
        term = self.search.text().strip().lower()
        # clear
        for i in reversed(range(self.list_layout.count())):
            item = self.list_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
        self._checkboxes = []
        for e in self._entries:
            name = e.get('name','')
            phone = e.get('phone','')
            text = f"{name} | {phone}"
            if term and term not in text.lower():
                continue
            row = QHBoxLayout()
            cb = QCheckBox(text)
            row.addWidget(cb)
            widget = QWidget()
            widget.setLayout(row)
            self.list_layout.addWidget(widget)
            self._checkboxes.append((cb, e))

    def _add_selected(self):
        selected = []
        for cb, e in self._checkboxes:
            if cb.isChecked():
                selected.append(e)
        if not selected:
            QMessageBox.information(self, 'No Selection', 'Please select at least one student to add')
            return
        self.selected = selected
        self.accept()

    


class AddEntryDialog(QDialog):
    """Minimal Add/Edit entry dialog used by MainWindow."""
    def __init__(self, keys, descriptions, parent=None):
        super().__init__(parent)
        self.keys = keys
        self.descriptions = descriptions
        self.result_entry = None
        self.setWindowTitle('Add / Edit Entry')
        layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.answers_input = QLineEdit()
        layout.addWidget(QLabel('Name:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel('Phone:'))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel('Answers (e.g. abcd...):'))
        layout.addWidget(self.answers_input)
        btns = QHBoxLayout()
        ok = QPushButton('OK')
        cancel = QPushButton('Cancel')
        ok.clicked.connect(self.on_ok)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

    def on_ok(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        answers = self.answers_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Name required')
            return
        score = 0
        for idx, ch in enumerate(answers):
            if idx < len(self.keys) and ch in self.keys[idx]:
                try:
                    score += int(self.keys[idx][ch])
                except Exception:
                    pass
        self.result_entry = {'name': name, 'phone': phone, 'answers': answers, 'score': score}
        self.accept()


class SearchDialog(QDialog):
    """Minimal search dialog for entries. Allows viewing results."""
    def __init__(self, entries, keys, descriptions, parent=None):
        super().__init__(parent)
        self.entries = entries
        self.keys = keys
        self.descriptions = descriptions
        self.setWindowTitle('Search Entries')
        self.resize(600, 400)
        v = QVBoxLayout()
        h = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search by name or phone')
        self.find_btn = QPushButton('Find')
        h.addWidget(self.search)
        h.addWidget(self.find_btn)
        v.addLayout(h)
        self.table = QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels(['Name','Phone','Score'])
        v.addWidget(self.table)
        btns = QHBoxLayout()
        close = QPushButton('Close')
        close.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(close)
        v.addLayout(btns)
        self.setLayout(v)
        self.find_btn.clicked.connect(self.do_search)
        self.search.returnPressed.connect(self.do_search)
        self.do_search()

    def do_search(self):
        term = self.search.text().strip().lower()
        self.table.setRowCount(0)
        for e in self.entries:
            if term and term not in (e.get('name','').lower() + ' ' + e.get('phone','')):
                continue
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r,0, QTableWidgetItem(e.get('name','')))
            self.table.setItem(r,1, QTableWidgetItem(e.get('phone','')))
            self.table.setItem(r,2, QTableWidgetItem(str(e.get('score',''))))


class MainWindow(QMainWindow):
    """
    Main application window. Shows the table of entries and provides access to add/search dialogs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Psychological Talent Identification')
        self.setWindowIcon(QIcon('YASA.ico'))

        # Ensure keys exist; if not, open editor once
        if not os.path.exists(KEYS_FILE):
            dlg = KeysEditorDialog(self)
            dlg.exec_()
        self.keys, self.descriptions = load_keys()

        # Load entries
        self.entries = load_entries()

        # Central widget and layout
        self.central = QWidget()
        self.setCentralWidget(self.central)
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        # Top buttons
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

        # Table
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

        # Footer
        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.footer_label)

        self.central.setLayout(layout)
        self.refresh_table()
        self.update_footer()
        self.setMinimumWidth(600)

        # Menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        merge_action = QAction('Merge Entity Files', self)
        merge_action.triggered.connect(self.open_merge_entities)
        tools_menu.addAction(merge_action)
        edit_keys_action = QAction('Edit Keys', self)
        edit_keys_action.triggered.connect(self.open_keys_editor)
        tools_menu.addAction(edit_keys_action)

        # Class Management menu (non-invasive addition)
        class_menu = menubar.addMenu('Class Management')
        classes_action = QAction('Classes', self)
        classes_action.triggered.connect(self.open_class_management)
        class_menu.addAction(classes_action)

        self.sort_column = 0
        self.sort_order = Qt.AscendingOrder

    # Class Management menu is added in __init__ to avoid module-scope references


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
    # --- Class management DB helper ---
    def setup_class_db(self):
        import sqlite3
        db_path = 'class.sqlite3'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # classes table: id, name, detail, days (csv), start_time, end_time
        c.execute('''CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            detail TEXT,
            days TEXT,
            start_time TEXT,
            end_time TEXT
        )''')
        # class_students: id, class_id, entry_name, entry_phone, entry_answers
        c.execute('''CREATE TABLE IF NOT EXISTS class_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            answers TEXT
        )''')
        # class_dates: id, class_id, date TEXT
        c.execute('''CREATE TABLE IF NOT EXISTS class_dates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            date TEXT
        )''')
        # attendance: id, class_id, date_id, student_id, present INTEGER, score TEXT
        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            date_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            present INTEGER DEFAULT 0,
            score TEXT
        )''')
        conn.commit()
        conn.close()

    def open_class_management(self):
        # Ensure DB exists
        try:
            self.setup_class_db()
        except Exception:
            pass
        dlg = ClassesDialog(self)
        dlg.exec_()
# Entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
