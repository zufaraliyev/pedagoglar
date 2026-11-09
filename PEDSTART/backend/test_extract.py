import os
import docx
import re
from pptx import Presentation

data_dir = r"D:\Antigravity\PEDTAYYOR\DATA"

def clean_uz_text(text):
    if not text:
        return ""
    # Buzilgan apostroflar va belgilarni to'g'rilash
    text = text.replace('\ufffd', "'")
    text = text.replace('', "'")
    text = text.replace('‘', "'").replace('’', "'").replace('`', "'")
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

# Fayllar xaritasi
lecture_files = {
    1: "1-ma'ruza.docx",
    2: "2-mavzu.docx",
    3: "3-mavzu.docx",
    4: "4.1-mavzu.docx",
    5: "5-mavzu.docx",
    6: "6-mavzu.docx",
    7: "7-mavzu.docx",
    8: "Pedagogika, 8-ma'ruza.pptx",
    9: "9-mavzu.docx",
    10: "10-mavzu.docx",
    11: "11-mavzu.docx",
    12: "12-mavzu.docx",
    13: "13-mavzu.docx",
    14: "14-dars.docx",
    15: "15-mavzu.docx",
}

for num in range(1, 16):
    fname = lecture_files[num]
    fpath = os.path.join(data_dir, fname)
    if not os.path.exists(fpath):
        print(f"Mavzu {num}: {fname} TOPILMADI!")
        continue
    
    if fname.endswith('.docx'):
        doc = docx.Document(fpath)
        paragraphs = [clean_uz_text(p.text) for p in doc.paragraphs if clean_uz_text(p.text)]
        print(f"Mavzu {num} ({fname}): {len(paragraphs)} ta paragraf, {sum(len(p) for p in paragraphs)} belgi")
        if paragraphs:
            print("  Boshlanishi:", paragraphs[0][:120])
    elif fname.endswith('.pptx'):
        prs = Presentation(fpath)
        texts = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    t = clean_uz_text(shape.text_frame.text)
                    if t:
                        texts.append(t)
        print(f"Mavzu {num} ({fname}): {len(texts)} ta slayd matni, {sum(len(p) for p in texts)} belgi")
        if texts:
            print("  Boshlanishi:", texts[0][:120])
