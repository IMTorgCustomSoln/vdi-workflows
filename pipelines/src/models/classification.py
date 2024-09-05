#!/usr/bin/env python3
"""
Module Docstring

"""

#TODO:from nltk.tokenize import word_tokenize 

import torch
#from transformers import AutoModel
from setfit import SetFitModel

from pathlib import Path
import copy


#load models
#config_env.config()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_path = Path("pretrained_models/finetuned--BAAI")
model = SetFitModel.from_pretrained(model_path)
model.to(device)




class Classifier:
    """..."""
    def __init__(self):
        pass
    
    def config(self, config):
        self.config = copy.deepcopy(config)
        self.models = [
            kw_classifier,
            phrase_classifier,
            #fs_classifier
        ]
        with open(self.config['TRAINING_DATA_DIR'] / 'pos_kw.txt', 'r') as file:
            kw_lines = file.readlines()
        self.config['KEYWORDS'] = [ ' ' + word.replace('\n','') + ' ' for word in kw_lines]      #ensure spacing around word
        
    def run(self, chunk):
        """Importable function to run assigned models."""
        result = []
        for model in self.models:
            result.append( model(self.config, chunk) )
        return result
    

TextClassifier = Classifier()



def kw_classifier(config, chunk):
    """..."""
    result = {
        'search': 'KW',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    hits = []
    for word in config['KEYWORDS']:
        if word in chunk['text'].lower():
            hits.append(word)
    #words = word_tokenize(chunk['text'])
    if len(hits)>0:
            result['target'] = ' '.join(hits)       #TODO: provide formatted chunk['text']
            result['pred'] = len(hits) / len(chunk['text'])
            if 'timestamp' in chunk.keys():
                result['timestamp'] = chunk['timestamp']
            return result
    else:
        return None
    

def phrase_classifier(config, chunk):
    """..."""
    return None


def fs_classifier(config, chunk):
    """..."""
    result = {
        'search': 'FS',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    if len(chunk['text']) > 40:
        probs = model.predict_proba(chunk['text'])
        pos_idx = model.labels.index('positive')
        prob_positive = probs.tolist()[pos_idx]
        if prob_positive > .5:
            result['target'] = chunk['text']
            result['pred'] = prob_positive
            if 'timestamp' in chunk.keys():
                result['timestamp'] = chunk['timestamp']
            return result
    return None