import os
import docx

data_dir = r"D:\Antigravity\PEDTAYYOR\DATA"
files = sorted([f for f in os.listdir(data_dir) if f.endswith('.docx')])

print(f"Jami .docx fayllar: {len(files)}")
for f in files:
    path = os.path.join(data_dir, f)
    try:
        doc = docx.Document(path)
        first_p = ""
        for p in doc.paragraphs:
            if p.text.strip():
                first_p = p.text.strip()
                break
        print(f"FILE: {f} -> First line: {first_p[:100]}")
    except Exception as e:
        print(f"FILE: {f} -> ERROR: {e}")
