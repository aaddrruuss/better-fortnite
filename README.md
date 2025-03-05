# Better Fortnite 🎮🔥

A simple Python application that initializes a controller-based program. The entry point calls a run_app() function to start the application logic.

## ⭐ Features

- 🚀 **Quick Account Switching**: Allows you to switch between different Fortnite accounts without manually logging in and out each time.
- 🎨 **Intuitive Interface**: Simple and easy-to-use design that enhances user experience.
- 🔒 **Secure Credential Management**: Stores account credentials securely to ensure user privacy and security.
- Simple interface with a clear entry point.
- Modular design separating the main script and controller logic.
- Easy to run with minimal setup.

## 🛠️ Prerequisites
- Python 3.6 or higher

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/aaddrruuss/better-fortnite.git
   cd better-fortnite
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # For Windows:
   venv\Scripts\activate
   # For Unix-based systems:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   Make sure you have [Python](https://www.python.org/downloads/) installed. Then, install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python src/main.py
   ```

## 🚀 Easy Installation - Recommended Method ✅

If you prefer a quick and hassle-free setup, follow these steps:

1. ~~📝 **Create the `.env` file** in the project root with the credential information.~~ __**(NO LONGER NEEDED)**

2. 🎮 **Run the latest `.exe` file version** located in `dist/`.

⚡ **No need to install Python or dependencies!**

This is the easiest and fastest way to start using the application.

## 🎯 Usage

Upon running, the application will delegate control to the controller module (via run_app()). Follow any on-screen instructions or prompts within the app.

1. 🆕 **Add accounts**: When launching the application for the first time, you will be prompted to enter your Fortnite account credentials.
2. 🔄 **Switch accounts**: Select the account you want to switch to, and the application will automatically handle the logout and login process in Fortnite.

## ⌨️ Keyboard Shortcuts

Better Fortnite includes several keyboard shortcuts to improve efficiency:

- ⏭ **AltGr + S**: Skip mission animation.
- 🚪 **AltGr + L**: Leave party.
- 🎮 **AltGr + Up Arrow**: Open Fortnite.
- 🔍 **AltGr + Down Arrow**: Check current account.
- ⬅️ **AltGr + Left Arrow**: Switch to the previous account.
- ➡️ **AltGr + Right Arrow**: Switch account or add a new one if there isn't one already.
- ➡️ **AltGr + Q**: Opens 'FortniteDB' website on your browser.

These shortcuts allow for a faster and more seamless experience when managing multiple accounts.

## 🤝 Contributions

Contributions are welcome! If you would like to improve this project:

1. 🍴 **Fork the repository**.
2. 🌱 **Create a new branch** (`git checkout -b feature/new-feature`).
3. 🛠 **Make your changes and commit** (`git commit -m 'Add new feature'`).
4. 📤 **Push your changes** to your repository (`git push origin feature/new-feature`).
5. 🔄 **Open a Pull Request** on GitHub.

## 📜 License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.
