import argparse
import csv
import os
import math
from scipy import stats

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

def evaluate_algorithms(input_file_dstar2, input_file_addition, buggy_lines_file, output_file, top_N_lines, project, bug, formula):
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

    input_file_dstar2 = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file_dstar2
    input_file_addition = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + input_file_addition
    buggy_lines_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + buggy_lines_file
    sorted_susp_lines_dstar2 = read_susp_lines_from_file(input_file_dstar2)
    sorted_susp_lines_addition = read_susp_lines_from_file(input_file_addition)
    buggy_lines = read_susp_lines_from_file(buggy_lines_file)


    # output file
    output_file = "/home/kanag23/Desktop/Fault_loc/Python_scripts_July_25/" + output_file

    dcg_ideal = 0.0
    for i in range(top_N_lines):
        if i >= len(buggy_lines):
            break
        dcg_ideal += (2 ** 1 - 1) / math.log(i + 2, 2)

    dcg_dstar2 = 0.0
    for i in range(top_N_lines):
        # print(f"index: {i},   len(sorted_susp_lines_dstar2): {len(sorted_susp_lines_dstar2)}")
        is_found_dstar2 = find_if_predicted_line_is_buggy(sorted_susp_lines_dstar2[i], buggy_lines)
        dcg_dstar2 += (2 ** is_found_dstar2 - 1) / math.log(i + 2, 2)        # dcg formula
    ndcg_dstar2_value = dcg_dstar2 / dcg_ideal


    dcg_addition = 0.0
    for i in range(top_N_lines):
        # print(f"index: {i},   len(sorted_susp_lines_dstar2): {len(sorted_susp_lines_dstar2)}")
        is_found_addition = find_if_predicted_line_is_buggy(sorted_susp_lines_addition[i], buggy_lines)
        dcg_addition += (2 ** is_found_addition - 1) / math.log(i + 2, 2)   # dcg formula
    ndcg_dstar2_addition = dcg_addition / dcg_ideal

    return ndcg_dstar2_value, ndcg_dstar2_addition


def find_if_predicted_line_is_buggy(predicted_weighted_line, buggy_lines):
    for buggy_line in buggy_lines:
        buggy_line_parts = buggy_line[0].split('#')
        buggy_line_id = buggy_line_parts[0] + "#" + buggy_line_parts[1]
        if predicted_weighted_line[0] == buggy_line_id:
            return 1
    return 0


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


def wilcoxon_tests(ndcg_dstar2_for_each_bug, ndcg_new_for_each_bug):
    # WILCOXON TEST
    print("================ Stats Results Start: ====================")
    print(f"Length of ndcg_dstar2_for_each_bug: {len(ndcg_dstar2_for_each_bug)}")
    print(f"Values: {ndcg_dstar2_for_each_bug}")
    print(f"Length of ndcg_new_for_each_bug: {len(ndcg_new_for_each_bug)}")
    print(f"Values: {ndcg_new_for_each_bug}")

    print(stats.wilcoxon(ndcg_dstar2_for_each_bug, ndcg_new_for_each_bug))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--suspiciousness-data-dir', required=True, help='Suspiciousness data directory')
    parser.add_argument('-b', '--buggy-lines-dir', required=True, help='Buggy Lines data directory')
    parser.add_argument('-o', '--output-dir', required=True, help='Output directory')

    args = parser.parse_args()

    # top_N_lines = [1, 3, 5, 10, 15, 20, 50]
    top_N_lines = [10]      # top 10 lines are only considered from the final recommended ranked lines

    # For stats test
    ndcg_dstar2_for_each_bug = []
    ndcg_new_for_each_bug = []


    print("\t\t\tdstar2 \t Product")

    for project, bugs in zip(PROJECTS, PROJECT_BUGS):
        # for susp_weight, recency_weight in [(0.5, 0.5), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 1.0)]:
        for susp_weight, recency_weight in [(0.9, 0.1)]:
            print(f"======= susp weight: {susp_weight} and recency_weight: {recency_weight}======")
            for top_N in top_N_lines:
                total_ndcg_dstar2, total_ndcg_addition = 0.0, 0.0



                for bug in bugs:
                    for formula in FORMULA:
                        input_csv_dstar2 = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency-{formula}-{susp_weight}-{recency_weight}"
                        input_csv_addition = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency-addition-{susp_weight}-{recency_weight}"
                        output_csv = f"{project}-{bug}-{formula}-sorted-weighted-susp-recency"
                        buggy_lines_csv = f"{project}-{bug}.buggy.lines"

                        # Calling the main functionality
                        ndcg_dstar2, ndcg_addition = evaluate_algorithms(os.path.join(args.suspiciousness_data_dir, input_csv_dstar2),
                                                                                                             os.path.join(args.suspiciousness_data_dir, input_csv_addition),
                                                                                                             os.path.join(args.buggy_lines_dir, buggy_lines_csv),
                                                                                                             os.path.join(args.output_dir, output_csv),
                                                                                                             top_N, project, bug, formula)
                        ndcg_dstar2_for_each_bug.append(ndcg_dstar2)
                        ndcg_new_for_each_bug.append(ndcg_addition)
                        total_ndcg_dstar2 += ndcg_dstar2
                        total_ndcg_addition += ndcg_addition


                # print(f"NDCG score for top {top_N}\t dstar2 \t\t\t addition")
                print(f"NDCG score for top {top_N}: \t\t\t\t\t{total_ndcg_dstar2:.4f} \t\t\t\t {total_ndcg_addition:.4f}", end="")
                if total_ndcg_dstar2 >= total_ndcg_addition:
                    print(f"\t\t\t dstar2")
                else:
                    print(f"\t\t\t addition")
                print(f"NDCG score for top {top_N}: \t\t\t\t\t{(total_ndcg_dstar2 / len(bugs)):.4f} \t\t\t\t {(total_ndcg_addition / len(bugs)):.4f}", end="")
                if (total_ndcg_dstar2 / len(bugs)) >= (total_ndcg_addition / len(bugs)):
                    print(f"\t\t\t dstar2")
                else:
                    print(f"\t\t\t addition")

                # print(f"Top {top_N} lines: \t {buggy_line_in_topN_dstar2_counter} \t\t\t {buggy_line_in_topN_addition_counter}", end="")
                # if buggy_line_in_topN_dstar2_counter > buggy_line_in_topN_addition_counter:
                #     print(f"\t\t dstar2")
                # else:
                #     print(f"\t\t Weighted Addition")
            print("===================\n\n")

    wilcoxon_tests(ndcg_dstar2_for_each_bug, ndcg_new_for_each_bug)

