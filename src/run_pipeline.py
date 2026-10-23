"""
Master Reproducible Pipeline Runner for Campus Facility Feedback NLP System.

Executes and verifies:
1. Raw dataset validation (structural, schema, label whitelists, substring matching).
2. Merging raw data into comment-level (campus_feedback.csv) and aspect-level (campus_aspects.csv).
3. 70/15/15 Comment-level train/val/test split with zero leakage and facility/abuse stratification.
4. Gold human verification sample creation (sampled strictly from training).
5. External dataset adapters (EduRABSA, Jigsaw benchmark sample).
6. Comprehensive report, manifest, and distribution generation.

Usage:
    python src/run_pipeline.py
"""

import sys
import os
import subprocess
import time

def run_step(description, command):
    print(f"\n{'='*70}")
    print(f">> RUNNING STEP: {description}")
    print(f"   Command: {command}")
    print(f"{'='*70}")
    t0 = time.time()
    res = subprocess.run(command, shell=True)
    dt = time.time() - t0
    if res.returncode != 0:
        print(f"\n[X] FAILURE in step: {description} (exit code {res.returncode})")
        sys.exit(res.returncode)
    print(f"[OK] COMPLETED: {description} in {dt:.2f}s")

def main():
    print("=" * 70)
    print("CAMPUS FACILITY FEEDBACK NLP DATASET - MASTER PIPELINE EXECUTION")
    print("=" * 70)
    
    # Step 1: Pre-validation of raw data
    run_step("Raw Dataset Integrity & Schema Validation", "python src/validate_dataset.py")
    
    # Step 2: Merge raw data into processed comments and aspects
    run_step("Merge and Format Raw Data into Processed CSVs", "python src/merge_campus_data.py")
    
    # Step 3: Split into Train / Validation / Test partitions with Zero Leakage
    run_step("Stratified Train/Val/Test Split (70/15/15)", "python src/split_data.py")
    
    # Step 4: Run External Adapters (EduRABSA, Jigsaw)
    run_step("Process External Adapters (EduRABSA & Jigsaw)", "python src/adapters.py")
    
    # Step 5: Generate Quality Reports, Manifest, and Label Distributions
    run_step("Generate Manifest, Distribution, and Quality Reports", "python src/generate_reports.py")
    
    # Step 6: Post-pipeline comprehensive verification
    run_step("Final Pipeline Verification Check", "python src/validate_dataset.py")
    
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("All artifacts generated, verified, and ready for model training preparation.")
    print("=" * 70)

if __name__ == "__main__":
    main()
