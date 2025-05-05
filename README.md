# Password Manager App

App for generating, strengthening, and managing your passwords. Built with `ttkbootstrap`, featuring password safety tools and password reuse detection. 
**NOTE:** still in WIP. Will add updates either never or very soon.

---

## Features

- **Generate strong passwords** with control over length, letters, numbers, and symbols.
- **Strengthen existing passwords** with substitutions and added randomness.
- **Manage your saved passwords** with a table-based UI (site + password).
- **Remove, search, or edit** saved passwords easily.
- **Password security check** flags weak or common passwords.
- **Password frequency check** warns of reused passwords.
- **Modern UI** using the `ttkbootstrap` dark theme.
- **Clipboard support** for one-click copying.
- **Image/logo support** via base64. I am NOT bouta include screenshots hell naw.

---

## Technologies Used

- `Python 3.11`
- `tkinter` + `ttkbootstrap`
- `PIL` for image handling
- `secrets`, `string`, `re`, `base64`, `collections.Counter`
  
---

## How to Run

You know it already.

```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager
python main.py
```

Make sure the required dependencies are installed (mostly standard lib + `ttkbootstrap`, `Pillow`):

```bash
pip install ttkbootstrap Pillow
```

---

## File Overview

- `main.py` – Main application logic and UI
- `passwordmanagerlogo.png` – App icon (or base64-encoded in code)
- `README.md` – You’re here!

---

## Security Notes

- This app does **not** store data persistently (no file/database).
- Passwords are **kept in memory only** and lost on close. Prolly gonnu add a save feature.
- Be cautious when using real credentials.

---

## License
Andre Lic

---

## Author

Made with anxiety and sting by [Danny](https://github.com/DanielIsHungry)
