# Project Report Preparation Pack: NLP-Based Campus Facility Feedback Analysis System

Welcome! This folder (`report_pack/`) contains all the factual raw material, draft sections, figures, data samples, and architectural diagrams you need to write our final project report for **M.Tech CSI4007: Natural Language Processing and Computational Linguistics (J Component)**.

Because you did not write the underlying code, everything in this pack is written in **simple, plain English** with technical terms explained in everyday language the very first time they appear. 

---

## 1. How This Pack Maps to the College Report Template

The college project report requires a fixed structure. Each markdown document in this folder directly feeds one or more sections of the final report:

| Report Section / Chapter | Corresponding File in this Pack | Key Content & Purpose |
|---|---|---|
| **Front Matter** | [`11_front_matter_lists.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/11_front_matter_lists.md) | Lists of Figures, Tables, Abbreviations (alphabetical), Symbols & Notations. |
| **Abstract** | [`01_abstract_and_introduction.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/01_abstract_and_introduction.md) | Single-page draft Abstract (300 to 500 words) using strictly real facts and numbers. |
| **Chapter 1: Introduction** | [`01_abstract_and_introduction.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/01_abstract_and_introduction.md) | 1.1 Background, 1.2 Motivations, 1.3 Scope (what the system covers vs excludes). |
| **Chapter 2: Project Description & Goals** | [`02_project_description_and_goals.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/02_project_description_and_goals.md) | 2.1 Literature Review topics, 2.2 Research Gap, 2.3 Objectives, 2.4 Problem Statement, 2.5 Chronological Project Plan. |
| **Chapter 3: Technical Specification** | [`03_technical_specification.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/03_technical_specification.md) | 3.1 Requirements (Functional & Non-Functional), 3.2 Feasibility (Technical, Economic, Social), 3.3 Hardware & Software Specs. |
| **Chapter 4: Design Approach & Details** | [`04_design_and_diagrams.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_design_and_diagrams.md) & [`04_diagrams/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/) | System Architecture, DFD Level 0 & Level 1, Use Case, Class Diagram, Sequence Diagram (Mermaid, PlantUML, and PNG). |
| **Chapter 5: Methodology and Testing** | [`05_methodology_and_testing.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/05_methodology_and_testing.md) | Detailed walkthrough of the 7 modules, dataset accounting, neutral data additions, model training, evaluation metrics, and edge test cases. |
| **Chapter 6: Project Demonstration** | [`06_project_demonstration.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/06_project_demonstration.md) | Tour of all 7 web application views, screenshot checklist, and step-by-step viva demo script. |
| **Chapter 7: Results and Discussion** | [`07_results_and_discussion.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/07_results_and_discussion.md) & [`12_figures/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/12_figures/) | Result tables, reconciliation of metrics, plain explanations, limitations, and zero-dollar cost analysis. |
| **Chapter 8: Conclusion & Future Work** | [`08_conclusion_and_future_work.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/08_conclusion_and_future_work.md) | Project summary, conclusions drawn from findings, and realistic future engineering work. |
| **Chapter 9: References** | [`09_references_and_links.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/09_references_and_links.md) | Official documentation links, datasets, pre-trained models, and verified tools used. Marked VERIFY BEFORE CITING. |
| **Appendix A: Sample Code** | [`10_appendix_a_sample_code.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/10_appendix_a_sample_code.md) | Short, clean code snippets from real repository files with line-by-line plain explanations. |
| **Formatting Rules** | [`13_formatting_rules.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/13_formatting_rules.md) | Official college formatting requirements (fonts, line spacing, margins, table/figure captions). |

---

## 2. Recommended Reading & Writing Order

To build a thorough understanding before writing, follow this sequence:

1. **Start with Overview**: Read [`01_abstract_and_introduction.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/01_abstract_and_introduction.md) and [`02_project_description_and_goals.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/02_project_description_and_goals.md) to understand why the system was created, what facilities it monitors, and the problem it solves.
2. **Understand the Mechanics**: Read [`05_methodology_and_testing.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/05_methodology_and_testing.md) to see how the 7 modules work together, why we upgraded each module from simple baselines to transformer models, and why neutral comments were added later.
3. **Examine the System Design**: Open [`04_design_and_diagrams.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_design_and_diagrams.md) and view the high-resolution images in [`04_diagrams/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/04_diagrams/) to visualize data flows and architecture.
4. **Inspect the Web App & Demo**: Read [`06_project_demonstration.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/06_project_demonstration.md) so you can describe the web dashboard and prepare for the project viva presentation.
5. **Review Numbers & Tables**: Read [`07_results_and_discussion.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/07_results_and_discussion.md) alongside the generated charts in [`12_figures/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/12_figures/) to write the analysis and conclusions.
6. **Assemble Front Matter & Appendix**: Use [`11_front_matter_lists.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/11_front_matter_lists.md), [`10_appendix_a_sample_code.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/10_appendix_a_sample_code.md), and [`13_formatting_rules.md`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/13_formatting_rules.md) to finalize the report document.

---

## 3. Ground Rules Followed in This Pack

- **Strictly Real Numbers**: Every number in these documents is pulled directly from actual project files, evaluation logs, or dataset CSVs. No number has been invented.
- **Discrepancies Clarified**: Where an earlier test showed 0.939 accuracy and 0.925 macro-F1 while the final test gave 0.905 accuracy and 0.875 macro-F1, both numbers are clearly explained with their exact sample sizes (132 aspects originally vs 147 aspects after neutral additions).
- **Clear Placeholders**: Personal identifying information (team member names, registration numbers, guide name) appears as clear placeholders like `[TEAM MEMBER 1]` and `[GUIDE NAME]`.
- **Zero Hallucinated Citations**: Only real datasets, libraries, and pre-trained models actually present in the code repository are cited. Any academic paper requiring full formal bibliographic reference lookup is flagged with `VERIFY BEFORE CITING`.
- **Self-Contained Data Samples**: Clean, small sample CSVs are available in [`report_pack/data_samples/`](file:///c:/Users/sowmy/OneDrive/Desktop/campus-feedback-nlp/report_pack/data_samples/) so you can check exact row contents without having to open large datasets.
