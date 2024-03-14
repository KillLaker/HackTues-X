import os
from tika import parser

file_path = 'static/uploads/TUES11SW-VMKS-2_semester_Lecture 1.pdf'

if file_path.endswith('.docx') or file_path.endswith('.pptx') or file_path.endswith('.pdf'):
    parsed = parser.from_file(file_path)
    text = parsed['content']
    # print(text)

def remove_extra_newlines(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() != '':
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1] != '':
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

cleaned_text = remove_extra_newlines(text)
print(cleaned_text)