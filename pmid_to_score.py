# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:56:13 2021

@author: HCC604
"""

import sys

from ncbi_search import load_abstract
from UnifiedQA import preprocess_input, run_model

pmid_list = ['29744625', '30675655']
abstracts = load_abstract(pmid_list, separate_title=False)

sign_study_type = """
What type of study is this? \\n
(A) Meta-analysis
(B) Systematic review of randomized controlled trials
(C) Randomizec controlled trial
(D) Systematic review of case control / cohort studies
(E) A cohort study
(F) A case-control study
(G) A case series
(H) A case report
"""

for abstract in abstracts:
    abstract[1] = preprocess_input(abstract[1])
    print(abstract, file=sys.stderr)
    pred = run_model('What is this study about?' + '\\n' + abstract[1])
    print('Summary:', pred, file=sys.stderr)
    pred = run_model(sign_study_type + '\\n' + abstract[1])
    print('Inferred study type:', pred, file=sys.stderr)




