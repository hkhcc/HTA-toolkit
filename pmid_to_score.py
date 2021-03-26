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

for abstract in abstracts:
    abstract[1] = preprocess_input(abstract[1])
    print(abstract, file=sys.stderr)
    pred = run_model('What is this study about?' + '\\n' + abstract[1])
    print('Summary:', pred, file=sys.stderr)
    pred = run_model('Is this a meta-analysis or systematic review or randomized controlled trial?' + '\\n' + abstract[1])
    print('Grade 1:', pred, file=sys.stderr)
    pred = run_model('Is this a case-control study?' + '\\n' + abstract[1])
    print('Grade 2 (case-control):', pred, file=sys.stderr)
    pred = run_model('Is this a cohort study?' + '\\n' + abstract[1])
    print('Grade 2 (cohort):', pred, file=sys.stderr)
    pred = run_model('Is this a case series or case report?' + '\\n' + abstract[1])
    print('Grade 3:', pred, file=sys.stderr)



