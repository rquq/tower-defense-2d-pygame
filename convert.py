import re
import subprocess
import sys

def main():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypandoc"])
    
    with open('bao_cao_do_an.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Restore parenthesis for python type hints in docstrings
    text = re.sub(r'(\w+) kiểu (\w+):', r'\1 (\2):', text)
    
    with open('bao_cao_do_an.md', 'w', encoding='utf-8') as f:
        f.write(text)

    import pypandoc
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("Downloading pandoc...")
        pypandoc.download_pandoc()
    
    print("Converting...")
    pypandoc.convert_file('bao_cao_do_an.md', 'docx', outputfile='bao_cao_do_an.docx')
    print("Done")

if __name__ == "__main__":
    main()
