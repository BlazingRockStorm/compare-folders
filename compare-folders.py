from difflib import Differ
import os
from filecmp import dircmp
import configparser

def find_unique_files(dcmp):
    uniqueFilesLeft = []
    uniqueFilesRight = []
    # dir1 unique files
    if len(dcmp.left_only) != 0:
        for filename in dcmp.left_only:
            uniqueFilesLeft.append(dcmp.left+"/"+filename)
    # dir2 unique files
    if len(dcmp.right_only) != 0:
        for filename in dcmp.right_only:
            uniqueFilesRight.append(dcmp.right+"/"+filename)
    # recursive call to process the sub folders
    for sub_dcmp in dcmp.subdirs.values():
        sub_uniques = find_unique_files(sub_dcmp)
        uniqueFilesLeft += sub_uniques["left"]
        uniqueFilesRight += sub_uniques["right"]
    uniqueFilesLeft.sort()
    uniqueFilesRight.sort()
    return {"left": uniqueFilesLeft, "right": uniqueFilesRight}


def build_common_files(dcmp):
    # listing common files in dir
    commonFiles = []
    for filename in dcmp.common_files:
        commonFiles.append(dcmp.left + "/" + filename)
    # listing in sub-dirs
    for subdir in dcmp.common_dirs:
        subCommonFiles = build_common_files(dircmp(dcmp.left + "/" + subdir, dcmp.right + "/" + subdir))
        for filename in subCommonFiles:
            commonFiles.append(filename)
    commonFiles.sort()
    return commonFiles


def print_unique_files(files, result_file):
    count = 0
    if len(files) != 0:
        for filepath in files:
            if os.path.isdir(filepath):
                filepath += '/'
            with open(r"%s"%(filepath), 'r') as fp:
                for count, line in enumerate(fp):
                    pass
            f = open("%s"%(result_file),'a+')
            f.write('%s,%s\n'%(filepath,count + 1))

config = configparser.ConfigParser()
config.read('example.ini')
default_config = config['DEFAULT']
print(default_config['old'])
print(default_config['new'])
if not os.path.isdir(default_config['old']):
    print(default_config['old'] + " is not a valid directory")
    exit(-1)
if not os.path.isdir(default_config['new']):
    print(default_config['new'] + " is not a valid directory")
    exit(-1)

print("Analyzing directories...")
dcmp = dircmp(default_config['old'], default_config['new'])
uniqueFiles = find_unique_files(dcmp)

print("Building common files list...")
commonFiles = build_common_files(dcmp)
relativePathsCommonFiles = []
for filename in commonFiles:  # removing the root folder
    relativePathsCommonFiles.append(filename[len(default_config['old'])+1:])

filesDifferent = []
print("Searching for file differences by computing hashes...\n")
for filepath in relativePathsCommonFiles:
    open("changed_files_list.csv",'w+')
    filepathLeft = default_config['old'] + "/" + filepath
    filepathRight = default_config['new'] + "/" + filepath
    line_no = 1
    count = 0
    file_1 = open(filepathLeft, 'r', encoding="UTF-8")    
    file_2 = open(filepathRight, 'r', encoding="UTF-8")
    
    file_1_line = file_1.readline()
    file_2_line = file_2.readline()
 
    while file_1_line != '' or file_2_line != '':
 
        # Removing whitespaces
        file_1_line = file_1_line.rstrip()
        file_2_line = file_2_line.rstrip()
    
        # Compare the lines from both file
        if file_1_line != file_2_line:
            count += 1
        file_1_line = file_1.readline()
        file_2_line = file_2.readline()
    
        line_no += 1
    
    f = open("changed_files_list.csv",'a+')
    f.write('%s,%s\n'%(filepath,count))

    file_1.close()
    file_2.close()
print("Changed files list report completed!\n")

if uniqueFiles["left"]:
    open("deleted_files_list.csv",'w+')
    print_unique_files(uniqueFiles["left"], "deleted_files_list.csv")
    print("Deleted files list report completed!\n")
if uniqueFiles["right"]:
    open("added_files_list.csv",'w+')
    print_unique_files(uniqueFiles["right"], "added_files_list.csv")
    print("Added files list report completed!\n")

if len(filesDifferent)+len(uniqueFiles["left"])+len(uniqueFiles["right"]) == 0:
    print("NO DIFFERENCE FOUND :)\n")
