import fitz

pdf_path = 'C:/Users/admin/Documents/read_paper/Robot_readpaper/paper-2026-04-16-pi0-7/paper.pdf'
doc = fitz.open(pdf_path)
text = ''
for page_num in range(len(doc)):
    page = doc[page_num]
    text += page.get_text()
    
# Save text to file
with open('C:/Users/admin/Documents/read_paper/Robot_readpaper/paper-2026-04-16-pi0-7/paper_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)
    
print(f"Extracted {len(text)} characters from PDF")
print("First 500 characters:")
print(text[:500])