import argparse
import csv
import os
import datetime

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
#FORMULA = ['tarantula']
FORMULA = ['dstar2']


def find_normalized_line_len(input_file, output_file, project, bug, formula):
    input_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file
    sorted_susp_lines = read_susp_lines_from_file(input_file)

    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + output_file

    line_length = []
    for susp_line in sorted_susp_lines:
        line_length.append(int(susp_line[-1].strip()))

    mini = min(line_length)
    maxi = max(line_length)

    diff_len = maxi - mini
    line_counter = 0

    for susp_line in sorted_susp_lines:
        if diff_len == 0:
            print("Divide by Zero: Max and Min are same")
            raise ValueError("ERROR: RARE CASE: All the dates are same")
        normalized_len = (line_length[line_counter] - mini) / diff_len
        # recency = 1 - normalized_len
        add_recency_to_file(output_file, susp_line, normalized_len)
        line_counter += 1


def find_recency(input_file, output_file, project, bug, formula):
    """
    find the recency of the last update for every suspiciouss line

    Parameters
    ----------
    input_file : str (file contains sorted suspicousness lines with date)
    output_file: str (file contains sorted suspiciousness lines file with date, author and recency)
    project: str (project name)
    bug: str (bug id) 
    formula: str (fault localization technique)
    commit_id: str (commit id of the buggy vesion)

    """
   
    input_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file
    sorted_susp_lines = read_susp_lines_from_file(input_file)
    
    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + output_file

    dates = []

    for susp_line in sorted_susp_lines:
        date = susp_line[-1].strip()
        datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        bug_date = datetime_obj.date()
        dates.append(bug_date)

    no_of_days_elapsed = []

    for date in dates:
        no_of_days_elapsed.append((max(dates) - date).days)

    min_days = min(no_of_days_elapsed)
    max_days = max(no_of_days_elapsed)
    diff_days = max_days - min_days

    line_counter = 0

    for susp_line in sorted_susp_lines:
        if diff_days == 0:
            print("Divide by Zero: Max and Min are same")
            raise ValueError("ERROR: RARE CASE: All the dates are same")
        normalized_time = (no_of_days_elapsed[line_counter] - min_days)/diff_days
        recency = 1 - normalized_time      
        add_recency_to_file(output_file, susp_line, recency)
        line_counter += 1
        

def add_recency_to_file(output_file, susp_line, recency):
    """
    appends the author and date to the output file containing suspiciousness lines
    
    Paramaeters:
    ------------
    output_file: str 
    susp_line: str
    recency: str

    """
    susp_line = ", ".join(susp_line)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line}, {recency}\n")


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
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines   
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')

    args = parser.parse_args()

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        for bug in bugs:
            for formula in FORMULA:
                input_csv = f"{project}-{bug}-{formula}-sorted-susp-with-date"
                output_csv = f"{project}-{bug}-{formula}-sorted-susp-with-recency.csv"
                find_normalized_line_len(os.path.join(args.suspiciousness_data_dir, input_csv),
                     os.path.join(args.output_dir, output_csv), project, bug, formula)
