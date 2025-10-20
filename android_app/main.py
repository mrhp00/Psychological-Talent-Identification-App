"""
Psychological Talent Identification - Android App (Kivy)
Professional UI with data snapshot integrity
"""
import os
import json
import copy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.widget import Widget

KEYS_FILE = 'keys.json'
ENTRIES_FILE = 'entries.json'


def get_data_path(filename):
    """Get persistent storage path for data files."""
    app = App.get_running_app()
    if app:
        base = app.user_data_dir
    else:
        base = os.getcwd()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)


def load_keys():
    """Load keys and descriptions from keys.json."""
    path = get_data_path(KEYS_FILE)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'keys': [], 'descriptions': []}, f, ensure_ascii=False, indent=2)
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data.get('keys', []), data.get('descriptions', [])


def save_keys(keys, descriptions):
    """Save keys and descriptions to keys.json."""
    path = get_data_path(KEYS_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'keys': keys, 'descriptions': descriptions}, f, ensure_ascii=False, indent=2)


def load_entries():
    """Load all entries from entries.json."""
    path = get_data_path(ENTRIES_FILE)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_entries(entries):
    """Save entries to entries.json."""
    path = get_data_path(ENTRIES_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def compute_score_from_keys(keys, answers):
    """Compute total score for answers string using provided keys list (snapshot or current)."""
    total = 0
    for idx, ch in enumerate(answers):
        if idx < len(keys) and ch in keys[idx]:
            try:
                total += int(keys[idx][ch])
            except Exception:
                pass
    return total


def migrate_entries_add_snapshots(keys):
    """Add keys_snapshot to entries that lack it. Returns number of entries updated."""
    entries = load_entries()
    updated = 0
    for e in entries:
        if 'keys_snapshot' not in e:
            e['keys_snapshot'] = copy.deepcopy(keys)
            e['score'] = compute_score_from_keys(e['keys_snapshot'], e.get('answers', ''))
            updated += 1
    if updated:
        save_entries(entries)
    return updated


class EntryRow(BoxLayout):
    """Widget representing one entry in the list with edit/delete buttons."""
    def __init__(self, entry, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(5), padding=dp(5), **kwargs)
        self.entry = entry
        
        # Info column with name and details
        info = BoxLayout(orientation='vertical', size_hint_x=0.6)
        info.add_widget(Label(
            text=entry.get('name','Unknown'),
            font_size=dp(16),
            bold=True,
            halign='left',
            valign='middle',
            text_size=(None, None)
        ))
        info.add_widget(Label(
            text=f"Phone: {entry.get('phone','N/A')} | Score: {entry.get('score',0)}",
            font_size=dp(12),
            halign='left',
            valign='middle',
            text_size=(None, None)
        ))
        self.add_widget(info)
        
        # Buttons column
        btns = BoxLayout(size_hint_x=0.4, spacing=dp(5))
        edit = Button(text='Edit', size_hint_x=0.5)
        delete = Button(text='Del', size_hint_x=0.5, background_color=(0.8, 0.2, 0.2, 1))
        edit.bind(on_release=self.on_edit)
        delete.bind(on_release=self.on_delete)
        btns.add_widget(edit)
        btns.add_widget(delete)
        self.add_widget(btns)

    def on_edit(self, *a):
        App.get_running_app().open_add_edit_dialog(self.entry)

    def on_delete(self, *a):
        App.get_running_app().delete_entry(self.entry)


class MainLayout(BoxLayout):
    """Main screen with entry list and action buttons."""
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        
        # Top action bar
        top = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        top.add_widget(Button(
            text='+ Add Entry',
            on_release=lambda *_: App.get_running_app().open_add_edit_dialog(),
            background_color=(0.2, 0.6, 0.2, 1)
        ))
        top.add_widget(Button(
            text='Edit Keys',
            on_release=lambda *_: App.get_running_app().open_keys_editor()
        ))
        top.add_widget(Button(
            text='Migrate',
            on_release=lambda *_: App.get_running_app().migrate_entries()
        ))
        self.add_widget(top)

        # Search bar
        search_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        self.search_input = TextInput(
            hint_text='Search by name or phone...',
            multiline=False,
            size_hint_x=0.8
        )
        self.search_input.bind(text=self.on_search_text)
        search_bar.add_widget(self.search_input)
        search_bar.add_widget(Button(
            text='Clear',
            size_hint_x=0.2,
            on_release=lambda *_: setattr(self.search_input, 'text', '')
        ))
        self.add_widget(search_bar)

        # Scrollable list
        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.add_widget(self.scroll)

        self.refresh()

    def on_search_text(self, instance, value):
        """Filter entries by search text."""
        self.refresh(search_term=value)

    def refresh(self, search_term=''):
        """Reload and display entries, optionally filtered by search term."""
        self.list_layout.clear_widgets()
        entries = load_entries()
        
        # Filter by search term
        if search_term:
            term = search_term.lower()
            entries = [e for e in entries 
                      if term in e.get('name', '').lower() or term in e.get('phone', '')]
        
        # Sort by score descending
        entries.sort(key=lambda e: e.get('score', 0), reverse=True)
        
        if not entries:
            self.list_layout.add_widget(Label(
                text='No entries found. Tap "+ Add Entry" to create one.',
                size_hint_y=None,
                height=dp(100)
            ))
        else:
            for e in entries:
                row = EntryRow(e)
                self.list_layout.add_widget(row)


class PsychoApp(App):
    """Main Kivy application with snapshot data integrity."""
    
    def build(self):
        self.title = 'Psychological Talent Identification'
        self.keys, self.descriptions = load_keys()
        
        # Run migration on first launch
        migrated = migrate_entries_add_snapshots(self.keys)
        if migrated:
            print(f"Migrated {migrated} entries with keys snapshot")
        
        return MainLayout()

    def refresh_ui(self):
        """Refresh the main list."""
        self.root.refresh()

    def open_add_edit_dialog(self, entry=None):
        """Open dialog to add or edit an entry with snapshot support."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        name = TextInput(
            text=entry.get('name','') if entry else '',
            multiline=False,
            hint_text='Name (required)',
            size_hint_y=None,
            height=dp(40)
        )
        phone = TextInput(
            text=entry.get('phone','') if entry else '',
            multiline=False,
            hint_text='Phone',
            size_hint_y=None,
            height=dp(40)
        )
        answers = TextInput(
            text=entry.get('answers','') if entry else '',
            multiline=False,
            hint_text='Answers (e.g., abcdabcd...)',
            size_hint_y=None,
            height=dp(40)
        )
        
        content.add_widget(Label(text='Enter entry details:', size_hint_y=None, height=dp(30)))
        content.add_widget(name)
        content.add_widget(phone)
        content.add_widget(answers)
        
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        ok = Button(text='Save', background_color=(0.2, 0.6, 0.2, 1))
        cancel = Button(text='Cancel')
        btns.add_widget(ok)
        btns.add_widget(cancel)
        content.add_widget(btns)

        popup = Popup(
            title='Edit Entry' if entry else 'Add Entry',
            content=content,
            size_hint=(0.9, 0.6)
        )

        def on_ok(*a):
            n = name.text.strip()
            p = phone.text.strip()
            a_text = answers.text.strip()
            
            if not n:
                self.show_error('Name is required')
                return
            
            # Snapshot current keys with this entry
            keys_snapshot = copy.deepcopy(self.keys)
            score = compute_score_from_keys(keys_snapshot, a_text)
            
            new_entry = {
                'name': n,
                'phone': p,
                'answers': a_text,
                'score': score,
                'keys_snapshot': keys_snapshot
            }
            
            entries = load_entries()
            if entry:
                # Replace matching entry
                for i, e in enumerate(entries):
                    if (e.get('name') == entry.get('name') and 
                        e.get('phone') == entry.get('phone') and 
                        e.get('answers') == entry.get('answers')):
                        entries[i] = new_entry
                        break
            else:
                entries.append(new_entry)
            
            save_entries(entries)
            self.refresh_ui()
            popup.dismiss()

        ok.bind(on_release=on_ok)
        cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def delete_entry(self, entry):
        """Delete an entry after confirmation."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(
            text=f"Delete entry for {entry.get('name', 'Unknown')}?",
            size_hint_y=0.7
        ))
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(10))
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.4))
        
        def do_delete(*a):
            entries = load_entries()
            entries = [e for e in entries if not (
                e.get('name') == entry.get('name') and 
                e.get('phone') == entry.get('phone') and 
                e.get('answers') == entry.get('answers')
            )]
            save_entries(entries)
            self.refresh_ui()
            popup.dismiss()
        
        yes_btn = Button(text='Yes, Delete', background_color=(0.8, 0.2, 0.2, 1))
        yes_btn.bind(on_release=do_delete)
        no_btn = Button(text='Cancel')
        no_btn.bind(on_release=lambda *_: popup.dismiss())
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        popup.open()

    def migrate_entries(self):
        """Manually run migration to add snapshots to entries that lack them."""
        updated = migrate_entries_add_snapshots(self.keys)
        self.show_info(f'Migrated {updated} entries with keys snapshot')
        self.refresh_ui()

    def open_keys_editor(self):
        """Open keys editor with recalculation support (respects snapshots)."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        txt = TextInput(
            text=json.dumps(
                {'keys': self.keys, 'descriptions': self.descriptions},
                ensure_ascii=False,
                indent=2
            ),
            size_hint_y=0.8
        )
        content.add_widget(Label(
            text='Edit keys and descriptions (JSON format):',
            size_hint_y=None,
            height=dp(30)
        ))
        content.add_widget(txt)
        
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        save = Button(text='Save & Recalculate', background_color=(0.2, 0.6, 0.2, 1))
        cancel = Button(text='Cancel')
        btns.add_widget(save)
        btns.add_widget(cancel)
        content.add_widget(btns)
        
        popup = Popup(title='Edit Keys', content=content, size_hint=(0.95, 0.9))

        def on_save(*a):
            try:
                data = json.loads(txt.text)
                k = data.get('keys', [])
                d = data.get('descriptions', [])
                save_keys(k, d)
                self.keys, self.descriptions = k, d
                
                # Recalculate scores using each entry's snapshot (or new keys if no snapshot)
                entries = load_entries()
                for e in entries:
                    ksnap = e.get('keys_snapshot')
                    if ksnap:
                        e['score'] = compute_score_from_keys(ksnap, e.get('answers', ''))
                    else:
                        # Backward compatibility
                        e['score'] = compute_score_from_keys(self.keys, e.get('answers', ''))
                save_entries(entries)
                
                self.refresh_ui()
                popup.dismiss()
                self.show_info('Keys saved and scores recalculated')
            except Exception as ex:
                self.show_error(f'Invalid JSON: {ex}')

        save.bind(on_release=on_save)
        cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def show_error(self, message):
        """Show error popup."""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def show_info(self, message):
        """Show info popup."""
        popup = Popup(
            title='Info',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()


if __name__ == '__main__':
    PsychoApp().run()
