import re

with open('AMORA_Conference_Paper.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Title
title_match = re.search(r'\\title\{([^}]+)\}', text)
title = title_match.group(1).replace('\\\\', ' ') if title_match else ''
title_words = len(title.split())

# Abstract
abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.DOTALL)
abstract_text = abstract_match.group(1).strip() if abstract_match else ''
abstract_clean = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', abstract_text)
abstract_words = len(re.findall(r'\b[A-Za-z0-9\'-]+\b', abstract_clean))

# Strip latex comments
text_no_comments = re.sub(r'%.*', '', text)

def get_sec_content(sec_name, next_sec_name):
    pattern = r'\\section\{' + re.escape(sec_name) + r'\}(.*?)(?=\\section\{' + re.escape(next_sec_name) + r'\}|\\begin\{thebibliography\}|$)'
    m = re.search(pattern, text_no_comments, re.DOTALL)
    if not m:
        return ''
    raw = m.group(1)
    clean = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', raw)
    return clean

intro = get_sec_content('Introduction', 'Literature Review')
lit = get_sec_content('Literature Review', 'Methodology')
meth = get_sec_content('Methodology', 'Experimental Setup and Benchmark Methodology')
exp = get_sec_content('Experimental Setup and Benchmark Methodology', 'Results')
results = get_sec_content('Results', 'Discussion')
disc = get_sec_content('Discussion', 'Conclusion')
conc = get_sec_content('Conclusion', '')

def count_words(txt):
    return len(re.findall(r'\b[A-Za-z0-9\'-]+\b', txt))

body_match = re.search(r'\\begin\{document\}(.*?)\\begin\{thebibliography\}', text_no_comments, re.DOTALL)
body_clean = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', body_match.group(1)) if body_match else ''
total_body_words = count_words(body_clean)

print("="*65)
print("SPINE OF STRONG RESEARCH PAPER - VERIFICATION AUDIT")
print("="*65)
print(f"Title: \"{title.strip()}\"")
print(f"Title Words: {title_words:5d}  | Criterion: 10-15 words, includes IV + DV")
print(f"Abstract Words: {abstract_words:5d}  | Criterion: 150-250 words, 3 parts, no refs")
print(f"Introduction:   {count_words(intro):5d}  | Criterion: ~1000 words, 4 movements (Hook, Gap, Past, Aim)")
print(f"Lit Review:     {count_words(lit):5d}  | Criterion: 1000-1500 words, synthesized, max 3 levels")
print(f"Methodology:    {count_words(meth):5d}  | Criterion: Past tense, logical steps < 300 words")
print(f"Exp Setup:      {count_words(exp):5d}  | Criterion: Participants/catalogs, tools, procedures")
print(f"Results:        {count_words(results):5d}  | Criterion: Visuals, one result/para, pure empirical")
print(f"Discussion:     {count_words(disc):5d}  | Criterion: 5-6 paragraphs max, connect to theory")
print(f"Conclusion:     {count_words(conc):5d}  | Criterion: < 250 words, reaffirm & future steps")
print(f"Total Body Words: {total_body_words:5d}  | Criterion: >= 6000 words")
print("="*65)
