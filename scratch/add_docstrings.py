import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Match class or def
        match = re.match(r'^(\s*)(class|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', line)
        if match:
            indent = match.group(1)
            type_name = match.group(2)
            name = match.group(3)
            
            # Find the next non-empty line
            next_non_empty = -1
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    next_non_empty = j
                    break
            
            if next_non_empty != -1:
                # Check if it already has a docstring
                if lines[next_non_empty].strip().startswith('"""') or lines[next_non_empty].strip().startswith("'''"):
                    pass # Already has one
                else:
                    doc_indent = indent + "    "
                    docstring = f'{doc_indent}"""\n{doc_indent}Docstring for {type_name} {name}.\n{doc_indent}"""\n'
                    new_lines.append(docstring)
            else:
                # End of file
                doc_indent = indent + "    "
                docstring = f'{doc_indent}"""\n{doc_indent}Docstring for {type_name} {name}.\n{doc_indent}"""\n'
                new_lines.append(docstring)
        i += 1
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def main():
    base_dir = r"E:\CODING\Python\TowerDefense"
    folders = ['core', 'entities', 'systems']
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if os.path.exists(folder_path):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
