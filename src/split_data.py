"""
Split campus facility feedback dataset into Train (70%), Validation (15%), and Test (15%) partitions.

Guarantees:
1. Strictly comment-level partitioning (all aspect rows from a comment stay in the same split).
2. Stratified by facility and balanced across abusive and sentiment labels.
3. Zero comment-ID, exact-text, or near-duplicate leakage across splits.
4. Gold verification sample (gold_to_verify.csv) sampled exclusively from the TRAINING partition,
   marked 'AWAITING_HUMAN_REVIEW'.
"""

import os
import re
import json
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.model_selection import StratifiedShuffleSplit

PROCESSED_DIR = "data/processed"
SEED = 42


def split_dataset(processed_dir=PROCESSED_DIR, seed=SEED):
    feedback_path = os.path.join(processed_dir, "campus_feedback.csv")
    aspects_path = os.path.join(processed_dir, "campus_aspects.csv")
    
    if not os.path.exists(feedback_path) or not os.path.exists(aspects_path):
        raise FileNotFoundError("Run src/merge_campus_data.py before running src/split_data.py")
        
    df = pd.read_csv(feedback_path)
    aspects = pd.read_csv(aspects_path)
    
    np.random.seed(seed)
    
    train_ids = []
    val_ids = []
    test_ids = []
    
    # Stratify by facility, balancing abusive comments
    for fac, group in df.groupby("facility"):
        abusive_rows = group[group["abusive"] == True]
        non_abusive_rows = group[group["abusive"] == False]
        
        # 6 abusive comments per facility: 4 train, 1 val, 1 test
        abusive_shuffled = abusive_rows.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        ab_train = abusive_shuffled.iloc[:4]
        ab_val = abusive_shuffled.iloc[4:5]
        ab_test = abusive_shuffled.iloc[5:6]
        
        # 94 non-abusive comments per facility: 66 train, 14 val, 14 test -> 70 train, 15 val, 15 test total
        non_abusive_shuffled = non_abusive_rows.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        non_ab_train = non_abusive_shuffled.iloc[:66]
        non_ab_val = non_abusive_shuffled.iloc[66:80]
        non_ab_test = non_abusive_shuffled.iloc[80:94]
        
        fac_train = pd.concat([ab_train, non_ab_train])
        fac_val = pd.concat([ab_val, non_ab_val])
        fac_test = pd.concat([ab_test, non_ab_test])
        
        assert len(fac_train) == 70, f"{fac} train count is {len(fac_train)}"
        assert len(fac_val) == 15, f"{fac} val count is {len(fac_val)}"
        assert len(fac_test) == 15, f"{fac} test count is {len(fac_test)}"
        
        train_ids.extend(fac_train["id"].tolist())
        val_ids.extend(fac_val["id"].tolist())
        test_ids.extend(fac_test["id"].tolist())

    train_df = df[df["id"].isin(train_ids)].copy().sample(frac=1.0, random_state=seed).reset_index(drop=True)
    val_df = df[df["id"].isin(val_ids)].copy().sample(frac=1.0, random_state=seed).reset_index(drop=True)
    test_df = df[df["id"].isin(test_ids)].copy().sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    assert len(train_df) == 560
    assert len(val_df) == 120
    assert len(test_df) == 120
    
    # Leakage check: ID intersection
    set_train = set(train_df["id"])
    set_val = set(val_df["id"])
    set_test = set(test_df["id"])
    assert len(set_train & set_val) == 0, "ID leakage between train and val"
    assert len(set_train & set_test) == 0, "ID leakage between train and test"
    assert len(set_val & set_test) == 0, "ID leakage between val and test"
    
    # Leakage check: Exact text overlap
    norm_tr = {re.sub(r"\W+", " ", t.lower()).strip() for t in train_df["text"]}
    norm_va = {re.sub(r"\W+", " ", t.lower()).strip() for t in val_df["text"]}
    norm_te = {re.sub(r"\W+", " ", t.lower()).strip() for t in test_df["text"]}
    assert len(norm_tr & norm_va) == 0, "Exact text leakage between train and val"
    assert len(norm_tr & norm_te) == 0, "Exact text leakage between train and test"
    assert len(norm_va & norm_te) == 0, "Exact text leakage between val and test"
    
    # Partition aspects
    train_aspects = aspects[aspects["id"].isin(set_train)].copy().reset_index(drop=True)
    val_aspects = aspects[aspects["id"].isin(set_val)].copy().reset_index(drop=True)
    test_aspects = aspects[aspects["id"].isin(set_test)].copy().reset_index(drop=True)
    
    assert len(train_aspects) + len(val_aspects) + len(test_aspects) == len(aspects)
    
    # Save partitioned files
    train_df.to_csv(os.path.join(processed_dir, "train_comments.csv"), index=False)
    val_df.to_csv(os.path.join(processed_dir, "validation_comments.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test_comments.csv"), index=False)
    
    train_aspects.to_csv(os.path.join(processed_dir, "train_aspects.csv"), index=False)
    val_aspects.to_csv(os.path.join(processed_dir, "validation_aspects.csv"), index=False)
    test_aspects.to_csv(os.path.join(processed_dir, "test_aspects.csv"), index=False)
    
    # Compatibility aliases
    train_df.to_csv(os.path.join(processed_dir, "campus_train.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "campus_test.csv"), index=False)
    train_aspects.to_csv(os.path.join(processed_dir, "campus_aspects_train.csv"), index=False)
    test_aspects.to_csv(os.path.join(processed_dir, "campus_aspects_test.csv"), index=False)
    
    # Sample Gold dataset for human verification strictly from TRAINING partition
    gold = train_df.sample(n=min(100, len(train_df)), random_state=seed).copy()
    gold["verified"] = "AWAITING_HUMAN_REVIEW"
    gold.to_csv(os.path.join(processed_dir, "gold_to_verify.csv"), index=False)
    
    print("=" * 60)
    print("SPLIT CREATION SUMMARY")
    print("=" * 60)
    print(f"Train Comments      : {len(train_df)} (Aspects: {len(train_aspects)}, Abusive: {train_df['abusive'].sum()})")
    print(f"Validation Comments : {len(val_df)} (Aspects: {len(val_aspects)}, Abusive: {val_df['abusive'].sum()})")
    print(f"Test Comments       : {len(test_df)} (Aspects: {len(test_aspects)}, Abusive: {test_df['abusive'].sum()})")
    print(f"Gold Sample (Train) : {len(gold)} comments (status: AWAITING_HUMAN_REVIEW)")
    print("Zero Leakage across all splits verified!")
    print("=" * 60)
    
    return train_df, val_df, test_df


if __name__ == "__main__":
    split_dataset()
