# patch_usermodel.py
from pathlib import Path

f = Path("backend/src/models/userModel.js")

text = f.read_text(encoding="utf-8")

# Fix escaped template literals
text = text.replace("\\`", "`")

f.write_text(text, encoding="utf-8")

print("✅ Fixed escaped backticks in userModel.js")
