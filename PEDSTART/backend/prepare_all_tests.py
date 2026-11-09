import re
import json

def clean_text(s):
    if not s:
        return ""
    # Fix characters
    s = s.replace('\xa0', ' ')
    s = s.replace('', "'").replace('’', "'").replace('‘', "'")
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def extract_all_tests():
    all_tests = []
    
    # 1. Parse 200 test .doc (GIFT format)
    with open(r'D:\Antigravity\PEDTAYYOR\DATA\200_test_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().replace('\xa0', ' ').replace('\r', '')
        
    blocks = re.split(r'::\d+::', content)
    for b in blocks[1:]:
        lines = [l.strip() for l in b.split('\n') if l.strip()]
        if not lines:
            continue
        q = clean_text(lines[0])
        opts = []
        correct_idx = 0
        for l in lines[1:]:
            if l == '}':
                continue
            if l.startswith('A)') or l.startswith('{='):
                clean_opt = re.sub(r'^(A\)|\{=)\s*', '', l).rstrip('}').strip()
                clean_opt = clean_text(clean_opt)
                if clean_opt:
                    opts.append(clean_opt)
                    correct_idx = len(opts) - 1
            elif l.startswith('~'):
                clean_opt = l.lstrip('~').rstrip('}').strip()
                clean_opt = clean_text(clean_opt)
                if clean_opt:
                    opts.append(clean_opt)
        if len(opts) >= 2 and len(q) > 5:
            all_tests.append({
                "question": q,
                "options": opts[:4],
                "correct_option": correct_idx,
                "explanation": f"«{q[:60]}...» savoli boshlang'ich ta'lim pedagogikasi va didaktika fanining me'yoriy asoslariga tayanadi."
            })
            
    print(f"Loaded {len(all_tests)} questions from 200_test.")
    
    # 2. Parse yakuniy_100
    with open(r'D:\Antigravity\PEDTAYYOR\DATA\yakuniy_100_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
        y_lines = [l.strip() for l in f.readlines() if l.strip()]
        
    i = 0
    y_count = 0
    while i < len(y_lines):
        line = y_lines[i]
        # match "1. Question text"
        m = re.match(r'^\d+\.\s*(.+)', line)
        if m:
            q_text = clean_text(m.group(1))
            opts = []
            j = i + 1
            while j < len(y_lines) and not re.match(r'^\d+\.\s*', y_lines[j]) and len(opts) < 4:
                opt_line = clean_text(y_lines[j])
                if opt_line and not opt_line.startswith('1-variant') and not opt_line.startswith('2-variant'):
                    opts.append(opt_line)
                j += 1
            if len(opts) >= 2:
                all_tests.append({
                    "question": q_text,
                    "options": opts[:4],
                    "correct_option": 0,
                    "explanation": f"To'g'ri javob: «{opts[0]}». Didaktika va pedagogika qonuniyatlariga asosan to'g'ri hisoblanadi."
                })
                y_count += 1
            i = j
        else:
            i += 1
            
    print(f"Loaded {y_count} questions from yakuniy_100. Total questions: {len(all_tests)}")
    
    with open(r'D:\Antigravity\PEDTAYYOR\backend\all_tests.json', 'w', encoding='utf-8') as out:
        json.dump(all_tests, out, ensure_ascii=False, indent=2)
    print("Saved all_tests.json successfully!")

if __name__ == '__main__':
    extract_all_tests()
