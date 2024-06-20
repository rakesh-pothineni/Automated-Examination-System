# Load packages
import numpy as np
import nltk as nlp
from nltk.corpus import stopwords


# Question patterns
question_formats = [
    "Explain in detail ",
    "Define ",
    "Write a short note on ",
    "What do you mean by "
    ]


# Grammer to chunk keywords
grammer = r"""
    CHUNK:{<NN>+<NN>+}
    {<NN>+<NNP>+}
    {<NNP>+<NN>+}
    {<NNP>+<NNP>+}
    """


def generate_subj_question(filepath):
    # Open file and load data
    try:
        fp = open(filepath, mode="r")
        data = fp.read()
        fp.close()
    except FileNotFoundError as e:
        print(e)

    sentences = nlp.sent_tokenize(data)
    que_ans_dict = dict()

    # Train the regex parser on the above grammer
    cp = nlp.RegexpParser(grammer)

    # Select imp sentence to generate questions
    for sentence in sentences:
        tagged_words = nlp.pos_tag(nlp.word_tokenize(sentence))
        
        # Parse the words to select the imp keywords to generate questions
        tree = cp.parse(tagged_words)
        for subtree in tree.subtrees():
            if subtree.label() == "CHUNK":
                temp = ""
                # Traverse through the subtree
                for sub in subtree:
                    temp += sub[0]
                    temp += " "
                temp = temp.strip()
                temp = temp.upper()
                if temp not in que_ans_dict:
                    if len(nlp.word_tokenize(sentence)) > 20:
                        que_ans_dict[temp] = sentence
                else:
                    que_ans_dict[temp] += sentence
    # Get a list of all keywords
    keyword_list = list(que_ans_dict.keys())
    que_ans_pair2 = list()
    
    # Form questions
    for _ in range(3):
        rand_num = np.random.randint(0, len(keyword_list))
        selected_key = keyword_list[rand_num]
        answer = que_ans_dict[selected_key]
        # Get a question format
        rand_num %= 4
        que_format = question_formats[rand_num]
        question = que_format + selected_key + "."
        # Make a dictionary and append to the main list repo
        que_ans_pair2.append({"Question": question, "Answer": answer})
    return que_ans_pair2