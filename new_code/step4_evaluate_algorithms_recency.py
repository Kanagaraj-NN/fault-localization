import argparse
import csv
import os
import datetime

# PROJECTS = ['Closure', 'Lang', 'Chart', 'Math', 'Mockito', 'Time']

PROJECTS = ['Math']

# PROJECT_BUGS = [
#     [str(x) for x in range(1, 134)],
#     [str(x) for x in range(1, 66)],
#     [str(x) for x in range(1, 27)],
#     [str(x) for x in range(1, 107)],
#     [str(x) for x in range(1, 39)],
#     [str(x) for x in range(1, 28)]
# ]

PROJECT_BUGS = [
     [str(x) for x in range(1, 107)]
     ]

#FORMULA = ['barinel', 'dstar2', 'jaccard', 'muse', 'ochiai', 'opt2', 'tarantula']
#FORMULA = ['tarantula']
FORMULA = ['dstar2']

def evaluate_algorithms(input_file_tarantula, input_file_product, buggy_lines_file, output_file, top_N_lines, project, bug, formula):
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

    input_file_tarantula = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file_tarantula
    input_file_product = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file_product
    buggy_lines_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + buggy_lines_file
    sorted_susp_lines_tarantulla = read_susp_lines_from_file(input_file_tarantula)
    sorted_susp_lines_product = read_susp_lines_from_file(input_file_product)
    buggy_lines = read_susp_lines_from_file(buggy_lines_file)


    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + output_file

    is_buggy_line_in_topN_tarantula = (False, 0)
    for buggy_line in buggy_lines:
        buggy_line_parts = buggy_line[0].split('#')
        buggy_line_id = buggy_line_parts[0] + "#" + buggy_line_parts[1]
        # if search_buggy_line_in_top_N(sorted_susp_lines_tarantulla, buggy_line_id, top_N_lines):
        #     is_buggy_line_in_topN_tarantula = True

        found, position = search_buggy_line_in_top_N(sorted_susp_lines_tarantulla, buggy_line_id, top_N_lines)
        if found:
            is_buggy_line_in_topN_tarantula = (True, position)




    # Search each buggy line in the product file
    is_buggy_line_in_topN_product = (False, 0)
    for buggy_line in buggy_lines:
        # buggy_line_path, line_number, code = buggy_line[0].split('#')
        # buggy_line_id = buggy_line_path + "#" + line_number
        buggy_line_parts = buggy_line[0].split('#')
        buggy_line_id = buggy_line_parts[0] + "#" + buggy_line_parts[1]
        # if search_buggy_line_in_top_N(sorted_susp_lines_product, buggy_line_id, top_N_lines):
        #     is_buggy_line_in_topN_product = True
        found, position = search_buggy_line_in_top_N(sorted_susp_lines_product, buggy_line_id, top_N_lines)
        if found:
            is_buggy_line_in_topN_product = (True, position)

    return is_buggy_line_in_topN_tarantula, is_buggy_line_in_topN_product


    # # sorting
    # reader = csv.reader(open(output_file), delimiter=',')
    # sorted_list = sorted(reader, key=lambda row: row[-1], reverse=True)
    #
    #
    # output_file += '-product'
    # for sorted_line in sorted_list:
    #     write_sorted_list_to_file(output_file, sorted_line)


def search_buggy_line_in_top_N_old(buggy_lines, search_line, top_N_lines):

    for i, buggy_line in enumerate(buggy_lines):
        buggy_line_path, line_number, code = buggy_line[0].split('#')
        buggy_line_id = buggy_line_path + "#" + line_number
        # print(buggy_line_id)
        if search_line == buggy_line_id:
            return True
        if i >= top_N_lines:
            return False

    return False


def search_buggy_line_in_top_N(susp_lines, buggy_line, top_N_lines):

    for i, susp_line in enumerate(susp_lines):
        if i >= top_N_lines:
            return False, i     # i is returned to find the position
        if buggy_line == susp_line[0]:
            # Found the bug
            return True, i

    return False, i


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
    susp_data = csv.reader(open(input_file, encoding="latin-1"), delimiter=',')
    sorted_susp_lines = [susp_line for susp_line in susp_data]
    
    return sorted_susp_lines   
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-b', '--buggy-lines-dir', required=True, help='Buggy Lines data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')

    args = parser.parse_args()

    # top_N_lines = [1, 5, 10, 20, 50, 100, 200, 500, 1000]
    top_N_lines = [1000]
    bug_found_position_dstar2 = []
    bug_found_position_new_tech = []


    print("\t\t\tdstar2 \t Product")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        # for susp_weight, recency_weight in [(0.5, 0.5), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 1.0)]:
        for susp_weight, recency_weight in [(0.9, 0.1)]:
            print(f"======= susp weight: {susp_weight} and recency_weight: {recency_weight}======")
            for top_N in top_N_lines:
                buggy_line_in_topN_tarantula_counter = 0
                buggy_line_in_topN_product_counter = 0
                for bug in bugs:
                    for formula in FORMULA:
                        input_csv_tarantula = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency-{formula}-{susp_weight}-{recency_weight}"
                        input_csv_addition = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency-addition-{susp_weight}-{recency_weight}"
                        output_csv = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency"
                        buggy_lines_csv = f"{project}-{bug}.buggy.lines"

                        # Calling the main functionality
                        is_buggy_line_in_topN_tarantula, is_buggy_line_in_topN_product = evaluate_algorithms(os.path.join(args.suspiciousness_data_dir, input_csv_tarantula),
                                                                                                             os.path.join(args.suspiciousness_data_dir, input_csv_addition),
                                                                                                             os.path.join(args.buggy_lines_dir, buggy_lines_csv),
                                                                                                             os.path.join(args.output_dir, output_csv),
                                                                                                             top_N, project, bug, formula)

                        bug_found_position_dstar2.append(is_buggy_line_in_topN_tarantula[1])
                        bug_found_position_new_tech.append(is_buggy_line_in_topN_product[1])

                        if is_buggy_line_in_topN_tarantula[0]:
                            buggy_line_in_topN_tarantula_counter += 1
                        if is_buggy_line_in_topN_product[0]:
                            buggy_line_in_topN_product_counter += 1
                # print(f"Project {project} : Top {top_N} line: Tarantula Counter: {buggy_line_in_topN_tarantula_counter}\{len(bugs)}")
                # print(f"Project {project} : Top {top_N} line: Product Counter: {buggy_line_in_topN_product_counter}\{len(bugs)}")

                print(f"Top {top_N} lines: \t {buggy_line_in_topN_tarantula_counter} \t\t\t {buggy_line_in_topN_product_counter}", end="")
                if buggy_line_in_topN_tarantula_counter >= buggy_line_in_topN_product_counter:
                    print(f"\t\t dstar2")
                else:
                    print(f"\t\t Weighted Addition")
            print("===================\n\n")

    print(f"Project names is {project}")
    print("bug_found_position_dstar2")
    print(bug_found_position_dstar2)
    print("bug_found_position_new_tech")
    print(bug_found_position_new_tech)

    bug_found_position_dstar2.sort()
    bug_found_position_new_tech.sort()

    print("After sorting")
    print("bug_found_position_dstar2")
    print(bug_found_position_dstar2)
    print("bug_found_position_new_tech")
    print(bug_found_position_new_tech)

    print("After Removing zeros")
    print("bug_found_position_dstar2")
    print(bug_found_position_dstar2)
    print("bug_found_position_new_tech")
    print(bug_found_position_new_tech)

    # Remove zeros
    bug_found_position_dstar2 = [val for val in bug_found_position_dstar2 if val != 0]
    bug_found_position_new_tech = [val for val in bug_found_position_new_tech if val != 0]

    print("After Removing zeros")
    print("bug_found_position_dstar2")
    print(bug_found_position_dstar2)
    print("bug_found_position_new_tech")
    print(bug_found_position_new_tech)

    print("======MEDIAN=========")
    print(f"Number of bugs found: {len(bug_found_position_dstar2)}")
    print(f"Number of bugs found: {len(bug_found_position_new_tech)}")
    print(bug_found_position_dstar2[len(bug_found_position_dstar2) // 2])
    print(bug_found_position_new_tech[len(bug_found_position_new_tech) // 2])


