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


def compute_weighted_suspiciousness(input_file, output_file, project, bug, formula):
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
    compute_different_weights(sorted_susp_lines, 1.0, 1.0, output_file)
    compute_different_weights(sorted_susp_lines, 0.9, 0.1, output_file)
    compute_different_weights(sorted_susp_lines, 0.8, 0.2, output_file)
    compute_different_weights(sorted_susp_lines, 0.7, 0.3, output_file)
    compute_different_weights(sorted_susp_lines, 0.6, 0.4, output_file)
    compute_different_weights(sorted_susp_lines, 0.5, 0.5, output_file)

def compute_different_weights(sorted_susp_lines, susp_weight, recency_weight, output_file):
    output_file_temp = output_file + f"-dstar2-{susp_weight}-{recency_weight}"

    for susp_line in sorted_susp_lines:
        susp = susp_line[1].strip()
        recency = susp_line[5].strip()
        weighted_susp = combine_susp_recency_weigthed_addition(susp, recency, susp_weight, recency_weight)
        add_weighted_susp_to_file(output_file_temp, susp_line, weighted_susp)

    # sorting
    reader = csv.reader(open(output_file_temp), delimiter=',')
    sorted_list = sorted(reader, key=lambda row: row[-1], reverse=True)

    output_file += f'-addition-{susp_weight}-{recency_weight}'
    for sorted_line in sorted_list:
        write_sorted_list_to_file(output_file, sorted_line)


def combine_susp_recency_weigthed_addition(susp, recency, susp_weight, recency_weight):
    return susp_weight * float(susp) + recency_weight * float(recency)


def combine_susp_recency_product(susp, recency):
    return float(susp) * float(recency)


def write_sorted_list_to_file(output_file, susp_line_full):
    susp_line_full = ", ".join(susp_line_full)
    with open(output_file, mode="a", encoding="utf-8") as myFile:
        myFile.write(f"{susp_line_full}\n")


def add_weighted_susp_to_file(output_file, susp_line, recency):
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
                input_csv = f"{project}-{bug}-{formula}-sorted-susp-with-recency.csv"
                output_csv = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency"
                compute_weighted_suspiciousness(os.path.join(args.suspiciousness_data_dir, input_csv),
                     os.path.join(args.output_dir, output_csv), project, bug, formula)
