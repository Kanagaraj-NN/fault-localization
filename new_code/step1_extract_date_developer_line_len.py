import argparse
import csv
import os

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']

PROJECTS = ['Closure']

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],
#     [str(x) for x in range(1, 66)],
#     [str(x) for x in range(1, 27)],
#     [str(x) for x in range(1, 107)],
#     [str(x) for x in range(1, 39)],
#     [str(x) for x in range(1, 28)]
# ]

PROJECT_BUGS = [
     [str(x) for x in range(1, 134)]
     ]

#FORMULA = ['barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula']
#FORMULA = ['barinel', 'ochiai', 'opt2', 'tarantula']
#FORMULA = ['tarantula']

FORMULA = ['dstar2']

error_counter = 0

def find_author_date(input_file, output_file, project, bug, formula, commit_id):
    """
    find the author and date of the last update for every suspiciouss line

    Parameters
    ----------
    input_file : str (sorted suspicousness lines file)
    output_file: str (sorted suspiciousness lines file with date field and author field appended)
    project: str (project name)
    bug: str (bug id) 
    formula: str (fault localization technique)

    """
    
    # reading the suspiciousness values from the input file 
    input_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file
    sorted_susp_lines = read_susp_lines_from_file(input_file)
    
    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + output_file

    # Running git checkout buggy_version
    checkout_project_git(project, bug)

    git_blame_output = f"/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/Git_blame_output/git_blame_{project}_{bug}"

    line_counter = 0
    prev_file_name = ""
    git_blame_lines = None
    line_mapping_info = None

    for susp_line in sorted_susp_lines:
        file_name_full, line_number = susp_line[0].split("#")
        line_number = int(line_number)
        file_name = file_name_full.split("/")[-1]
        if prev_file_name != file_name:
            checkout_project_git_using_tag(project, bug)
            line_mapping_info, git_blame_lines = compute_diff_git_blame_lines(file_name, file_name_full, git_blame_output, commit_id)
            prev_file_name = file_name

        if line_mapping_info:   # If the diff is non empty, then take the correct line number from the mapping
            line_number = line_mapping_info[line_number]

        # BUG FIX
        if line_number > len(git_blame_lines):
            print(" ########## ERROR ########### ")
            print(f"Line number {line_number} from the suspiciousness file is not present in Git_blame_output_file")
            print(f"Line number to be searched: {line_number} ; Number of lines in the Git_blame_output: {len(git_blame_lines)}")

            global error_counter
            error_counter += 1
            #TODO: uncomment
            #raise ValueError("ERROR: Mismatch in the line numbers")

            # add_author_date_to_file(output_file, susp_line, "NOT_FOUND", "NOT_FOUND")
            #
            # print(f"Not collecting date and author for the project: {project} and bug: {bug}")
            # return

        # if line_number is -1, it is newly added. so, the line is skipped when it line number is -1
        if line_number in git_blame_lines:
            blame_line = git_blame_lines[line_number] # picking the line
            # find the author and date
            author, date, line_length = extract_author_date_line_length(blame_line[0])
            add_author_date_to_file(output_file, susp_line, author, date, line_length)

        line_counter += 1 

        # print(f"=================LINE : {line_counter}==========\n\n\n")


def add_author_date_to_file(output_file, susp_line, author, date, line_length):
    """
    appends the author and date to the output file containing suspiciousness lines
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    author: str
    date: str

    """
    susp_line = ", ".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line}, {author}, {date}, {line_length}\n")



def read_susp_lines_from_file(input_file):
    """
    reads the suspiciousness lines data from the sorted suspiciousness file

    Parameters:
    ----------
    input_file: str

    return:
    ------
    sorted_susp_lines: list (2D)

    """
    susp_data = csv.reader(open(input_file), delimiter=',')

    top_n_lines = 1000
    # header line is not needed (first line is skipped)
    sorted_susp_lines = [susp_line for i, susp_line in enumerate(susp_data) if i != 0 and i <= top_n_lines]
   
    return sorted_susp_lines


def checkout_project_git_using_tag(project, bug):
    """ 
    Checkout to the Defects4j buggy version

    Parameters:
    ----------
    project: str
    bug: str
    """
    commit_tag = f"D4J_{project}_{bug}_BUGGY_VERSION"
    os.system(f"git checkout {commit_tag}")


def checkout_project_git(project, bug):
    """
    checkout to the project using git commands

    Parameters:
    ----------
    project: str
    bug: str
    """

    checkout_directory = f"/tmp/{project}_{bug}_buggy_ver"
    command_git_checkout = f"defects4j checkout -p {project} -v {bug}b -w {checkout_directory}" 
    os.system(command_git_checkout)
    os.chdir(checkout_directory)


def extract_author_date_line_length(line):
    """
    parses the line and extract the author and date

    Parameters:
    ----------
    line: str (line from the git output file)

    return:
    -------
    author: author of the line
    date: date of change
    """

    name_start_index = line.find("(") + 1
    end_index = line.find(")") - 1

    author = ""
    i = name_start_index
    while not (line[i].isdigit() and line[i+1].isdigit() and line[i+2].isdigit() and line[i+3].isdigit()) :
        author += line[i]
        i += 1

    author = author.strip()     # removing sorrounding white spaces
    date = "".join([line[indx] for indx in range(i, i+10)])

    i += 10
    while line[i] != ")":
        i += 1

    line_len_counter = 0

    i += 1  # Skipping the last bracket
    # print(line[i:])
    while i < len(line):
        if line[i] != " ":
            line_len_counter += 1
        i += 1

    # print(line)
    # import pdb;
    # pdb.set_trace()

    return author, date, line_len_counter


def find_correct_author_date(line, commit_id, file_name, file_name_full, git_blame_output):
    """
    Checkout the original buggy version of the project and collect the 
    author and data for the lines

    Parameters:
    ----------
    line: str
    commit_id: str
    file_name: str
    git_blame_output: str
    """
    os.system(f"git checkout {commit_id}")
    file_path = find_file_path(file_name, file_name_full)
    git_blame_output += "_orig"
    os.system(f"git blame {file_path} > {git_blame_output}")
    git_blame_data = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_list =  list(git_blame_data)
    git_blame_lines = {(i+1):git_blame_list[i] for i in range(len(git_blame_list))}        
    source_code = extract_src_code_from_line(line)
    orig_line_id, orig_line = find_line_in_orig_buggy_version(git_blame_lines, source_code)
 
    if orig_line_id != -1:
        author, date, line_length = extract_author_date_line_length(orig_line)
    else:
        author = "defects4j"
        date = "2018-04-25"
    return author, date, line_length


def find_line_in_orig_buggy_version(git_blame_lines, source_code):
    """
    Search the line in the original buggy version and return found line id 
    
    Parameters:
    ----------
    git_blame_lines: str
    source_code: str
    """
    for line_id, git_line in git_blame_lines.items():
        if git_line[0].find(source_code) != -1:
            return line_id, git_line[0]

    print("#### LINE NOT FOUND IN THE BUGGY VERSION")
    return -1, "NOT-FOUND"


def extract_src_code_from_line(line):
    """
    Extract the source code text from the git blame line

    Parameters:
    ----------
    line: str    
    """

    loc1 = line.find(")")
    i = loc1
    source_code = ""

    while i < len(line):
        source_code += line[i]
        i += 1

    return source_code


def find_file_path(file_name, susp_file_path):
    """
    Find the full path of the file

    Parameters:
    ----------
    file_name: str
    susp_file_path: str
    """
    find_command = f"find -name {file_name}"
    os.system(f"{find_command} > find_output.txt")
    with open("find_output.txt") as file:
        file_paths = file.readlines()

    if len(file_paths) == 1:
        return file_paths[0].strip("\n")

    for file_path in file_paths:
        if susp_file_path in file_path:
            return file_path.strip("\n")


# def find_file_path(file_name):
#     """
#     Find the full path of the file

#     Parameters:
#     ----------
#     file_name: str
#     """
#     find_command = f"find -name {file_name}"
#     file_path = None
#     os.system(f"{find_command} > find_output.txt")
#     with open("find_output.txt") as file:
#         file_path = file.readline()

#     file_path = file_path.strip("\n")
#     return file_path    


def extract_git_blame_lines(file_name, susp_file_path, git_blame_output):
    """
    run git blame on the given file and return the git blame lines    
    Parameters:
    ----------
    file_name: str (file name passed to git blame command)
    susp_file_path: str (file path in the suspiciousness output)
    git_blame_output : str (output file where git blame command output is dumped)

    """
    file_path = find_file_path(file_name, susp_file_path)
    os.system(f"git blame {file_path} > {git_blame_output}")
    git_blame_data = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_list =  list(git_blame_data)
    git_blame_lines = {(i+1):git_blame_list[i] for i in range(len(git_blame_list))}    
  
    return git_blame_lines


def compute_diff_git_blame_lines(file_name, file_name_full, git_blame_output, commit_id_original_buggy_version):

    file_path = find_file_path(file_name, file_name_full)
    os.system(f"git blame {file_path} > {git_blame_output}")

    defects4j_buggy_file = git_blame_output + "_defects4j_buggy_file"
    os.system(f"cat {file_path} > {defects4j_buggy_file}")

    # Original buggy version
    os.system(f"git checkout {commit_id_original_buggy_version}")

    file_path = find_file_path(file_name, file_name_full)
    git_blame_output_orig = git_blame_output + "_orig"
    os.system(f"git blame {file_path} > {git_blame_output_orig}")

    original_buggy_file = git_blame_output + "_original_buggy_file"
    os.system(f"cat {file_path} > {original_buggy_file}")

    git_blame_diff = git_blame_output + "_diff_blame"
    os.system(f"diff {git_blame_output_orig} {git_blame_output} > {git_blame_diff}")

    diff_output = git_blame_output + "_diff_output"
    os.system(f"diff {original_buggy_file} {defects4j_buggy_file} > {diff_output}")

    git_blame_lines_new = csv.reader(open(git_blame_output, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_new = list(git_blame_lines_new)
    git_blame_lines_new = {(i+1):git_blame_lines_new[i] for i in range(len(git_blame_lines_new))}
    number_of_lines_new = len(git_blame_lines_new)

    git_blame_lines_orig = csv.reader(open(git_blame_output_orig, encoding='ISO-8859-1'), delimiter='\n')
    git_blame_lines_orig = list(git_blame_lines_orig)
    git_blame_lines_orig = {(i+1):git_blame_lines_orig[i] for i in range(len(git_blame_lines_orig))}
    number_of_lines_old = len(git_blame_lines_orig)

    # if the diff is empty, no need of line mapping
    if os.stat(diff_output).st_size == 0:
        return None, git_blame_lines_orig


    home_path = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/Git_blame_output/"
    path_to_diff_runner = home_path + "RunDiffProcessor_4.jar"
    properties_file = home_path + "HistorySlicingFuzzy.properties"
    # diff_file = home_path + "_diff_output_file"
    line_mapping_output_file = git_blame_output + "_line_mapping"

    os.system(f"java -jar {path_to_diff_runner} {properties_file} {diff_output} {number_of_lines_old} {number_of_lines_new} > {line_mapping_output_file}")

    line_mapping_info = csv.reader(open(line_mapping_output_file, encoding='ISO-8859-1'), delimiter='\n')
    line_mapping_info = list(line_mapping_info)
    line_mapping_info = {(i + 1): int(*line_mapping_info[i]) for i in range(len(line_mapping_info))}
    print("size of line mapping dict: ", len(line_mapping_info))
    return line_mapping_info, git_blame_lines_orig


def get_commit_ids(project):
    """
    finds the commit data for all the bugs for the given defects4j project

    Parameters:
    ----------
    project: str (name of the project)
    
    return:
    ------
    commit_ids : dictionary (key:value pair is bug id:commit id)

    """
    
    # Getting the commit data for each project 
    path_to_commit_db = "/home/kanag23/Desktop/Defects4j_v2/defects4j/framework/projects/"
    commit_db_file = os.path.join(path_to_commit_db, project, "commit-db")
    commit_db_data = csv.reader(open(commit_db_file), delimiter=',')
    commit_db_list = list(commit_db_data)
    commit_ids = {commit_id_line[0]:commit_id_line[1] for commit_id_line in commit_db_list}

    return commit_ids


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')

    args = parser.parse_args()

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        commit_ids = get_commit_ids(project)
        for bug in bugs:
            for formula in FORMULA:
                input_csv = f"{project}-{bug}-{formula}-sorted-susp"
                output_csv = f"{project}-{bug}-{formula}-sorted-susp-with-date"
                find_author_date(os.path.join(args.suspiciousness_data_dir, input_csv),
                     os.path.join(args.output_dir, output_csv), project, bug, formula, commit_ids[bug])

    print(f"ERROR COUNTER : {error_counter}")