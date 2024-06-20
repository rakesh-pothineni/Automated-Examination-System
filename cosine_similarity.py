# Load packages
import math
import nltk as nlp
import numpy as np
from nltk.corpus import stopwords

def find_mod_vector(vector):
    summ = 0
    for x in vector:
        summ += x**2
    return math.sqrt(summ)


def compute_vector(small_list, main_list):
    myvector = list()
    for i in range(len(main_list)):
        key = main_list[i]
        if key in small_list:
            myvector.append(1)
        else:
            myvector.append(0)
    return myvector


def get_vector(string_str):
    sentences = nlp.sent_tokenize(string_str)
    t_list = list()
    for s in sentences:
        temp = nlp.word_tokenize(s)
        for x in temp:
            t_list.append(x)
    return t_list


def evaluate_subj_answer(original_answer, user_answer):
    score_obt = 0
    
    orig_list = get_vector(original_answer)
    user_list = get_vector(user_answer)

    forig_list = [word for word in orig_list if word not in stopwords.words('english')]
    fuser_list = [word for word in user_list if word not in stopwords.words('english')]

    main_list = forig_list + fuser_list
    vector1 = compute_vector(forig_list, main_list)
    vector2 = compute_vector(fuser_list, main_list)

    v1 = find_mod_vector(vector1)
    v2 = find_mod_vector(vector2)

    v1_v2 = np.dot(vector1, vector2)

    dist = v1_v2 / (v1 * v2)
    score_obt = dist * 100

    return score_obt
