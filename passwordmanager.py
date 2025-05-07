import ttkbootstrap as ttk
import string
import re
import base64
import random
from PIL import Image, ImageTk
from tkinter.messagebox import askyesno
from collections import Counter
from io import BytesIO
import json
import csv
import pyperclip
import os
from encoded_image import ENCODED_IMAGE
import os
import json
import base64
import shutil
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import tempfile

def _get_chrome_passwords():
    """Internal method"""
    def get_master_key(local_state_path):
        with open(local_state_path, "r", encoding="utf-8") as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # remove DPAPI prefix
        master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return master_key

    def decrypt_password(buff, key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted = cipher.decrypt(payload)[:-16].decode()
            return decrypted
        except Exception:
            try:
                return str(win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1])
            except Exception:
                return ""

    results = []
    chrome_path = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data")
    local_state_path = os.path.join(chrome_path, "Local State")
    login_db_path = os.path.join(chrome_path, r"Default\Login Data")

    if not os.path.exists(local_state_path) or not os.path.exists(login_db_path):
        print("Chrome profile not found.")
        return []

    master_key = get_master_key(local_state_path)

    # Copy DB to avoid lock issues
    temp_dir = tempfile.gettempdir()
    temp_db = os.path.join(temp_dir, "LoginDataTemp.db")
    shutil.copy2(login_db_path, temp_db)

    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        for row in cursor.fetchall():
            url, username, encrypted_password = row
            if not username or not encrypted_password:
                continue
            password = decrypt_password(encrypted_password, master_key)
            results.append({
                "url": url,
                "username": username,
                "password": password
            })

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error reading Chrome DB:", e)
    finally:
        os.remove(temp_db)

    return results


def _invalid(root, widget, og_style):
    widget.config(bootstyle='dark')
    root.after(1000, lambda: widget.config(bootstyle=og_style))

def valid(root, widget, message, time, og_style, og_text):
    widget.config(bootstyle='success', text=message)
    root.after(time, lambda: widget.config(bootstyle=og_style, text=og_text))


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f'{w-15}x{h-100}+0+0')
        self.root.iconbitmap("passwordmanagerlogo.png")

        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # --- VARS ---

        self.passwords = {}

        for F in (HomePage, CreatePassword, ManagePasswords):
            page = F(parent=container, controller=self)
            self.frames[F] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)


    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Title style
        titlestyle = ttk.Style()
        titlestyle.configure(
            'title.TLabel',
            font=('Bahnschrift', 54, 'bold'),
            foreground='#4472C4',
        )

        buttonstyle = ttk.Style()
        buttonstyle.configure(
            'bluebutton.TButton',
            font=('Bahnschrift SemiBold', 18),
            background='#4472C4',
            foreground='white'
        )

        # Decode base64 image
        image_data = base64.b64decode(ENCODED_IMAGE)
        pil_image = Image.open(BytesIO(image_data)).resize((125, 125))
        tk_image = ImageTk.PhotoImage(pil_image)

        # Title and Logo
        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="w")

        logo = ttk.Label(title_frame, image=tk_image)
        logo.image = tk_image  # prevent GC
        logo.grid(row=0, column=0)

        titletext = ttk.Label(title_frame, text='Password Manager', style='title.TLabel')
        titletext.grid(row=0, column=1, padx=10)

        # Buttons
        button_container = ttk.Frame(self)
        button_container.grid(row=1, column=0, padx=20, sticky="nsew")

        genpass_btn = ttk.Button(button_container, text=' Generate Strong Password ',
                                 style='bluebutton.TButton', command=lambda: controller.show_frame(CreatePassword))
        genpass_btn.grid(row=0, column=0, padx=10, pady=10)

        managepass_btn = ttk.Button(button_container, text=' Manage Passwords ', style='bluebutton.TButton',
                                    command=lambda: controller.show_frame(ManagePasswords))
        managepass_btn.grid(row=0, column=1, padx=10, pady=10)

        viewpass_btn = ttk.Button(button_container, text=' View Your Passwords ', style='bluebutton.TButton')
        viewpass_btn.grid(row=0, column=2, padx=10, pady=10)

class CreatePassword(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padding=30)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        title_label = ttk.Label(
            self,
            text="Strengthen Your Password",
            font=('Bahnschrift Light', 30),
            padding=20
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # --- Input Field ---
        self.entry = ttk.Entry(
            self,
            font=('Bahnschrift Light', 24),
            width=30,
            justify='center'
        )
        self.entry.grid(row=1, column=0, columnspan=3, pady=10)

        # --- Options ---
        options_frame = ttk.LabelFrame(self, text="Options", padding=20)
        options_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.length = ttk.IntVar(value=12)
        ttk.Label(options_frame, text="Length:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        length_spinbox = ttk.Spinbox(options_frame, from_=6, to=64, textvariable=self.length, width=5)
        length_spinbox.grid(row=0, column=1, padx=(0, 20))

        self.use_letters = ttk.BooleanVar(value=True)
        self.use_nums = ttk.BooleanVar(value=True)
        self.use_symbols = ttk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Letters", variable=self.use_letters).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(options_frame, text="Numbers", variable=self.use_nums).grid(row=0, column=3, padx=5)
        ttk.Checkbutton(options_frame, text="Symbols", variable=self.use_symbols).grid(row=0, column=4, padx=5)


        # --- Buttons ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        generate_btn = ttk.Button(
            button_frame,
            text="🎲 Generate",
            style='bluebutton.TButton',
            command=self.generate
        )
        generate_btn.pack(side='left', padx=10)

        strengthen_btn = ttk.Button(
            button_frame,
            text="💪 Strengthen",
            style='bluebutton.TButton',
            command=self.strengthen_password
        )
        strengthen_btn.pack(side='left', padx=10)

        self.copy_btn = ttk.Button(
            button_frame,
            text="📋 Copy",
            style='bluebutton.TButton',
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side='left', padx=10)

        back_btn = ttk.Button(
            button_frame,
            text="← Back",
            style='bluebutton.TButton',
            command=lambda: controller.show_frame(HomePage)
        )
        back_btn.pack(side='left', padx=10)

    def generate_pass(self, length, symbols=True, letters=True, nums=True):
        chars = ''
        if letters:
            chars += string.ascii_letters
        if nums:
            chars += string.digits
        if symbols:
            chars += string.punctuation

        if not chars:
            return "⚠️ Enable at least one type!"

        password = ''.join(random.choices(chars, k=length))
        return password

    def strengthen_password(self):
        base = self.entry.get()
        if not base:
            return

        chars = ''
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_nums.get():
            chars += string.digits
        if self.use_symbols.get():
            chars += string.punctuation

        if not chars:
            self.entry.delete(0, 'end')
            self.entry.insert(0, "Select at least one option!")
            return

        # Mix the original password with random characters to "strengthen" it
        target_length = self.length.get()
        extra_needed = max(0, target_length - len(base))
        extra_chars = ''.join(random.choices(chars, k=extra_needed))

        # Shuffle original + new characters
        combined = list(base + extra_chars)
        random.shuffle(combined)
        strengthened = ''.join(combined[:target_length])

        self.entry.delete(0, 'end')
        self.entry.insert(0, strengthened)

    def generate(self):
        length = int(self.length.get())

        if not (self.use_letters.get() or self.use_nums.get() or self.use_symbols.get()):
            self.entry.delete(0, 'end')
            self.entry.insert(0, "⚠️ Enable at least one type!")
            return

        password = self.generate_pass(
            length,
            symbols=self.use_symbols.get(),
            letters=self.use_letters.get(),
            nums=self.use_nums.get()
        )
        self.entry.delete(0, 'end')
        self.entry.insert(0, password)
        self.copy_btn.config(text="📋 Copy")

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.entry.get())
        self.copy_btn.config(text="✅ Copied!")
        self.update()

class ManagePasswords(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Treeview expands
        self.grid_columnconfigure(1, weight=0)  # Right-side controls

        # --- Treeview (left side) ---
        self.view = ttk.Treeview(self, columns=('Name', 'Email or User', 'Pass'), show="headings")
        self.view.heading("Name", text="Site Name")
        self.view.heading("Email or User", text="Email or Username")
        self.view.heading("Pass", text="Password")
        self.view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Right-side vertical container ---
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        # --- Add Frame ---
        add_frame = ttk.LabelFrame(right_frame, text='Add')
        add_frame.grid(row=0, column=0)

        ttk.Label(add_frame, text="Site:").grid(row=0, column=0, sticky="w")
        self.add_site = ttk.Entry(add_frame, width=25)
        self.add_site.grid(row=1, column=0, pady=(0, 10), sticky="w")
        self.add_site.insert(0, 'https://example.com/')

        ttk.Label(add_frame, text="Email or Username:").grid(row=2, column=0, sticky="w")
        self.add_email = ttk.Entry(add_frame, width=25)
        self.add_email.grid(row=3, column=0, pady=(0, 10), sticky="w")
        self.add_email.insert(0, 'exampleemail@gmail.com')


        ttk.Label(add_frame, text="Password:").grid(row=6, column=0, sticky="w")
        self.add_pass = ttk.Entry(add_frame, width=25)
        self.add_pass.grid(row=7, column=0, sticky="w")
        self.add_pass.insert(0, 'ExamplePassword')

        self.add_to_field = ttk.Button(add_frame, text='Add To Passwords', padding=10,
                                  command=self.add_field, bootstyle='success')
        self.add_to_field.grid(row=8, column=0, pady=10)

        # --- Remove Frame ---
        del_frame = ttk.LabelFrame(right_frame, text='Remove')
        del_frame.grid(row=1, column=0)

        self.delete_btn = ttk.Button(del_frame, text="Remove Selected", width=24,
                                command=self.delete_field, bootstyle='danger')
        self.delete_btn.grid(row=0, column=0, pady=10)

        self.delete_all_btn = ttk.Button(del_frame, text="Remove All", width=24,
                                    command=self.delete_all_fields, bootstyle='danger')
        self.delete_all_btn.grid(row=1, column=0, pady=10)

        tools_frame = ttk.LabelFrame(right_frame, text='Tools')
        tools_frame.grid(row=2, column=0)

        self.get_passwords_btn = ttk.Button(tools_frame, text="Get passwords from chrome", width=24,
                                             command=self.get_passwords, bootstyle='info')
        self.get_passwords_btn.grid(row=0, column=0, pady=10)

        self.check_security_btn = ttk.Button(tools_frame, text="Check Password Security", width=24,
                                        command=self.check_security_password, bootstyle='primary')
        self.check_security_btn.grid(row=1, column=0, pady=10)

        self.check_security_btn_freq = ttk.Button(tools_frame, text="Check Password Frequency", width=24,
                                        command=self.check_password_frequency, bootstyle='primary')
        self.check_security_btn_freq.grid(row=2, column=0, pady=10)

        self.copy_btn = ttk.Button(tools_frame, text="Copy Selected Password", width=24, command=self.copy_password,
                                   bootstyle='primary')
        self.copy_btn.grid(row=3, column=0, pady=10)

        self.save_btn = ttk.Button(tools_frame, text="Save", width=24, command=self.save_passwords,
                                   bootstyle='secondary')
        self.save_btn.grid(row=4, column=0, pady=10)

        self.load_btn = ttk.Button(tools_frame, text="Load", width=24, command=self.load_passwords,
                                   bootstyle='secondary')
        self.load_btn.grid(row=5, column=0, pady=10)

        self.export_btn = ttk.Button(tools_frame, text="Export to CSV", width=24, command=self.export_to_csv,
                                     bootstyle='secondary')
        self.export_btn.grid(row=6, column=0, pady=10)

        right_frame2 = ttk.Frame(self)
        right_frame2.grid(row=0, column=2, sticky="n", padx=10, pady=10)

        edit_frame = ttk.LabelFrame(right_frame2, text='Search and edit')
        edit_frame.grid(row=3, column=0)

        ttk.Label(edit_frame, text="Search Site or Password:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(edit_frame, width=25)
        self.search_entry.grid(row=1, column=0, pady=(0, 10), sticky="w")
        self.search_entry.insert(0, 'https://example.com/')

        self.search_btn = ttk.Button(edit_frame, text="Search", width=24,
                                        command=self.search_treeview, bootstyle='warning')
        self.search_btn.grid(row=2, column=0, pady=10)

        ttk.Label(edit_frame, text="Edit Selected To Site or Password:").grid(row=3, column=0, sticky="w")
        self.edit_entry = ttk.Entry(edit_frame, width=25)
        self.edit_entry.grid(row=4, column=0, pady=(0, 10), sticky="w")
        self.edit_entry.insert(0, 'https://example.com/')

        self.edit_site_btn = ttk.Button(edit_frame, text="Edit site name", width=24,
                                command=self.edit_sitename, bootstyle='warning')
        self.edit_site_btn.grid(row=5, column=0, pady=10)

        self.edit_pass_btn = ttk.Button(edit_frame, text="Edit password", width=24,
                                   command=self.edit_passname, bootstyle='warning')
        self.edit_pass_btn.grid(row=6, column=0, pady=10)

        # --- Back Button ---
        back_btn = ttk.Button(self, text="← Back", style='bluebutton.TButton', width=24,
                              command=lambda: controller.show_frame(HomePage))
        back_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def add_field(self):
        site = self.add_site.get()
        email = self.add_email.get()
        password = self.add_pass.get()

        if site and email and password:
            self.view.insert('', 'end', values=(site, email, password))
        else:
            _invalid(self, self.add_to_field, 'success')

    def delete_field(self):
        if self.view.selection() == ():
            _invalid(self, self.delete_btn, og_style='danger')
            return

        ans = askyesno('Deleting confirmation',
                       'Are you sure you would like to delete selected expenses?\nYou cannot undo this process.')
        if ans == False:
            return

        for item in self.view.selection():
            self.view.delete(item)

    def delete_all_fields(self):
        if self.view.get_children() == ():
            _invalid(self, self.delete_all_btn, og_style='danger')
            return

        ans = askyesno('Deleting confirmation',
                       'Are you sure you would like to delete selected expenses?\nYou cannot undo this process.')
        if ans == False:
            return

        ans = askyesno('Deleting confirmation',
                       'Are you ABSOLUTELY sure?')
        if ans == False:
            return

        for item in self.view.get_children():
            self.view.delete(item)

    def check_security_password(self):
        def evaluate_password_strength(password):
            password = str(password)
            issues = []

            if len(password) < 8:
                issues.append("too short (min 8 chars)")
            if not re.search(r'[A-Z]', password):
                issues.append("missing uppercase")
            if not re.search(r'[a-z]', password):
                issues.append("missing lowercase")
            if not re.search(r'[0-9]', password):
                issues.append("missing digit")
            if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
                issues.append("missing special char")
            if password.lower() in {"password", "123456", "qwerty", "admin", "letmein"}:
                issues.append("common password")
            if re.search(r'(.)\1\1', password):
                issues.append("has repeated chars")
            if "1234" in password or "abcd" in password.lower():
                issues.append("has sequential pattern")

            is_weak = len(issues) >= 2  # Adjust threshold as needed
            return is_weak, issues

        passes = {}

        for item in self.view.get_children():
            values = self.view.item(item)["values"]
            password = values[1]  # Make sure index matches your table

            is_weak, issues = evaluate_password_strength(password)
            if is_weak:
                passes[password] = f" → WEAK: {', '.join(issues)}"

            else:
                passes[password] = f" → STRONG"

        win = ttk.Toplevel()

        passwordview = ttk.Treeview(win, columns=('Password', 'Strength'), show="headings")
        passwordview.heading("Password", text="Password")
        passwordview.heading("Strength", text="Strength")
        passwordview.pack(expand=True, fill='both')

        lengths = []

        passwordview.tag_configure("blue", foreground="light blue")

        # Then, in your loop:
        for key, val in passes.items():
            tag = "blue"
            passwordview.insert("", "end", values=(key, val), tag=(tag,))
            lengths.append(len(val))

        try:
            win.geometry(f'{400+max(lengths) * 10}x400')
        except Exception:
            return

    def check_password_frequency(self):
        from collections import Counter
        from tkinter.messagebox import showinfo

        passwords = [self.view.item(item, 'values')[2] for item in self.view.get_children()]
        freq = Counter(passwords)

        duplicates = {pwd: count for pwd, count in freq.items() if count > 1}

        if duplicates:
            summary = "\n".join(f"{pwd}: {count} times" for pwd, count in duplicates.items())
            showinfo("Frequent Passwords", f"The following passwords are used more than once:\n\n{summary}")
        else:
            valid(self, self.check_security_btn_freq, 'No frequent passwords', 5000, 'primary', 'Check Password Frequency')
    def search_treeview(self):
        query = self.search_entry.get().lower().strip()

        if not query:
            _invalid(self, self.search_btn, og_style='warning')
            return

        found = False
        for item in self.view.get_children():
            values = self.view.item(item, "values")
            if any(query in str(val).lower() for val in values):
                self.view.selection_set(item)
                self.view.focus(item)
                self.view.see(item)
                found = True
                break

        if not found:
            _invalid(self, self.search_btn, og_style='warning')

    def edit_sitename(self):
        selected = self.view.selection()
        if not selected:
            _invalid(self, self.edit_site_btn, og_style='warning')
            return

        ans = self.edit_entry.get()

        for item in selected:
            current = self.view.item(item, "values")
            new_values = (
                ans,
                current[1] if len(current) > 1 else "",
                current[2] if len(current) > 2 else "",
            )
            self.view.item(item, values=new_values)

    def edit_passname(self):
        selected = self.view.selection()
        if not selected:
            _invalid(self, self.edit_pass_btn, og_style='warning')

        ans = self.edit_entry.get()

        for item in selected:
            current = self.view.item(item, "values")
            # Safely build a new tuple with edited second column
            new_values = (
                current[0],
                ans,
                current[2] if len(current) > 2 else "",
            )
            self.view.item(item, values=new_values)

    def copy_password(self):
        selected = self.view.selection()
        if selected:
            pw = self.view.item(selected[0])['values'][1]
            pyperclip.copy(pw)
        else:
            _invalid(self, self.copy_btn, 'primary')

    def save_passwords(self):
        data = [self.view.item(i)['values'] for i in self.view.get_children()]
        with open('passwords.json', 'w') as f:
            json.dump(data, f)

    def load_passwords(self):
        if not os.path.exists('passwords.json'):
            return
        with open('passwords.json') as f:
            for row in json.load(f):
                self.view.insert('', 'end', values=tuple(row))

    def export_to_csv(self):
        with open('passwords.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for row in self.view.get_children():
                writer.writerow(self.view.item(row)['values'])

    def get_passwords(self):
        for entry in _get_chrome_passwords():
            self.view.insert('', 'end', values=(entry['url'], entry['username'], entry['password'])) # ('Site', 'Email or User', 'Pass')

if __name__ == '__main__':
    root = ttk.Window(themename='darkly')
    app = PasswordManagerApp(root)
    root.mainloop()
