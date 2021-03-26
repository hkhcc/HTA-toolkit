# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:56:13 2021

@author: HCC604
"""

import sys

from ncbi_search import load_abstract
from UnifiedQA import preprocess_input, run_model

sign_grading_question = '''
This paper is a _ \n
(A) Meta-analysis, systematic review of randomized controlled trials (RCTs), or randomized controlled trial
(B) Systematic review of case control or cohort studies; case control or cohort study
(C) Case report or case series
(D) Expert opinion
(E) Cannot be determined
'''


pmid_list = ['29744625', '30675655']
abstracts = load_abstract(pmid_list, separate_title=False)

for abstract in abstracts:
    print(abstract, file=sys.stderr)
    pred = run_model(preprocess_input(sign_grading_question) + '\\n' + preprocess_input(abstract[1]))
    print('Prediction:', pred, file=sys.stderr)


