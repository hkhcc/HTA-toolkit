# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:56:13 2021

@author: HCC604
"""

import sys

from ncbi_search import load_abstract
from UnifiedQA import preprocess_input, run_model

sign_grading_question = '''
What type of study is this? \n
1 Meta-analyses, systematic reviews of randomized controlled trials (RCTs), or RCTs
2 Systematic review of case control or cohort studies; case control or cohort studies
3 Case report or case series
4 Expert opinion
5 Cannot be determined
'''


pmid_list = ['29744625', '30675655']
abstracts = load_abstract(pmid_list, separate_title=False)

for abstract in abstracts:
    print(abstract, file=sys.stderr)
    pred = run_model(sign_grading_question + '\\n' + abstract[1])
    print('Prediction:', pred, file=sys.stderr)


