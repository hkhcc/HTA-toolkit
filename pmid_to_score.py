# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:56:13 2021

@author: HCC604
"""

import sys

import pandas as pd

from ncbi_search import load_abstract
from UnifiedQA import preprocess_input, run_model



jo_input = pd.read_excel('PMID-Input.xlsx', sheet_name='jo_data')

# prepare the question list and output list
jo_output = jo_input.copy()
question_list = list()
questions = pd.read_excel('Questions_set1.xlsx', sheet_name='questions')
for question_index, question_row in questions.iterrows():
    question_list.append(question_row['#Question'])
    jo_output['Question ' + str(question_index + 1) + ": " + question_row['#Question'].split('\\n')[0].rstrip()] = ""

print(jo_output, file=sys.stderr)

for article_index, article_row in jo_input.iterrows():
    pubmed_data = load_abstract([str(article_row['PMID']), ])
    title_and_abstract = pubmed_data[0][1] + pubmed_data[0][2]
    
    for question_index, question in enumerate(question_list):
        print(question, ':', file=sys.stderr, end='')
        this_answer = run_model(question + ' \\n ' + title_and_abstract)
        print(this_answer, file=sys.stderr)        
        jo_output.at[article_index, 'Question ' + str(question_index + 1) + ": " + question.split('\\n')[0].rstrip()] = this_answer[0]

# output the Excel file
jo_output.to_excel('PMID-Output.xlsx', sheet_name='jo_analysis')




