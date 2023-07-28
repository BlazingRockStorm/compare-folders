import os
import csv
import filecmp
import difflib
import configparser
import chardet

TEXT_EXTENSIONS = ['.html', '.htm', '.css', '.js', '.txt', '.java', '.jsp', '.xsd', '.xml', '.properties', '.tag']

def is_text_file(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower() in TEXT_EXTENSIONS

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def preprocess_lines(lines):
    # Convert line endings to LF (Unix-style) for consistent comparison
    return [line.rstrip('\r\n') + '\n' for line in lines]

def count_changed_lines(file1, file2):
    encoding1 = detect_file_encoding(file1)
    encoding2 = detect_file_encoding(file2)

    with open(file1, 'r', encoding=encoding1, errors='replace') as f1, \
         open(file2, 'r', encoding=encoding2, errors='replace') as f2:
        lines1 = preprocess_lines(f1.readlines())
        lines2 = preprocess_lines(f2.readlines())

    differ = difflib.Differ()
    diff = differ.compare(lines1, lines2)
    changed_lines = sum(1 for line in diff if line.startswith('+ ') or line.startswith('- '))

    return changed_lines

def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return len(f.readlines())
    
def compare_folders(folder1, folder2):
    results = []

    for root, dirs, files in os.walk(folder1):
        for file in files:
            file1_path = os.path.join(root, file)
            file2_path = os.path.join(folder2, os.path.relpath(file1_path, folder1))

            if not (os.path.exists(file2_path) and filecmp.cmp(file1_path, file2_path)):
                if is_text_file(file1_path) and is_text_file(file2_path):
                    changed_lines = count_changed_lines(file1_path, file2_path)
                    results.append((file1_path, file2_path, changed_lines))

    for root, dirs, files in os.walk(folder2):
        for file in files:
            file2_path = os.path.join(root, file)
            file1_path = os.path.join(folder1, os.path.relpath(file2_path, folder2))

            if not (os.path.exists(file1_path)):
                if is_text_file(file2_path) and is_text_file(file1_path):
                    exclusive_lines = count_lines(file2_path)
                    results.append(('', file2_path, exclusive_lines))

    sum_changed_lines = sum(result[2] for result in results)
    results.append(('変更ライン数合計:', '', sum_changed_lines))


    return results

def export_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['元のコード', '新しいコード', '変更ライン数'])

        for result in results:
            csv_writer.writerow(result)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('example.ini')
    default_config = config['DEFAULT']
    folder1 = default_config['old']
    folder2 = default_config['new']
    output_csv = 'comparison_results.csv'

    comparison_results = compare_folders(folder1, folder2)
    export_to_csv(comparison_results, output_csv)
    print("Comparison completed. Results exported to", output_csv)
