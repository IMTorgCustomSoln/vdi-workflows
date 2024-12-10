#!/usr/bin/env python3
"""
Module Docstring

"""
import torch

from pathlib import Path
import sys
import json

#from src.modules import config_env

#sys.path.append(Path('config').absolute().as_posix() )
from config._constants import (
    logger
)
#TODO: logger.info("Begin prepare_models")


def finetune(config):
    """..."""

    #config_env.config()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f'finetune() using device: {device}')
    wdir = config['TRAINING_DATA_DIR']
    if not wdir.is_dir():
        logger.info(f'model data working dir is not available: {wdir}')
        return False

    #load model
    from setfit import SetFitModel
    load_foundation_model_path = "BAAI/bge-small-en-v1.5"
    save_finetuned_model_path = "pretrained_models/finetuned--BAAI"
    model = SetFitModel.from_pretrained(load_foundation_model_path)
    model.to(device)
    model.labels = ["negative", "positive"]

    #get records for train / test 
    from datasets import load_dataset, Dataset
    path_tng_records = wdir / 'train.json'
    path_tng_pos_sent = wdir / 'pos_sentence.txt'
    path_tng_neg_sent = wdir / 'neg_sentence.txt'
    path_test_records = wdir / 'test.json'

    if path_tng_records.is_file():
        with open(path_tng_records, 'r') as file:
            train_records = json.load(file)['records']
        #train_dataset = load_dataset(records)         #<<<FAILS HERE, maybe use this: Dataset.from_dict(
    else:
        logger.info(f'no training records available to refine model: {path_tng_records}')
        return False
    
    if path_tng_pos_sent:
        with open(path_tng_pos_sent, 'r') as file:
            train_lines = file.readlines()
        recs = [{'text':line.replace('\n',''), 'label':'positive'} for line in train_lines]
        train_records.extend(recs)

    if path_tng_neg_sent.is_file():
        with open(path_tng_neg_sent, 'r') as file:
            train_lines = file.readlines()
        recs = [{'text':line.replace('\n',''), 'label':'negative'} for line in train_lines]
        train_records.extend(recs)
    train_dataset = Dataset.from_list(train_records)        #[:10])     #<<<for testing

    if path_test_records.is_file():
        with open(path_test_records, 'r') as file:
            test_records = json.load(file)['records']
        test_dataset = Dataset.from_list(test_records)

    #train model
    from setfit import Trainer, TrainingArguments
    args = TrainingArguments(
        batch_size=25,
        num_epochs=10,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
    )
    trainer.train()

    #test model
    metrics = trainer.evaluate(test_dataset)
    print(metrics)
    '''
    preds = model.predict([
        "I got the flu and felt very bad.",
        "I got a raise and feel great.",
        "This bank is awful.",
        ])
    print(f'predictions: {preds}')
    '''

    #save model
    model_path = Path(save_finetuned_model_path)
    model.save_pretrained(model_path )
    model2 = SetFitModel.from_pretrained(model_path )
    result = True
    if not model2:
        result = False
    return result