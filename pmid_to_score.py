# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:56:13 2021

@author: HCC604
"""

import sys

import pandas as pd

from ncbi_search import load_abstract
from UnifiedQA import preprocess_input, run_model

pmid_list = ['29744625', '30675655']
abstracts = load_abstract(pmid_list, separate_title=False)

for abstract in abstracts:
    abstract[1] = preprocess_input(abstract[1])
    print(abstract, file=sys.stderr)
    questions = pd.read_excel('Questions_set1.xlsx', sheet_name='questions')
    for question_index, question_row in questions.iterrows():
        this_question = preprocess_input(question_row['#Question'])
        print(question_row['#Question'], ':', file=sys.stderr, end='')
        this_answer = run_model(this_question + ' \\n ' + abstract[1])
        print(this_answer, file=sys.stderr)
    




