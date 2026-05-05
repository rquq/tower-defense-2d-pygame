import os
import ast

def extract_docstrings(directory):
    results = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, directory)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filepath)
                        docstrings = []
                        
                        # Module docstring
                        mod_doc = ast.get_docstring(tree)
                        if mod_doc:
                            docstrings.append(f"# Module Docstring\n{mod_doc}")
                        
                        # Look at top-level statements
                        for node in tree.body:
                            if isinstance(node, ast.ClassDef):
                                class_doc = ast.get_docstring(node)
                                if class_doc:
                                    docstrings.append(f"## Class: {node.name}\n{class_doc}")
                                
                                for body_node in node.body:
                                    if isinstance(body_node, ast.FunctionDef):
                                        func_doc = ast.get_docstring(body_node)
                                        if func_doc:
                                            docstrings.append(f"### Method: {node.name}.{body_node.name}\n{func_doc}")
                                            
                            elif isinstance(node, ast.FunctionDef):
                                func_doc = ast.get_docstring(node)
                                if func_doc:
                                    docstrings.append(f"## Function: {node.name}\n{func_doc}")
                                    
                        if docstrings:
                            results[rel_path] = docstrings
                    except Exception as e:
                        print(f"Error parsing {filepath}: {e}")
    return results

def main():
    base_dir = r"E:\CODING\Python\TowerDefense"
    folders = ['core', 'entities', 'systems']
    
    with open(r"E:\CODING\Python\TowerDefense\scratch\extracted_docstrings.md", "w", encoding="utf-8") as out:
        for folder in folders:
            folder_path = os.path.join(base_dir, folder)
            if os.path.exists(folder_path):
                out.write(f"# Thư mục: {folder}\n\n")
                doc_map = extract_docstrings(folder_path)
                for file, docs in doc_map.items():
                    out.write(f"## File: `{file}`\n\n")
                    for doc in docs:
                        out.write(f"{doc}\n\n---\n\n")

if __name__ == "__main__":
    main()
