# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 10:37:47 2021

@author: HCC604
"""
import sys
import pandas as pd

from transformers import AutoTokenizer, T5ForConditionalGeneration

def preprocess_input(input_string):
    """Lowercase and remove quotes"""
    output_string = str(input_string).lower()
    output_string = str(output_string).replace('"', '')
    output_string = str(output_string).replace("'", '')
    output_string = str(output_string).replace('\n', '')
    return output_string
    

def run_model(input_string, **generator_args):
    input_ids = tokenizer.encode(input_string, return_tensors="pt")
    res = model.generate(input_ids, **generator_args)
    return tokenizer.batch_decode(res, skip_special_tokens=True)

if __name__ == "__main__":
    # Load the model
    print('# Now loading the AI model...', file=sys.stderr)
    model_name = "allenai/unifiedqa-t5-large" # you can specify the model size here
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    # Now processing the articles
    print('# Now processing the journal article data...', file=sys.stderr)
    
    jo_input = pd.read_excel('Input.xlsx', sheet_name='jo_data')
    for article_index, article_row in jo_input.iterrows():
        this_entry = article_row['Article_title'] + ' ' + article_row['Article_abstract'] + ' '
        this_entry += 'Article source: ' + article_row['Article_citation']
        this_entry = preprocess_input(this_entry)
        print('==========', file=sys.stderr)
        print('Article:', article_row['Article_title'], file=sys.stderr)
        print('Source:', article_row['Article_citation'], file=sys.stderr)
        print('-----', file=sys.stderr)
        questions = pd.read_excel('Questions_set1.xlsx', sheet_name='questions')
        for question_index, question_row in questions.iterrows():
            this_question = preprocess_input(question_row['#Question'])
            print(question_row['#Question'], ':', file=sys.stderr, end='')
            this_answer = run_model(this_question + ' \\n ' + this_entry)
            print(this_answer, file=sys.stderr)
        