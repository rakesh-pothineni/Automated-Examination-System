# Import packages
import os
import csv
import numpy as np
import pandas as pd
from datetime import datetime
from atp.objective_question import ObjectiveQuestion

# Path for backup
subjective_path = str(os.getcwd()) + "/atp/static/data/db/user_data_log_subjective.csv"
objective_path = str(os.getcwd()) +  "/atp/static/data/db/user_data_log_objective.csv"


def back_up_data(username, subject_name, score_obt, flag):
    # Transform username and subject_name for backup
    username = "_".join([x.upper() for x in username.split()])
    subject_name = subject_name.strip().upper()
    
    if flag == "objective":
        filepath = objective_path
    else:
        filepath = subjective_path
    
    date = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year
    # Create a row for backup
    column_names = ["Date", "Month", "Year", "Username", "Subject", "Score"]
    row = [date, month, year, username, subject_name, score_obt] 
    try:
        with open(filepath,'a+',newline='') as fp:
            fp_writer = csv.writer(fp)
            fp_writer.writerow(row)
    except Exception as e:
        print(e)
    return True
    

def get_question_answer_pairs(pair, flag):
    if flag == "obj":
        length = 3
    elif flag == "subj":
        length = 2
    else:
        print("Error! Wrong `test_id` passed.")
        return None
    
    que = list()
    ans = list()

    while len(que) < length:
        rand_num = np.random.randint(0, len(pair))
        if pair[rand_num]["Question"] not in que:
            que.append(pair[rand_num]["Question"])
            ans.append(pair[rand_num]["Answer"])
        else:
            continue
    return que, ans


def generate_trivia(filename):
    questions = list()
    obj_a = ObjectiveQuestion(filename)
    questions.append(obj_a.generate_trivia_sentences())
    que_ans_pair = list()
    for lis in questions:
        for que in lis:
            if que["Anser_key"] > 3:
                que_ans_pair.append(que)
            else:
                continue
    return que_ans_pair


def relative_ranking(subjectname, flag):
    subjectname = subjectname.upper()
    max_score = 100
    min_score = 0
    mean_score = 66.2
    return max_score, mean_score, min_score