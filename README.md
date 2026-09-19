# 🎓 OBE Quiz Checker

### Collective Assessment Alignment Overview and Graphical Analysis

OBE Quiz Checker is a Streamlit-based assessment analysis tool designed to evaluate assessment questions for alignment with **Course Learning Outcomes (CLOs), Program Learning Outcomes (PLOs), subject relevance, and Bloom's Taxonomy**.

The tool supports different types of assessment questions and is not limited to MCQs. It can process questions from uploaded PDF, DOCX, TXT, CSV, and Excel files.

---

## 📌 Purpose

The purpose of OBE Quiz Checker is to help instructors and academic coordinators quickly review an assessment and identify whether its questions are appropriately aligned with:

- Course/Subject
- CLOs
- PLOs
- Bloom's Taxonomy
- Overall OBE assessment requirements

Instead of evaluating only individual question quality, the application provides a **collective overview of the assessment** through scores, tables, metrics, and graphical representations.

---

# ✨ Key Features

## 1. 📂 Multiple File Formats

The application can read assessment files in:

- PDF
- DOCX
- TXT
- CSV
- XLSX
- XLS

For PDF files, the application first attempts normal text extraction and can use OCR as a fallback when the PDF contains scanned pages.

---

## 2. 📝 Diverse Assessment Questions

The tool does not assume that every assessment is an MCQ quiz.

It can process:

- MCQs
- Short-answer questions
- Conceptual questions
- Numerical/problem-solving questions
- Analytical questions
- Essay questions
- Application-based questions
- Evaluation questions
- Design/creation questions

---

## 3. 🎯 Subject Relevance

The application checks whether questions are relevant to the selected course or subject.

For example:

**Selected Subject:**

> General Chemistry

The assessment questions are examined for evidence that they belong to the selected subject.

### Important Rule

Subject relevance acts as a **mandatory alignment condition**.

A question should not receive a high overall alignment score simply because its CLO, PLO, or Bloom characteristics appear suitable if the question itself is not relevant to the selected subject.

---

# 4. 🎯 CLO Alignment

Users can enter their Course Learning Outcomes (CLOs), for example:

```text
CLO1: Explain fundamental chemistry concepts.

CLO2: Apply chemical principles to solve problems.

CLO3: Analyze chemical reactions and experimental results.
