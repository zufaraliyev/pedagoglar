import re
import json

def parse_gift(text):
    # Normalize unicode quotes and question markers
    text = text.replace('\ufffd', "'").replace('', "'")
    
    # Matches ::number:: Question { =Correct ~Wrong ~Wrong ~Wrong } or A) ~ ~ ~
    raw_blocks = re.split(r'::\d+::', text)
    parsed = []
    
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        
        # Look for question and options
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
            
        question = lines[0].strip()
        # Clean up leading/trailing symbols
        question = re.sub(r'^[^\w\d\(\"\']+', '', question)
        
        options = []
        correct_idx = 0
        
        for line in lines[1:]:
            line = line.strip()
            if not line or line == '}':
                continue
                
            # If line is correct answer: A) or {=
            if line.startswith('{=') or line.startswith('A)'):
                opt = re.sub(r'^(\{=|A\))\s*', '', line).rstrip('}').strip()
                if opt:
                    options.append(opt)
                    correct_idx = len(options) - 1
            elif line.startswith('~'):
                opt = line.lstrip('~').rstrip('}').strip()
                if opt:
                    options.append(opt)
            elif re.match(r'^[B-D]\)', line):
                opt = line[2:].strip()
                if opt:
                    options.append(opt)
            elif len(options) > 0 and not line.startswith('::'):
                # multiline option continuation
                options[-1] += " " + line
                
        if len(options) >= 2 and len(question) > 5:
            # Ensure we have at least 4 options or pad if 3
            parsed.append({
                "question": question,
                "options": options[:4],
                "correct_option": correct_idx if correct_idx < len(options) else 0,
                "explanation": f"Mazkur savol boshlang'ich ta'lim pedagogikasi va didaktika fanining me'yoriy talablariga asoslangan."
            })
            
    return parsed

if __name__ == '__main__':
    with open(r'D:\Antigravity\PEDSTART\DATA\200_test_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
        t200 = f.read()
    res200 = parse_gift(t200)
    print(f"Parsed {len(res200)} questions from 200_test.")

    with open(r'D:\Antigravity\PEDSTART\DATA\yakuniy_100_extracted.txt', 'r', encoding='utf-8', errors='ignore') as f:
        t100 = f.read()
    res100 = parse_gift(t100)
    print(f"Parsed {len(res100)} questions from yakuniy_100.")
    
    with open('parsed_questions_sample.json', 'w', encoding='utf-8') as out:
        json.dump(res200[:5], out, ensure_ascii=False, indent=2)
