OBE Quiz Checker
Collective Assessment Alignment Overview and Graphical Analysis

OBE Quiz Checker is a Streamlit-based assessment analysis tool designed to help instructors, course coordinators, OBE coordinators, and academic quality teams evaluate assessment questions for alignment with Subject Relevance, Course Learning Outcomes (CLOs), Program Learning Outcomes (PLOs), and Bloom's Taxonomy.

The application supports diverse assessment formats and is not limited to MCQs. It can analyze MCQs, short-answer questions, conceptual questions, numerical problems, analytical questions, essay questions, application-based questions, evaluation questions, and design/create questions.

Purpose

The purpose of OBE Quiz Checker is to evaluate an entire assessment and provide a clear collective overview of its alignment.

The application evaluates each question independently and identifies:

Subject relevance
CLO alignment
PLO alignment
Intended Bloom level
Detected Bloom level
Bloom alignment
Overall alignment score
Alignment status

The tool then identifies questions with weak CLO, PLO, Bloom, or subject alignment and supports targeted question revision.

Main Workflow

Assessment Upload
↓
Question Extraction
↓
Complete Question-Level Evaluation
↓
Collective Metrics
↓
Graphical Analysis
↓
Weak CLO/PLO/Bloom Identification
↓
Question Revision
↓
Re-evaluation
↓
Before-and-After Comparison

Key Features
1. Multiple File Formats

The application supports:

PDF
DOCX
TXT
CSV
XLSX
XLS

PDF processing uses PyMuPDF as a primary PDF-reading library. OCR support is also available for scanned PDFs when the required OCR packages are installed.

2. Diverse Assessment Questions

The tool does not assume that every assessment is an MCQ.

It can process:

Multiple-choice questions
Short-answer questions
Conceptual questions
Numerical questions
Problem-solving questions
Analytical questions
Essay questions
Application-based questions
Evaluation questions
Design/create questions
3. Question Extraction

The application extracts actual assessment questions from uploaded files.

It attempts to ignore document metadata, dates, headings, and platform-generated information.

For example, content such as:

9/19/26, 5:27 AM
General Chemistry » QuestionWell
General Chemistry Question Set

should not be treated as assessment questions.

The objective is to analyze the actual assessment questions rather than document headings or metadata.

Assessment Alignment Metrics

Each question is evaluated independently using four major alignment areas:

Criterion	Weight
Subject Relevance	30%
CLO Alignment	25%
PLO Alignment	15%
Bloom Alignment	30%
Total	100%

Subject relevance is treated as an important alignment condition. A question should not receive a high alignment classification simply because its CLO, PLO, and Bloom characteristics appear appropriate if the question itself is not relevant to the selected subject.

Complete Metrics at the Start

The application should display the complete assessment metrics before the revision section.

For every question, the overview should include:

Question number
Subject relevance
CLO
CLO score
PLO
PLO score
Target Bloom level
Detected Bloom level
Bloom alignment score
Overall score
Alignment status

Example:

Question	Subject	CLO	CLO Score	PLO	PLO Score	Target Bloom	Detected Bloom	Bloom Score	Overall	Status
Q1	95	CLO1	92	PLO1	88	Apply	Apply	95	93	Aligned
Q2	90	CLO2	61	PLO2	85	Analyze	Understand	55	72	Needs Revision
Q3	94	CLO2	87	PLO3	52	Evaluate	Evaluate	96	78	Needs Revision
Q4	96	CLO3	91	PLO2	89	Apply	Apply	94	93	Aligned

This allows the instructor to see the complete assessment condition at a glance.

Question Scores Must Vary

Every question must be evaluated independently.

The application must not assign the same score to all questions simply because they belong to the same assessment.

For example, an assessment may produce:

Q1 → 94
Q2 → 78
Q3 → 86
Q4 → 61
Q5 → 91
Q6 → 73
Q7 → 88

This is preferable to giving every question the same score.

Score variation should reflect differences in:

Subject relevance
CLO alignment
PLO alignment
Bloom alignment
Overall evidence of alignment

The same principle applies after question revision. Revised questions should also receive independently calculated scores and should not all automatically receive the same score.

Weak Alignment Analysis

The application should not only provide an overall score.

It should identify exactly which alignment component is weak for each question.

For example:

Q2

Subject Relevance: 90
CLO Alignment: 61 — Weak
PLO Alignment: 85
Bloom Alignment: 55 — Weak
Overall Score: 72

The application should identify:

Q2 has weak CLO and Bloom alignment.

Another example:

Q3

Subject Relevance: 94
CLO Alignment: 87
PLO Alignment: 52 — Weak
Bloom Alignment: 96
Overall Score: 78

The application should identify:

Q3 has weak PLO alignment.

Alignment Classification

Individual component scores can be interpreted as:

80–100: Strong
60–79: Moderate
Below 60: Weak

A question may have a strong overall score while still having a weak individual component. The application should not hide such weaknesses.

For example:

Subject Relevance: 95
CLO Alignment: 55
PLO Alignment: 90
Bloom Alignment: 88

The application must still identify:

Weak CLO Alignment

CLO Weakness Analysis

The application should identify questions with weak CLO alignment.

Example:

Questions with Weak CLO Alignment:

Q2 → 54/100
Q7 → 48/100
Q11 → 57/100

This allows the instructor to focus revision efforts on questions that do not adequately assess the relevant CLO.

PLO Weakness Analysis

The application should separately identify questions with weak PLO alignment.

Example:

Questions with Weak PLO Alignment:

Q3 → 51/100
Q8 → 56/100
Q14 → 59/100

CLO and PLO weaknesses should be reported separately.

Bloom's Taxonomy

The application supports the six levels of Bloom's Taxonomy:

Remember
Understand
Apply
Analyze
Evaluate
Create

Examples of Bloom verbs include:

Remember: define, identify, list, state, recall

Understand: explain, describe, summarize, interpret

Apply: apply, calculate, solve, demonstrate

Analyze: analyze, examine, differentiate, compare

Evaluate: evaluate, justify, assess, critique

Create: design, develop, construct, formulate

The application compares the intended Bloom level with the cognitive level detected in the question.

Bloom Weakness Analysis

The application should identify questions where the detected cognitive level does not adequately match the intended Bloom level.

Example:

Q4

Target Bloom: Analyze
Detected Bloom: Understand
Bloom Score: 55

Another example:

Q9

Target Bloom: Evaluate
Detected Bloom: Remember
Bloom Score: 40

These questions can then be revised to better represent the intended cognitive level.

Collective Assessment Summary

At the beginning of the results section, the application should provide an assessment-level summary such as:

Total Questions: 20

Weak CLO Alignment: 4
Weak PLO Alignment: 3
Weak Bloom Alignment: 5
Weak Subject Relevance: 2
Questions Needing Revision: 6

This provides an immediate overview of the assessment.

Graphical Representation

The application should provide graphical analysis of the assessment, including:

Overall question alignment scores
CLO alignment by question
PLO alignment by question
Bloom alignment by question
Alignment distribution

The graphs should help instructors quickly identify patterns and weak areas across the assessment.

Question Revision

Questions that require revision can be revised within the application.

The revision should be based on the identified weakness.

If CLO alignment is weak, the question should be improved to better assess the intended CLO.

If PLO alignment is weak, the question should provide stronger evidence of the intended PLO.

If Bloom alignment is weak, the cognitive demand of the question should be improved to match the intended Bloom level.

If subject relevance is weak, the question should be revised to establish appropriate subject context.

CLO and PLO Must Not Be Written Inside Questions

CLOs and PLOs are alignment criteria and must not be inserted into student-facing assessment questions.

The application must not generate questions such as:

"CLO2: Analyze the following chemistry problem according to PLO2."

or:

"According to CLO2 and PLO2, explain the following concept."

Instead, the question should naturally assess the intended learning outcome.

For example:

"Calculate the concentration of a solution prepared by dissolving 5 g of sodium chloride in 250 mL of water. Show your calculations and explain the steps used."

The question assesses the intended learning outcome without explicitly mentioning the CLO or PLO.

CLO and PLO information should remain in the instructor-facing alignment analysis.

No Generic Question Suggestions

The application should provide an actual revised version of the original assessment question rather than only giving generic question suggestions.

The revision should preserve the original academic intent whenever possible while improving the identified alignment weakness.

Revised Question Evaluation

After revising a question, the instructor can test the revised version.

The application should calculate:

Revised subject relevance
Revised CLO alignment
Revised PLO alignment
Revised Bloom alignment
Revised overall score
Revised alignment status

If the revised question meets the required alignment threshold, the application should display:

Alignment is attained.

Before and After Comparison

The application should compare the original question with its revised version.

Example:

Metric	Before	After
Subject Relevance	90	96
CLO Alignment	55	88
PLO Alignment	82	91
Bloom Alignment	50	90
Overall Score	67	91

This allows the instructor to see which specific alignment areas improved.

Revised Scores Must Also Vary

Revised questions should not automatically receive identical scores.

For example:

Q1 → Before: 68 → After: 91
Q2 → Before: 74 → After: 86
Q3 → Before: 59 → After: 94
Q4 → Before: 77 → After: 88

The revised scores should continue to reflect differences between questions.

Reports

The application provides downloadable reports in:

CSV:

OBE_Quiz_Alignment_Report.csv

Excel:

OBE_Quiz_Alignment_Report.xlsx

These reports can support:

Course assessment review
Faculty coordination
Assessment moderation
OBE documentation
Accreditation documentation
Quality assurance
Departmental assessment review
User Interface
Sidebar

The sidebar contains:

Course / Subject
CLOs
PLOs
Intended Bloom Level
Main Dashboard

The main dashboard contains:

Assessment upload
Assessment evaluation
Complete metrics
Collective question overview
Graphical analysis
Weak CLO analysis
Weak PLO analysis
Weak Bloom analysis
Question revision
Revised-question testing
Before-and-after comparison
Report downloads
Technologies Used

The application is developed using:

Python
Streamlit
Pandas
PyMuPDF
PyPDF
PyPDF2
Python-DOCX
OpenPyXL
Pillow
Tesseract OCR
PDF2Image
