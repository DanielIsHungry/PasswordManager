import ttkbootstrap as ttk
import string
import re
import base64
from random import choice
from PIL import Image, ImageTk
from tkinter.messagebox import askyesno
from secrets import choice
from collections import Counter
from io import BytesIO

ENCODED_IMAGE = b'''
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
'''

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

    def strengthen_password(self):
        original = self.entry.get().strip()

        if not original:
            self.entry.delete(0, 'end')
            self.entry.insert(0, "⚠️ Enter a password first")
            return

        # Substitution rules
        substitutions = {
            'a': '@', 'A': '@',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '$', 'S': '$',
            'l': '1', 'L': '1',
            't': '7', 'T': '7',
            ' ': '_', '_': '-'
        }

        # Apply substitutions and random case
        strengthened = ''
        for char in original:
            if char in substitutions:
                strengthened += substitutions[char]
            else:
                strengthened += choice([char.lower(), char.upper()])

        # Add random symbols and digits
        extras = ''.join(choice(string.digits + "!@#$%") for _ in range(4))
        strengthened += "_" + extras

        # Show result
        self.entry.delete(0, 'end')
        self.entry.insert(0, strengthened)
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
        self.view = ttk.Treeview(self, columns=('Name', 'Pass'), show="headings")
        self.view.heading("Name", text="Site Name")
        self.view.heading("Pass", text="Password")
        self.view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # --- Right-side vertical container ---
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

        # --- Add Frame ---
        add_frame = ttk.LabelFrame(right_frame, text='Add')
        add_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(add_frame, text="Site:").grid(row=0, column=0, sticky="w")
        self.add_site = ttk.Entry(add_frame, width=25)
        self.add_site.grid(row=1, column=0, pady=(0, 10), sticky="w")
        self.add_site.insert(0, 'https://example.com/')

        ttk.Label(add_frame, text="Password:").grid(row=2, column=0, sticky="w")
        self.add_pass = ttk.Entry(add_frame, width=25)
        self.add_pass.grid(row=3, column=0, sticky="w")
        self.add_pass.insert(0, 'ExamplePassword')

        add_to_field = ttk.Button(add_frame, text='Add To Passwords', padding=10,
                                  command=self.add_field, bootstyle='success')
        add_to_field.grid(row=4, column=0, pady=10)

        # --- Remove Frame ---
        del_frame = ttk.LabelFrame(right_frame, text='Remove')
        del_frame.pack(fill='x')

        delete_btn = ttk.Button(del_frame, text="Remove Selected", width=24,
                                command=self.delete_field, bootstyle='danger')
        delete_btn.grid(row=0, column=0, pady=10)

        delete_all_btn = ttk.Button(del_frame, text="Remove All", width=24,
                                    command=self.delete_all_fields, bootstyle='danger')
        delete_all_btn.grid(row=1, column=0, pady=10)

        tools_frame = ttk.LabelFrame(right_frame, text='Tools')
        tools_frame.pack(fill='x')

        check_security_btn = ttk.Button(tools_frame, text="Check Password Security", width=24,
                                        command=self.check_security_password, bootstyle='primary')
        check_security_btn.grid(row=1, column=0, pady=10)

        check_security_btn = ttk.Button(tools_frame, text="Check Password Frequency", width=24,
                                        command=self.check_password_frequency, bootstyle='primary')
        check_security_btn.grid(row=2, column=0, pady=10)

        edit_frame = ttk.LabelFrame(right_frame, text='Search and edit')
        edit_frame.pack(fill='x')

        ttk.Label(edit_frame, text="Search Site or Password:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(edit_frame, width=25)
        self.search_entry.grid(row=1, column=0, pady=(0, 10), sticky="w")
        self.search_entry.insert(0, 'https://example.com/')

        search_btn = ttk.Button(edit_frame, text="Search", width=24,
                                        command=self.search_treeview, bootstyle='warning')
        search_btn.grid(row=2, column=0, pady=10)

        # --- Back Button ---
        back_btn = ttk.Button(self, text="← Back", style='bluebutton.TButton', width=24,
                              command=lambda: controller.show_frame(HomePage))
        back_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def add_field(self):
        self.view.insert(
            "", "end",
            values=(self.add_site.get(), self.add_pass.get())
        )

        passwords = []

        for item in self.view.get_children():
            values = self.view.item(item, 'values')
            passwords.append(values)

    def delete_field(self):
        if self.view.selection() == ():
            return

        ans = askyesno('Deleting confirmation',
                       'Are you sure you would like to delete selected expenses?\nYou cannot undo this process.')
        if ans == False:
            return

        for item in self.view.selection():
            self.view.delete(item)

    def delete_all_fields(self):
        print(self.view.get_children())
        if self.view.get_children() == ():
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
        passes = []
        for item in self.view.get_children():
            values = self.view.item(item)["values"]
            password = values[1]
            passes.append(password)
        freq = Counter(passes)
        repeated = {pwd: count for pwd, count in freq.items() if count > 4}

        win = ttk.Toplevel()

        passwordview = ttk.Treeview(win, columns=('PasswordName', 'Frequency', 'Danger'), show="headings")
        passwordview.heading("PasswordName", text="Password")
        passwordview.heading("Frequency", text="Frequency")
        passwordview.heading("Danger", text="Danger")
        passwordview.pack(expand=True, fill='both')
        passwordview.tag_configure("blue", foreground="light blue")

        for pwd, count in repeated.items():
            tag = 'blue'
            danger = 'None' if count < 4 else 'Frequent'
            passwordview.insert("", "end", values=(pwd, count, danger))

    def search_treeview(self):
        query = self.search_entry.get().lower().strip()

        if not query:
            return

        found = False
        for item in self.view.get_children():
            values = self.view.item(item, "values")
            if any(query in str(val).lower() for val in values):
                self.view.selection_set(item)
                self.view.focus(item)
                self.view.see(item)
                found = True
                break  # Only focus the first match

        if not found:
            self.search_entry.delete(0, 'end')
            self.search_entry.insert(0, "❌ Not Found")


if __name__ == '__main__':
    try:
        root = ttk.Window(themename='darkly')
        app = PasswordManagerApp(root)
        root.mainloop()
    except Exception:
        print('')
