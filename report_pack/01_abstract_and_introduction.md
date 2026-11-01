# Chapter 1: Abstract and Introduction

This document provides the complete draft for the **Abstract** and **Chapter 1 (Introduction)** for the project report on the **"NLP-Based Campus Facility Feedback Analysis System"**.

---

## Abstract

*(Requirement: Strictly between 300 and 500 words, formatted to fit on a single page in Times New Roman 12 pt, 1.15 line spacing).*

Higher education institutions routinely collect large volumes of qualitative student feedback regarding campus infrastructure and support services. However, traditional feedback mechanisms rely on broad numerical satisfaction surveys that fail to capture specific complaints, or unorganized free-text comment boxes that require tedious manual inspection by college administrators. Furthermore, student comments in Indian colleges frequently feature informal phrasing, spelling errors, and bilingual code-mixing between English and Tamil (Tanglish), while occasionally containing offensive language that can distort institutional ratings. To resolve these challenges, this project presents an end-to-end Natural Language Processing (NLP) system designed to automatically analyze unstructured campus facility feedback. The system evaluates student opinions across eight key institutional facilities: canteen, classrooms, hostel mess, hostel rooms, computing and engineering laboratories, library, bus transport, and campus Wi-Fi. The pipeline operates in seven sequential stages. First, student comments undergo text preprocessing and clause-level segmentation to isolate distinct opinions within compound sentences. Second, an abusive-content detection gate powered by the pre-trained `unitary/toxic-bert` model flags and quarantines toxic remarks, achieving 88% precision, 90% recall, and an F1-score of 0.89 across 800 campus comments, thereby preserving data integrity. Third, an aspect extraction module combines domain keyword patterns with a multi-label DistilBERT model to identify forty-two specific facility aspects, achieving an F1-score of 0.742 on the test partition. Fourth, an aspect-based sentiment analysis classifier fine-tuned on the DistilBERT architecture evaluates the emotional polarity of each aspect within its immediate clause context, achieving a final test accuracy of 0.905 and a macro-F1 score of 0.875 across positive, neutral, and negative classes. Fifth, an aggregation engine converts polarities into standard 1.0 to 5.0 facility star ratings and automatically identifies sixteen chronic issues where negative sentiment exceeds seventy percent. Sixth, a localized large language model (LLaMA 3.1 served via Ollama) produces concise executive summaries constrained by strict factual verification checks to prevent fabricated statements. Finally, a fully offline, responsive web dashboard built with Flask and Chart.js allows administrators to explore facility trends, audit quarantined comments, and test live feedback. By automating the transition from raw text to structured ratings, chronic problem alerts, and factual executive briefs, the system provides educational leaders with actionable, transparent insights to enhance campus living standards without recurring operational costs.

*(Word count: 374 words — strictly compliant with the 300 to 500 words college requirement).*

---

## 1. Introduction

### 1.1 Background

Modern university campuses are complex ecosystems encompassing dining halls, academic classrooms, residential student dormitories, engineering and research laboratories, libraries, bus transportation fleets, and wireless networks. The overall quality of campus life and student academic success depends heavily on the reliability, cleanliness, and maintenance of these shared facilities. In an effort to maintain campus standards, colleges regularly collect student reviews and grievances.

In traditional academic environments, student feedback is typically gathered through paper-based questionnaires or rigid online rating forms consisting of standardized five-point Likert scales. While these survey forms are easy to aggregate mathematically, they suffer from significant limitations. Numerical scores provide no context regarding *why* students are dissatisfied. For example, giving a low score of two stars to a campus library does not explain whether the primary issue is noisy study areas, outdated textbooks, air conditioning failures, or restrictive weekend opening hours.

When colleges provide open-ended free-text feedback boxes to capture qualitative comments, administrators encounter a different bottleneck: **information overload**. Campus administrative teams receive hundreds or thousands of unorganized comments at the end of each semester. Reading and cataloging these comments manually requires substantial staff hours, introducing human fatigue and subjective bias. In addition, student feedback in Indian engineering colleges often features bilingual expressions blending English and Tamil (commonly known as *Tanglish*), informal student slang, irregular abbreviations (such as *"ac"* for air conditioning or *"wifi"* for wireless internet), and inconsistent spelling. Standard, off-the-shelf sentiment analysis tools trained on formal news articles or product reviews perform poorly on such localized language.

To bridge this gap, this project develops a specialized **Natural Language Processing (NLP)** pipeline. NLP is a branch of artificial intelligence that trains computers to understand, interpret, and process human text. By breaking down free-form student feedback into fine-grained topics and identifying student sentiment toward each specific topic, colleges can replace manual sorting with transparent, automated intelligence.

---

### 1.2 Motivations

The development of this automated feedback analysis system is driven by four practical motivations:

1. **Overcoming the "Single-Score Fallacy" through Aspect-Based Sentiment Analysis (ABSA)**:
   In real life, a student comment rarely expresses a single uniform sentiment. A student might write:
   > *"The food in the canteen is very tasty, but the waiting queue takes twenty minutes and the cashier is rude."*
   
   If a system assigns a single overall sentiment label to this sentence, it either misses the praise or ignores the two severe complaints. This project is motivated by the need for **Aspect-Based Sentiment Analysis (ABSA)**—an NLP technique that breaks a sentence into specific components (such as *food quality*, *waiting time*, and *staff behavior*) and predicts how the student feels about each component individually.

2. **Protecting Rating Integrity Against Abusive and Toxic Content**:
   Campus feedback portals occasionally receive comments containing offensive language, profanity, or inappropriate personal attacks against campus staff. If an angry comment full of insults is counted directly toward facility ratings, it can unfairly penalize employees or distort quantitative records. Conversely, completely discarding such comments without review prevents administrators from addressing serious behavioral issues. Therefore, an automated moderation gate is needed to flag toxic language, quarantine abusive comments into a protected inspection database, and exclude them from facility ratings.

3. **Handling Multilingual Campus Slang and Tanglish**:
   Students in Tamil Nadu engineering institutions regularly communicate using a blend of Tamil vocabulary transliterated into the Roman English alphabet (for example, words like *"nalla"* meaning good, *"mokka"* meaning dull or boring, *"semma"* meaning excellent, or *"thanni"* meaning water). Traditional sentiment dictionaries fail to recognize these dialectal terms. Designing an NLP pipeline with localized vocabulary support and sentence segmentation ensures that Indian college feedback is evaluated accurately without forcing students to write in stiff, formal English.

4. **Bridging the Gap Between Numbers and Executive Decisions**:
   College deans, hostel wardens, and estate managers do not have the time to browse through large spreadsheets of thousands of predictions. They require actionable executive summaries:
   - What is the overall rating of the facility on a familiar 1 to 5 star scale?
   - What specific areas have reached a critical negative threshold (e.g., more than 70% negative reviews)?
   - Can an artificial intelligence summarize these findings into a short, factual 3-sentence brief that can be quoted directly in campus management meetings?

---

### 1.3 Scope of the Project

To ensure engineering rigor and practical usability, the project boundary is defined by clear inclusions and exclusions:

#### What the System Covers:
- **Facilities Monitored (8 Core Campus Facilities)**:
  1. *Canteen* (food quality, price, hygiene, waiting time, seating, staff behavior, quantity, variety)
  2. *Classrooms* (air conditioning/temperature, cleanliness, lighting, noise, projector/AV, seating)
  3. *Hostel Mess* (food quality, price, hygiene, waiting time, seating, staff behavior, quantity, variety)
  4. *Hostel Rooms* (cleanliness, electricity, laundry, maintenance, noise, room size, safety, water supply)
  5. *Engineering & Computing Labs* (cleanliness, equipment condition, lab staff, lab timings, software availability, space, system speed)
  6. *Library* (air conditioning/temperature, book availability, cleanliness, digital resources, opening hours, seating, silence, staff behavior)
  7. *College Bus Transport* (bus condition, crowding, driver behavior, fare, punctuality, route coverage, safety)
  8. *Campus Wi-Fi / Internet* (bandwidth limit, connectivity, coverage, login issues, reliability, speed)
- **Granular Aspect Coverage**: Forty-two (42) predefined domain aspects mapped strictly across the eight facilities.
- **Three-Class Sentiment Polarity**: Classification of aspect sentiments into *Positive*, *Neutral*, and *Negative*.
- **Automated Abusive Content Detection**: Binary classification using a dedicated transformer model (`unitary/toxic-bert`) to quarantine toxic text.
- **Data-Driven Metric Aggregation**: Calculation of 1.0 to 5.0 star ratings per facility and per aspect, and automatic flagging of chronic recurring issues based on negative mention ratios.
- **Local AI Summary Generation**: Production of factual text summaries using a locally hosted Large Language Model (LLaMA 3.1 via Ollama) paired with an automated fact-checking gate to prevent hallucinated numbers.
- **User Presentation Layer**: A lightweight, fully offline web dashboard built with Flask and styled with responsive dark-theme CSS and Chart.js visualizations, alongside a Streamlit prototype dashboard.

#### What the System Does NOT Cover (Explicit Exclusions):
- **Academic and Faculty Performance Evaluation**: The system does not analyze teacher pedagogy, syllabus difficulty, exam grading, or course curricula. (The external EduRABSA dataset was utilized solely for transfer learning, not for production faculty evaluation).
- **Audio, Voice, or Image Processing**: The pipeline does not process audio recordings of complaints or photos of broken campus infrastructure. It focuses exclusively on text.
- **Personal Student Identity Profiling**: The system is completely anonymous. It does not collect student register numbers, names, IP addresses, or email credentials.
- **Real-Time Database Synchronization with University ERP**: The system currently runs as a standalone analytics platform reading from local storage files (`data/outputs/`) rather than modifying live college SQL databases or student management ERP backends.
