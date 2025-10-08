import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp

KEYS_FILE = 'keys.json'
ENTRIES_FILE = 'entries.json'


def get_data_path(filename):
    # Use user_data_dir so files persist on device and are writable
    app = App.get_running_app()
    if app:
        base = app.user_data_dir
    else:
        base = os.getcwd()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)


def load_keys():
    path = get_data_path(KEYS_FILE)
    if not os.path.exists(path):
        # create empty keys structure
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'keys': [], 'descriptions': []}, f, ensure_ascii=False, indent=2)
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data.get('keys', []), data.get('descriptions', [])


def save_keys(keys, descriptions):
    path = get_data_path(KEYS_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'keys': keys, 'descriptions': descriptions}, f, ensure_ascii=False, indent=2)


def load_entries():
    path = get_data_path(ENTRIES_FILE)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_entries(entries):
    path = get_data_path(ENTRIES_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def calculate_score_for_answers(keys, answers):
    total = 0
    for idx, ch in enumerate(answers):
        if idx < len(keys) and ch in keys[idx]:
            try:
                total += int(keys[idx][ch])
            except Exception:
                pass
    return total


class EntryRow(BoxLayout):
    def __init__(self, entry, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(40), **kwargs)
        self.entry = entry
        self.add_widget(Label(text=entry.get('name',''), size_hint_x=0.4))
        self.add_widget(Label(text=entry.get('phone',''), size_hint_x=0.3))
        self.add_widget(Label(text=str(entry.get('score','')), size_hint_x=0.2))
        btns = BoxLayout(size_hint_x=0.1)
        edit = Button(text='Edit', size_hint_x=0.5)
        delete = Button(text='Del', size_hint_x=0.5)
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
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(8), spacing=dp(8), **kwargs)
        top = BoxLayout(size_hint_y=None, height=dp(40))
        top.add_widget(Button(text='Add Entry', on_release=lambda *_: App.get_running_app().open_add_edit_dialog()))
        top.add_widget(Button(text='Edit Keys', on_release=lambda *_: App.get_running_app().open_keys_editor()))
        top.add_widget(Button(text='Remove Dups', on_release=lambda *_: App.get_running_app().remove_duplicates()))
        self.add_widget(top)

        # header
        header = BoxLayout(size_hint_y=None, height=dp(30))
        header.add_widget(Label(text='Name', size_hint_x=0.4))
        header.add_widget(Label(text='Phone', size_hint_x=0.3))
        header.add_widget(Label(text='Score', size_hint_x=0.2))
        header.add_widget(Label(text='', size_hint_x=0.1))
        self.add_widget(header)

        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.add_widget(self.scroll)

        self.refresh()

    def refresh(self):
        self.list_layout.clear_widgets()
        entries = load_entries()
        for e in entries:
            row = EntryRow(e)
            self.list_layout.add_widget(row)


class SimpleApp(App):
    def build(self):
        self.title = 'Psychological Talent Identification'
        self.keys, self.descriptions = load_keys()
        return MainLayout()

    def refresh_ui(self):
        self.root.refresh()

    def open_add_edit_dialog(self, entry=None):
        keys = self.keys

        content = BoxLayout(orientation='vertical', spacing=dp(8))
        name = TextInput(text=entry.get('name','') if entry else '', multiline=False, hint_text='Name')
        phone = TextInput(text=entry.get('phone','') if entry else '', multiline=False, hint_text='Phone')
        answers = TextInput(text=entry.get('answers','') if entry else '', multiline=False, hint_text='Answers e.g. abcd')
        content.add_widget(name)
        content.add_widget(phone)
        content.add_widget(answers)
        btns = BoxLayout(size_hint_y=None, height=dp(40))
        ok = Button(text='OK')
        cancel = Button(text='Cancel')
        btns.add_widget(ok)
        btns.add_widget(cancel)
        content.add_widget(btns)

        popup = Popup(title='Add / Edit Entry', content=content, size_hint=(0.9, 0.5))

        def on_ok(*a):
            n = name.text.strip()
            p = phone.text.strip()
            a_text = answers.text.strip()
            if not n:
                return
            entries = load_entries()
            new_entry = {'name': n, 'phone': p, 'answers': a_text}
            new_entry['score'] = calculate_score_for_answers(keys, a_text)
            if entry:
                # replace matching entry by name+phone+answers
                for i, e in enumerate(entries):
                    if e['name'] == entry.get('name') and e['phone'] == entry.get('phone') and e['answers'] == entry.get('answers'):
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
        entries = load_entries()
        entries = [e for e in entries if not (e['name'] == entry['name'] and e['phone'] == entry['phone'] and e['answers'] == entry['answers'])]
        save_entries(entries)
        self.refresh_ui()

    def remove_duplicates(self):
        entries = load_entries()
        seen = set()
        unique = []
        for e in entries:
            key = (e.get('name'), e.get('phone'), e.get('answers'))
            if key not in seen:
                seen.add(key)
                unique.append(e)
        if len(unique) < len(entries):
            save_entries(unique)
            self.refresh_ui()

    def open_keys_editor(self):
        # simple keys editor: JSON editor for keys/descriptions
        keys, descs = self.keys, self.descriptions
        content = BoxLayout(orientation='vertical', spacing=dp(8))
        txt = TextInput(text=json.dumps({'keys': keys, 'descriptions': descs}, ensure_ascii=False, indent=2), size_hint_y=0.8)
        content.add_widget(txt)
        btns = BoxLayout(size_hint_y=None, height=dp(40))
        save = Button(text='Save')
        cancel = Button(text='Cancel')
        btns.add_widget(save)
        btns.add_widget(cancel)
        content.add_widget(btns)
        popup = Popup(title='Edit Keys (JSON)', content=content, size_hint=(0.95, 0.9))

        def on_save(*a):
            try:
                data = json.loads(txt.text)
                k = data.get('keys', [])
                d = data.get('descriptions', [])
                save_keys(k, d)
                self.keys, self.descriptions = k, d
                popup.dismiss()
            except Exception:
                pass

        save.bind(on_release=on_save)
        cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()


if __name__ == '__main__':
    SimpleApp().run()
