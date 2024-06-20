# Import packages
import os
import click
import flask
import csv
import pandas as pd
import numpy as np
from datetime import datetime
from flask import render_template, request
from werkzeug.utils import secure_filename
from atp import app
from atp.objective_question import ObjectiveQuestion
from atp.subjective_question import generate_subj_question
from atp.cosine_similarity import evaluate_subj_answer
from atp.util import generate_trivia, get_question_answer_pairs
from atp.util import relative_ranking, back_up_data

# Global placehodlers
global_name_list = list()
global_answer_list = list()
global_test_id = list()
store_name = list()
user_path = str(os.getcwd()) +  "/atp/static/data/db/user_log.csv"

@app.route('/')
@app.route('/home', methods=['GET','POST'])
def home():
    ''' Renders the home page '''
    return render_template(
        "index.html",
        date=datetime.now().day,
        month=datetime.now().month,
        year=datetime.now().year
    )


@app.route("/form", methods=['GET', 'POST'])
def form():
    ''' Prompt user to start the test '''
    global_name_list.clear()
    user_name = request.form["username"]
    pswd = request.form["password"]

    flag = 0
    
    with open(user_path, mode = "r") as fp:
        fp_reader = csv.reader(fp)
        next(fp)
        for line in fp_reader:
            if not len(line):
                break
            if line[1] == user_name and line[2] == pswd:
                flag=1
                break
    
    if flag == 1:
        global_name_list.append(user_name)
        return render_template(
            "form.html",
            username = user_name
        )
    else:
        message = "Either the username or the password is invalid"
        return render_template(
            "loginutil.html",
            result = message
        )
    


@app.route("/validate", methods=['GET','POST'])
def validate():
    ''' Prompt the validation of the registration form'''
    flag = 0
    full_name = request.form["fullname"]
    user_name = request.form["username"]
    password = request.form["password"]
    with open(user_path, mode = "r") as fp:
        fp_reader = csv.reader(fp)
        next(fp)
        for line in fp_reader:
            if not len(line):
                break
            if line[1] == user_name:
                flag=1
                break

    if flag == 0:
        row = [full_name,user_name,password]
        try:
            with open(user_path, 'a+',newline='') as fp:
                fp_writer = csv.writer(fp)
                fp_writer.writerow(row)

        except Exception as e:
            print(e)

    message = ""
    if flag == 0:
        message = "Registration successful! Welcome to the application!"
    else:
        message = "A user with the provided username already exists!"

    return render_template(
        "validation.html",
        result = message
    )

@app.route("/register", methods=['GET','POST'])
def register():
    ''' Prompt the user to register for the test'''    
    return render_template(
        "registration.html"
    )


@app.route("/generate_test", methods=['GET', 'POST'])
def generate_test():
    subject_id = request.form["subject_id"]
    if subject_id == "se":
        global_name_list.append("Software Testing")
        filename = str(os.getcwd()) + "/sample_test_data/software-testing.txt"
        print(filename)
    elif subject_id == "db":
        global_name_list.append("DBMS")
        filename = str(os.getcwd()) + "/sample_test_data/dbms.txt"
    elif subject_id == "ml":
        global_name_list.append("ML")
        filename = str(os.getcwd()) + "/sample_test_data/ml.txt"
    elif subject_id == "custom":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(secure_filename(file.filename))
        global_name_list.append("Custom")
    else:
        print("Error! Wrong `subject_id` received from the HTML form.")
        return None

    test_id = request.form["test_id"]
    global_test_id.append(test_id)

    if test_id == "obj":
        que_ans_pair = generate_trivia(filename)
        question_list, answer_list = get_question_answer_pairs(que_ans_pair, test_id)
        for ans in answer_list:
            global_answer_list.append(ans)

        return render_template(
            "objective_test.html",
            username=global_name_list[0],
            testname=global_name_list[1],
            question1=question_list[0],
            question2=question_list[1],
            question3=question_list[2]
        )
    elif test_id == "subj":
        que_ans_pair = generate_subj_question(filename)
        question_list, answer_list = get_question_answer_pairs(que_ans_pair, test_id)
        for ans in answer_list:
            global_answer_list.append(ans)

        return render_template(
            "subjective_test.html",
            username=global_name_list[0],
            testname=global_name_list[1],
            question1=question_list[0],
            question2=question_list[1]
        )
    else:
        print("Error! Wrong `test_id` received from the HTML form.")
        return None

@app.route("/retest", methods=["GET","POST"])
def retest():
    global_name_list.append(store_name[0])
    return render_template(
        "form.html",
        username = store_name[0]
    )

@app.route("/output", methods=["GET", "POST"])
def output():
    default_ans = list()
    user_ans = list()
    if global_test_id[0] == "obj":
        # Access objective answers
        user_ans.append(str(request.form["answer1"]).strip().upper())
        user_ans.append(str(request.form["answer2"]).strip().upper())
        user_ans.append(str(request.form["answer3"]).strip().upper())
    elif global_test_id[0] == "subj":
        # Access subjective answers
        user_ans.append(str(request.form["answer1"]).strip().upper())
        user_ans.append(str(request.form["answer2"]).strip().upper())
    else:
        print("Error! Wrong `test_id` found in `global_test_id`!!")
    
    for x in global_answer_list:
        default_ans.append(str(x).strip().upper())
    
    username = global_name_list[0]
    subjectname = global_name_list[1]

    # Evaluate the user repsonse
    total_score = 0
    flag = ""
    if global_test_id[0] == "obj":
        flag = "objective"
        # evaluate objective answer
        for i in range(len(user_ans)):
            if user_ans[i] == default_ans[i]:
                total_score += 100
        total_score /= 3
        total_score = round(total_score, 3)
        # back up the user details and score for rank analysis
        score_status = "Failed to save your score!"
        if back_up_data(username, subjectname, total_score, flag):
            score_status = "Your score has been saved!"
    elif global_test_id[0] == "subj":
        flag = "subjective"
        # evaluate subjective answer
        for i in range(len(default_ans)):
            temp_score = evaluate_subj_answer(default_ans[i], user_ans[i])
            if np.isnan(temp_score):
                temp_score=0.0
            total_score+=temp_score
        total_score /= 2
        total_score = round(total_score, 3)
        if np.isnan(total_score):
            total_score=0.0
        # back up the user details and score for rank analysis
        score_status = "Failed to save your score!"
        if back_up_data(username, subjectname, total_score, flag):
            score_status = "Your score has been saved!"

    max_score, mean_score, min_score = relative_ranking(subjectname, flag)
    store_name.clear()
    store_name.append(global_name_list[0])

    # Clear the global variables for next instance
    global_name_list.clear()
    global_answer_list.clear()
    global_test_id.clear()
    global_test_id.clear()
    user_ans.clear()
    default_ans.clear()

    return render_template(
        "output.html",
        show_score=total_score,
        username=username,
        subjectname=subjectname,
        status=score_status,
        max_score=max_score,
        mean_score=mean_score,
        min_score=min_score
    )