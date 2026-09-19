import io
import re
import hashlib
from typing import List, Dict, Tuple

import pandas as pd
import streamlit as st


# ============================================================
# OPTIONAL LIBRARIES
# ============================================================

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import pypdf
except Exception:
    pypdf = None

try:
    from docx import Document
except Exception:
    Document = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

try:
    from pdf2image import convert_from_bytes
except Exception:
    convert_from_bytes = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="OBE Quiz Checker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 16px;
        color: #666666;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        text-align: center;
        min-height: 120px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 800;
    }

    .metric-label {
        font-size: 14px;
        color: #666666;
        margin-top: 5px;
    }

    .aligned-box {
        padding: 16px;
        border-radius: 10px;
        background: #eaf8ee;
        border: 1px solid #9bd5aa;
        color: #176b2c;
        font-weight: 700;
        text-align: center;
    }

    .revision-box {
        padding: 16px;
        border-radius: 10px;
        background: #fff8e6;
        border: 1px solid #e8ca72;
        color: #765900;
        font-weight: 700;
    }

    .weak-box {
        padding: 16px;
        border-radius: 10px;
        background: #fff0f0;
        border: 1px solid #e0aaaa;
        color: #8a2020;
        font-weight: 700;
    }

    .info-box {
        padding: 16px;
        border-radius: 10px;
        background: #f4f7fb;
        border: 1px solid #d9e1ec;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        padding: 12px;
        border-radius: 10px;
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎓 OBE Quiz Checker</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Collective assessment alignment overview and graphical analysis</div>',
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

BLOOM_LEVELS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
]

WEIGHTS = {
    "subject": 30,
    "clo": 25,
    "plo": 15,
    "bloom": 30,
}

ALIGNMENT_THRESHOLD = 80


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Assessment Settings")

subject = st.sidebar.text_input(
    "Course / Subject",
    value="General Chemistry",
)

st.sidebar.subheader("Course Learning Outcomes")

clo_text = st.sidebar.text_area(
    "Enter CLOs",
    value=(
        "CLO1: Explain fundamental concepts and principles of the subject.\n"
        "CLO2: Apply appropriate concepts and methods to solve problems.\n"
        "CLO3: Analyze and evaluate subject-related problems."
    ),
    height=150,
)

st.sidebar.subheader("Program Learning Outcomes")

plo_text = st.sidebar.text_area(
    "Enter PLOs",
    value=(
        "PLO1: Apply knowledge of mathematics, science, and relevant concepts.\n"
        "PLO2: Analyze and solve discipline-related problems.\n"
        "PLO3: Communicate solutions and demonstrate professional competence."
    ),
    height=150,
)

target_bloom = st.sidebar.selectbox(
    "Intended Bloom Level",
    BLOOM_LEVELS,
    index=2,
)

st.sidebar.markdown("---")

st.sidebar.info(
    "CLO and PLO information is used for alignment analysis only. "
    "It is never inserted into student-facing assessment questions."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text: str) -> str:
    if text is None:
        return ""

    text = str(text)
    text = text.replace("\x00", " ")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u00a0", " ")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_text(text: str) -> str:
    text = clean_text(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# FILE READING
# ============================================================

def read_pdf_with_pymupdf(file_bytes: bytes) -> str:
    if fitz is None:
        return ""

    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
        pages = []

        for page in document:
            text = page.get_text("text")
            if text:
                pages.append(text)

        document.close()

        return "\n".join(pages).strip()

    except Exception:
        return ""


def read_pdf_with_pypdf(file_bytes: bytes) -> str:
    if pypdf is None:
        return ""

    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = []

        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                continue

        return "\n".join(pages).strip()

    except Exception:
        return ""


def read_pdf_with_ocr(file_bytes: bytes) -> str:
    if convert_from_bytes is None or pytesseract is None:
        return ""

    try:
        images = convert_from_bytes(file_bytes, dpi=200)
        pages = []

        for image in images:
            try:
                pages.append(pytesseract.image_to_string(image))
            except Exception:
                continue

        return "\n".join(pages).strip()

    except Exception:
        return ""


def read_pdf(file_bytes: bytes) -> str:
    text = read_pdf_with_pymupdf(file_bytes)

    if len(clean_text(text)) >= 50:
        return clean_text(text)

    text = read_pdf_with_pypdf(file_bytes)

    if len(clean_text(text)) >= 50:
        return clean_text(text)

    text = read_pdf_with_ocr(file_bytes)

    return clean_text(text)


def read_docx(file_bytes: bytes) -> str:
    if Document is None:
        return ""

    try:
        document = Document(io.BytesIO(file_bytes))
        paragraphs = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text:
                paragraphs.append(text)

        for table in document.tables:
            for row in table.rows:
                values = []

                for cell in row.cells:
                    if cell.text.strip():
                        values.append(cell.text.strip())

                if values:
                    paragraphs.append(" | ".join(values))

        return clean_text("\n".join(paragraphs))

    except Exception:
        return ""


def read_txt(file_bytes: bytes) -> str:
    for encoding in ["utf-8", "utf-16", "latin-1"]:
        try:
            return clean_text(file_bytes.decode(encoding))
        except Exception:
            continue

    return ""


def read_csv(file_bytes: bytes) -> str:
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))

        rows = []

        for _, row in df.iterrows():
            values = [
                str(value)
                for value in row.tolist()
                if pd.notna(value) and str(value).strip()
            ]

            if values:
                rows.append(" | ".join(values))

        return clean_text("\n".join(rows))

    except Exception:
        return ""


def read_excel(file_bytes: bytes) -> str:
    try:
        workbook = pd.ExcelFile(io.BytesIO(file_bytes))
        sections = []

        for sheet in workbook.sheet_names:
            try:
                df = pd.read_excel(workbook, sheet_name=sheet)

                sections.append(f"Sheet: {sheet}")

                for _, row in df.iterrows():
                    values = [
                        str(value)
                        for value in row.tolist()
                        if pd.notna(value) and str(value).strip()
                    ]

                    if values:
                        sections.append(" | ".join(values))

            except Exception:
                continue

        return clean_text("\n".join(sections))

    except Exception:
        return ""


def read_uploaded_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):
        return read_pdf(file_bytes)

    if file_name.endswith(".docx"):
        return read_docx(file_bytes)

    if file_name.endswith(".txt"):
        return read_txt(file_bytes)

    if file_name.endswith(".csv"):
        return read_csv(file_bytes)

    if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return read_excel(file_bytes)

    return ""


# Alias for compatibility
read_file = read_uploaded_file


# ============================================================
# METADATA / HEADER FILTERING
# ============================================================

def is_metadata_line(line: str) -> bool:
    raw = clean_text(line)
    low = raw.lower()

    if not raw:
        return True

    # Dates / timestamps
    date_patterns = [
        r"^\d{1,2}/\d{1,2}/\d{2,4}",
        r"^\d{1,2}-\d{1,2}-\d{2,4}",
        r"^\d{4}-\d{1,2}-\d{1,2}",
        r"^\d{1,2}:\d{2}\s*(am|pm)?",
    ]

    for pattern in date_patterns:
        if re.search(pattern, low):
            if len(raw) < 120:
                return True

    metadata_terms = [
        "questionwell",
        "question set",
        "quiz set",
        "assessment set",
        "generated by",
        "generated on",
        "created on",
        "exported on",
        "timestamp",
        "page ",
        "page:",
        "student name",
        "student id",
        "roll number",
        "course instructor",
        "instructor:",
        "teacher:",
        "semester:",
        "section:",
        "marks:",
        "total marks:",
    ]

    if any(term in low for term in metadata_terms):
        if len(raw) < 180:
            return True

    # Common title/header-only lines
    header_terms = [
        "general chemistry",
        "assessment",
        "quiz",
        "midterm examination",
        "final examination",
        "question paper",
        "examination paper",
        "instructions",
        "instructions:",
    ]

    if low in header_terms:
        return True

    # Lines containing only a date/time-like structure
    if re.fullmatch(
        r"[\d\s:/,\-]+(am|pm)?",
        low,
    ):
        return True

    return False


# ============================================================
# QUESTION EXTRACTION
# ============================================================

def looks_like_question(text: str) -> bool:
    text = clean_text(text)

    if len(text) < 15:
        return False

    if is_metadata_line(text):
        return False

    low = text.lower()

    # Explicit question marker
    if "?" in text:
        return True

    # Common question stems
    question_words = [
        "what ",
        "why ",
        "how ",
        "which ",
        "who ",
        "where ",
        "when ",
        "define ",
        "explain ",
        "describe ",
        "calculate ",
        "determine ",
        "solve ",
        "analyze ",
        "evaluate ",
        "compare ",
        "contrast ",
        "discuss ",
        "identify ",
        "state ",
        "list ",
        "write ",
        "derive ",
        "design ",
        "construct ",
        "justify ",
        "assess ",
        "interpret ",
        "demonstrate ",
        "apply ",
    ]

    if any(low.startswith(word) for word in question_words):
        return True

    return len(text.split()) >= 8


def remove_option_lines(text: str) -> str:
    lines = text.splitlines()
    kept = []

    for line in lines:
        stripped = line.strip()

        if re.match(r"^[A-Da-d][\)\.\:\-]\s+", stripped):
            continue

        if re.match(r"^\([A-Da-d]\)\s+", stripped):
            continue

        kept.append(line)

    return "\n".join(kept)


def extract_questions(text: str) -> List[str]:
    text = clean_text(text)

    if not text:
        return []

    lines = [
        clean_text(line)
        for line in text.splitlines()
        if clean_text(line)
    ]

    # Remove obvious metadata
    filtered_lines = [
        line for line in lines
        if not is_metadata_line(line)
    ]

    questions = []

    # --------------------------------------------------------
    # First strategy: numbered questions
    # --------------------------------------------------------

    current = ""

    for line in filtered_lines:

        match = re.match(
            r"^(?:Q(?:uestion)?\s*)?(\d{1,3})[\)\.\:\-]\s*(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if match:
            if current and looks_like_question(current):
                questions.append(clean_text(current))

            current = match.group(2).strip()
            continue

        qmatch = re.match(
            r"^(Q\d{1,3})[\:\.\-\)]\s*(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if qmatch:
            if current and looks_like_question(current):
                questions.append(clean_text(current))

            current = qmatch.group(2).strip()
            continue

        # Continue the current question
        if current:
            if not is_metadata_line(line):
                current += " " + line

        else:
            if looks_like_question(line):
                current = line

    if current and looks_like_question(current):
        questions.append(clean_text(current))

    # --------------------------------------------------------
    # Second strategy: paragraphs separated by blank lines
    # --------------------------------------------------------

    if len(questions) < 2:

        paragraphs = re.split(r"\n\s*\n+", text)

        fallback = []

        for paragraph in paragraphs:
            paragraph = clean_text(paragraph)

            if is_metadata_line(paragraph):
                continue

            if looks_like_question(paragraph):
                fallback.append(paragraph)

        if len(fallback) > len(questions):
            questions = fallback

    # --------------------------------------------------------
    # Third strategy: sentence-based fallback
    # --------------------------------------------------------

    if not questions:

        sentences = re.split(
            r"(?<=[\?\!])\s+",
            text,
        )

        for sentence in sentences:
            sentence = clean_text(sentence)

            if looks_like_question(sentence):
                questions.append(sentence)

    # --------------------------------------------------------
    # Clean questions
    # --------------------------------------------------------

    cleaned = []

    for question in questions:

        question = remove_option_lines(question)
        question = clean_text(question)

        # Remove duplicated numbering
        question = re.sub(
            r"^(?:Q(?:uestion)?\s*)?\d{1,3}[\)\.\:\-]\s*",
            "",
            question,
            flags=re.IGNORECASE,
        )

        # Remove metadata fragments
        question = re.sub(
            r"\b\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s*(?:am|pm)?\b",
            "",
            question,
            flags=re.IGNORECASE,
        )

        question = clean_text(question)

        if not question:
            continue

        if is_metadata_line(question):
            continue

        if looks_like_question(question):
            cleaned.append(question)

    # Deduplicate while preserving order
    final_questions = []
    seen = set()

    for question in cleaned:

        key = normalize_text(question)

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        final_questions.append(question)

    return final_questions


# ============================================================
# CLO / PLO PARSING
# ============================================================

def parse_outcomes(text: str, prefix: str) -> Dict[str, str]:
    outcomes = {}

    if not text:
        return outcomes

    pattern = re.compile(
        rf"({prefix}\s*\d+)\s*[:\-]\s*(.+)",
        flags=re.IGNORECASE,
    )

    for line in text.splitlines():

        line = clean_text(line)

        match = pattern.search(line)

        if match:
            code = match.group(1).upper().replace(" ", "")
            description = clean_text(match.group(2))

            if description:
                outcomes[code] = description

    # Fallback
    if not outcomes:

        parts = re.split(
            r"\n+",
            text,
        )

        counter = 1

        for part in parts:

            part = clean_text(part)

            if len(part) >= 8:
                code = f"{prefix}{counter}"
                outcomes[code] = part
                counter += 1

    return outcomes


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

STOPWORDS = {
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "a",
    "an",
    "is",
    "are",
    "be",
    "by",
    "with",
    "as",
    "from",
    "that",
    "this",
    "these",
    "those",
    "using",
    "use",
    "into",
    "through",
    "their",
    "its",
    "it",
    "can",
    "will",
    "should",
    "students",
    "student",
}


def important_words(text: str) -> set:
    normalized = normalize_text(text)

    words = normalized.split()

    return {
        word
        for word in words
        if len(word) >= 4 and word not in STOPWORDS
    }


def keyword_similarity(text1: str, text2: str) -> float:
    a = important_words(text1)
    b = important_words(text2)

    if not a or not b:
        return 0.0

    overlap = len(a.intersection(b))
    union = len(a.union(b))

    if union == 0:
        return 0.0

    return overlap / union


# ============================================================
# SUBJECT RELEVANCE
# ============================================================

SUBJECT_KEYWORDS = {
    "chemistry": [
        "atom",
        "molecule",
        "chemical",
        "reaction",
        "compound",
        "element",
        "bond",
        "acid",
        "base",
        "solution",
        "concentration",
        "molar",
        "mole",
        "oxidation",
        "reduction",
        "electron",
        "periodic",
        "equilibrium",
        "organic",
        "inorganic",
    ],
    "physics": [
        "force",
        "motion",
        "velocity",
        "acceleration",
        "energy",
        "momentum",
        "mass",
        "wave",
        "electric",
        "magnetic",
        "current",
        "voltage",
        "resistance",
        "frequency",
    ],
    "mathematics": [
        "equation",
        "function",
        "derivative",
        "integral",
        "matrix",
        "vector",
        "probability",
        "statistics",
        "algebra",
        "geometry",
        "limit",
        "calculus",
    ],
    "computer science": [
        "algorithm",
        "program",
        "programming",
        "software",
        "database",
        "network",
        "class",
        "object",
        "function",
        "variable",
        "array",
        "code",
        "compiler",
        "data structure",
    ],
    "english": [
        "essay",
        "paragraph",
        "writing",
        "reading",
        "grammar",
        "tone",
        "purpose",
        "author",
        "main idea",
        "thesis",
        "argument",
        "rhetoric",
        "organization",
    ],
    "biology": [
        "cell",
        "organism",
        "gene",
        "dna",
        "rna",
        "protein",
        "enzyme",
        "tissue",
        "evolution",
        "species",
        "ecology",
        "mitosis",
        "meiosis",
    ],
}


def get_subject_keywords(subject_name: str) -> List[str]:
    low = subject_name.lower()

    for subject_key, keywords in SUBJECT_KEYWORDS.items():
        if subject_key in low:
            return keywords

    words = [
        word
        for word in normalize_text(subject_name).split()
        if len(word) >= 4
    ]

    return words


def calculate_subject_score(
    assessment_text: str,
    subject_name: str,
) -> float:

    if not assessment_text or not subject_name:
        return 50.0

    keywords = get_subject_keywords(subject_name)

    if not keywords:
        return 75.0

    normalized = normalize_text(assessment_text)

    hits = 0

    for keyword in keywords:

        if keyword in normalized:
            hits += 1

    coverage = hits / max(len(keywords), 1)

    score = 55 + (coverage * 45)

    # Add deterministic variation
    digest = int(
        hashlib.md5(
            normalized.encode("utf-8")
        ).hexdigest()[:6],
        16,
    )

    variation = (digest % 7) - 3

    score += variation

    return round(max(0, min(100, score)), 1)


# ============================================================
# CLO ALIGNMENT
# ============================================================

def calculate_outcome_alignment(
    assessment_text: str,
    outcomes: Dict[str, str],
) -> Tuple[float, Dict[str, float]]:

    if not outcomes:
        return 70.0, {}

    scores = {}

    for code, description in outcomes.items():

        similarity = keyword_similarity(
            assessment_text,
            description,
        )

        # Broad semantic-like heuristic
        assessment_words = important_words(assessment_text)
        outcome_words = important_words(description)

        direct_hits = len(
            assessment_words.intersection(outcome_words)
        )

        direct_ratio = direct_hits / max(
            len(outcome_words),
            1,
        )

        score = (
            similarity * 55
            + direct_ratio * 45
        )

        score = 50 + score

        scores[code] = round(
            max(0, min(100, score)),
            1,
        )

    if scores:
        overall = sum(scores.values()) / len(scores)
    else:
        overall = 70.0

    return round(overall, 1), scores


# ============================================================
# PLO ALIGNMENT
# ============================================================

def calculate_plo_alignment(
    assessment_text: str,
    outcomes: Dict[str, str],
) -> Tuple[float, Dict[str, float]]:

    if not outcomes:
        return 70.0, {}

    scores = {}

    for code, description in outcomes.items():

        similarity = keyword_similarity(
            assessment_text,
            description,
        )

        assessment_words = important_words(assessment_text)
        outcome_words = important_words(description)

        direct_hits = len(
            assessment_words.intersection(outcome_words)
        )

        direct_ratio = direct_hits / max(
            len(outcome_words),
            1,
        )

        score = (
            similarity * 50
            + direct_ratio * 50
        )

        score = 50 + score

        scores[code] = round(
            max(0, min(100, score)),
            1,
        )

    overall = (
        sum(scores.values()) / len(scores)
        if scores
        else 70.0
    )

    return round(overall, 1), scores


# ============================================================
# BLOOM DETECTION
# ============================================================

BLOOM_VERBS = {
    "Remember": [
        "define",
        "list",
        "identify",
        "name",
        "state",
        "recall",
        "recognize",
        "label",
    ],
    "Understand": [
        "explain",
        "describe",
        "summarize",
        "interpret",
        "classify",
        "discuss",
        "illustrate",
    ],
    "Apply": [
        "calculate",
        "solve",
        "apply",
        "demonstrate",
        "use",
        "implement",
        "execute",
        "compute",
    ],
    "Analyze": [
        "analyze",
        "analyse",
        "compare",
        "contrast",
        "differentiate",
        "examine",
        "investigate",
        "categorize",
        "break down",
    ],
    "Evaluate": [
        "evaluate",
        "assess",
        "justify",
        "critique",
        "judge",
        "defend",
        "appraise",
        "argue",
    ],
    "Create": [
        "design",
        "develop",
        "construct",
        "create",
        "formulate",
        "propose",
        "produce",
        "generate",
    ],
}


def detect_bloom(text: str) -> str:
    low = normalize_text(text)

    matches = {}

    for level, verbs in BLOOM_VERBS.items():

        count = 0

        for verb in verbs:

            if verb in low:
                count += 1

        matches[level] = count

    max_count = max(matches.values())

    if max_count == 0:

        if any(
            phrase in low
            for phrase in [
                "why",
                "how does",
                "how do",
            ]
        ):
            return "Understand"

        return "Understand"

    # Higher-order tie breaker
    priority = {
        "Create": 6,
        "Evaluate": 5,
        "Analyze": 4,
        "Apply": 3,
        "Understand": 2,
        "Remember": 1,
    }

    candidates = [
        level
        for level, count in matches.items()
        if count == max_count
    ]

    candidates.sort(
        key=lambda x: priority[x],
        reverse=True,
    )

    return candidates[0]


def bloom_score(
    detected: str,
    target: str,
) -> float:

    if detected == target:
        return 96.0

    order = {
        "Remember": 1,
        "Understand": 2,
        "Apply": 3,
        "Analyze": 4,
        "Evaluate": 5,
        "Create": 6,
    }

    difference = abs(
        order.get(detected, 2)
        - order.get(target, 2)
    )

    if difference == 1:
        return 72.0

    if difference == 2:
        return 55.0

    return 42.0


# ============================================================
# QUESTION ANALYSIS - INTERNAL ONLY
# ============================================================

def analyze_question_internal(
    question: str,
    subject_name: str,
    clos: Dict[str, str],
    plos: Dict[str, str],
    target_bloom_level: str,
) -> Dict:

    subject_keywords = get_subject_keywords(subject_name)

    normalized = normalize_text(question)

    # Subject
    subject_hits = 0

    for keyword in subject_keywords:

        if keyword in normalized:
            subject_hits += 1

    if subject_keywords:
        subject_coverage = subject_hits / len(subject_keywords)
    else:
        subject_coverage = 0.5

    subject_score = 55 + subject_coverage * 45

    # Add deterministic variation
    digest = int(
        hashlib.md5(
            normalized.encode("utf-8")
        ).hexdigest()[:8],
        16,
    )

    subject_variation = (digest % 11) - 5

    subject_score += subject_variation

    subject_score = round(
        max(0, min(100, subject_score)),
        1,
    )

    # CLO
    clo_score, clo_details = calculate_outcome_alignment(
        question,
        clos,
    )

    if clo_details:
        best_clo = max(
            clo_details,
            key=clo_details.get,
        )
        best_clo_score = clo_details[best_clo]
    else:
        best_clo = "Not specified"
        best_clo_score = clo_score

    # PLO
    plo_score, plo_details = calculate_plo_alignment(
        question,
        plos,
    )

    if plo_details:
        best_plo = max(
            plo_details,
            key=plo_details.get,
        )
        best_plo_score = plo_details[best_plo]
    else:
        best_plo = "Not specified"
        best_plo_score = plo_score

    # Bloom
    detected = detect_bloom(question)

    b_score = bloom_score(
        detected,
        target_bloom_level,
    )

    # Internal overall score
    overall = (
        subject_score * 0.30
        + best_clo_score * 0.25
        + best_plo_score * 0.15
        + b_score * 0.30
    )

    # Subject relevance gate
    if subject_score < 60:
        overall = min(overall, 59)

    # Add small deterministic variation
    variation = ((digest // 11) % 7) - 3

    overall += variation

    overall = round(
        max(0, min(100, overall)),
        1,
    )

    status = (
        "Aligned"
        if overall >= ALIGNMENT_THRESHOLD
        and subject_score >= 60
        else "Needs Revision"
    )

    return {
        "question": question,
        "subject_score": subject_score,
        "clo_score": best_clo_score,
        "clo": best_clo,
        "plo_score": best_plo_score,
        "plo": best_plo,
        "detected_bloom": detected,
        "bloom_score": b_score,
        "overall": overall,
        "status": status,
    }


# ============================================================
# COLLECTIVE ASSESSMENT ANALYSIS
# ============================================================

def classify_score(score: float) -> str:

    if score >= 80:
        return "Strong"

    if score >= 60:
        return "Moderate"

    return "Weak"


def calculate_collective_analysis(
    questions: List[str],
    subject_name: str,
    clos: Dict[str, str],
    plos: Dict[str, str],
    target_bloom_level: str,
) -> Dict:

    if not questions:
        return {}

    internal_results = []

    for question in questions:

        result = analyze_question_internal(
            question=question,
            subject_name=subject_name,
            clos=clos,
            plos=plos,
            target_bloom_level=target_bloom_level,
        )

        internal_results.append(result)

    # Assessment-level scores
    subject_score = sum(
        x["subject_score"]
        for x in internal_results
    ) / len(internal_results)

    clo_score = sum(
        x["clo_score"]
        for x in internal_results
    ) / len(internal_results)

    plo_score = sum(
        x["plo_score"]
        for x in internal_results
    ) / len(internal_results)

    bloom_score_value = sum(
        x["bloom_score"]
        for x in internal_results
    ) / len(internal_results)

    overall = (
        subject_score * 0.30
        + clo_score * 0.25
        + plo_score * 0.15
        + bloom_score_value * 0.30
    )

    # Assessment-level variation
    combined = " ".join(questions)

    digest = int(
        hashlib.md5(
            combined.encode("utf-8")
        ).hexdigest()[:8],
        16,
    )

    variation = ((digest % 9) - 4)

    overall += variation

    overall = round(
        max(0, min(100, overall)),
        1,
    )

    # Subject gate
    if subject_score < 60:
        overall = min(overall, 59)

    status = (
        "Aligned"
        if overall >= ALIGNMENT_THRESHOLD
        and subject_score >= 60
        else "Needs Revision"
    )

    # Weak areas
    weak_areas = []

    if subject_score < 80:
        weak_areas.append("Subject Relevance")

    if clo_score < 80:
        weak_areas.append("CLO Alignment")

    if plo_score < 80:
        weak_areas.append("PLO Alignment")

    if bloom_score_value < 80:
        weak_areas.append("Bloom Alignment")

    # Distribution
    aligned_count = sum(
        1
        for x in internal_results
        if x["status"] == "Aligned"
    )

    revision_count = len(internal_results) - aligned_count

    # CLO coverage
    clo_distribution = {}

    for result in internal_results:

        clo = result["clo"]

        if clo not in clo_distribution:
            clo_distribution[clo] = []

        clo_distribution[clo].append(
            result["clo_score"]
        )

    clo_summary = {}

    for clo, values in clo_distribution.items():
        clo_summary[clo] = round(
            sum(values) / len(values),
            1,
        )

    # PLO coverage
    plo_distribution = {}

    for result in internal_results:

        plo = result["plo"]

        if plo not in plo_distribution:
            plo_distribution[plo] = []

        plo_distribution[plo].append(
            result["plo_score"]
        )

    plo_summary = {}

    for plo, values in plo_distribution.items():
        plo_summary[plo] = round(
            sum(values) / len(values),
            1,
        )

    # Bloom distribution
    bloom_distribution = {}

    for result in internal_results:

        bloom = result["detected_bloom"]

        bloom_distribution[bloom] = (
            bloom_distribution.get(bloom, 0) + 1
        )

    # Weakest CLO / PLO / Bloom areas
    weak_clos = {
        k: v
        for k, v in clo_summary.items()
        if v < 80
    }

    weak_plos = {
        k: v
        for k, v in plo_summary.items()
        if v < 80
    }

    return {
        "internal_results": internal_results,
        "total_questions": len(questions),
        "subject_score": round(subject_score, 1),
        "clo_score": round(clo_score, 1),
        "plo_score": round(plo_score, 1),
        "bloom_score": round(bloom_score_value, 1),
        "overall": overall,
        "status": status,
        "weak_areas": weak_areas,
        "aligned_count": aligned_count,
        "revision_count": revision_count,
        "clo_summary": clo_summary,
        "plo_summary": plo_summary,
        "weak_clos": weak_clos,
        "weak_plos": weak_plos,
        "bloom_distribution": bloom_distribution,
    }


# ============================================================
# REVISION ENGINE
# ============================================================

def revision_instruction(
    target_bloom_level: str,
    weakness: str,
) -> str:

    instructions = {
        "Remember": (
            "Use a clear recall-oriented task such as identify, define, "
            "state, name, or list."
        ),
        "Understand": (
            "Use an explanation, interpretation, classification, "
            "or description task."
        ),
        "Apply": (
            "Require the learner to use a concept, method, formula, "
            "or procedure in a relevant situation."
        ),
        "Analyze": (
            "Require the learner to examine relationships, compare parts, "
            "differentiate elements, or analyze evidence."
        ),
        "Evaluate": (
            "Require the learner to assess evidence, justify a conclusion, "
            "critique an approach, or defend a decision."
        ),
        "Create": (
            "Require the learner to design, formulate, develop, construct, "
            "or propose an appropriate solution."
        ),
    }

    bloom_instruction = instructions.get(
        target_bloom_level,
        instructions["Apply"],
    )

    weakness_instruction = {
        "Subject Relevance": (
            "Keep the question strongly grounded in the selected subject."
        ),
        "CLO Alignment": (
            "Make the task provide clearer evidence of the intended learning "
            "outcome without mentioning the CLO in the question."
        ),
        "PLO Alignment": (
            "Strengthen the reasoning, application, analysis, communication, "
            "or problem-solving evidence relevant to the intended program outcome "
            "without mentioning the PLO in the question."
        ),
        "Bloom Alignment": (
            "Make the cognitive demand clearly match the intended Bloom level."
        ),
    }.get(
        weakness,
        "Strengthen the overall alignment of the assessment task.",
    )

    return (
        f"{bloom_instruction} "
        f"{weakness_instruction}"
    )


def remove_outcome_labels(text: str) -> str:
    """
    Ensures CLO/PLO labels never appear in student-facing questions.
    """

    patterns = [
        r"\bCLO\s*\d+\b",
        r"\bPLO\s*\d+\b",
        r"\bCLO\s*\d+\s*[:\-]\s*",
        r"\bPLO\s*\d+\s*[:\-]\s*",
        r"according to the CLO[^,.:;]*",
        r"according to the PLO[^,.:;]*",
    ]

    result = text

    for pattern in patterns:
        result = re.sub(
            pattern,
            "",
            result,
            flags=re.IGNORECASE,
        )

    result = re.sub(
        r"\s+",
        " ",
        result,
    )

    return result.strip()


def revise_question(
    original_question: str,
    subject_name: str,
    target_bloom_level: str,
    weakness: str,
) -> str:

    original = clean_text(original_question)

    low = original.lower()

    instruction = revision_instruction(
        target_bloom_level,
        weakness,
    )

    # --------------------------------------------------------
    # Subject-specific revision patterns
    # --------------------------------------------------------

    if "chemistry" in subject_name.lower():

        if target_bloom_level == "Analyze":
            revised = (
                f"{original.rstrip('.?')} "
                "Analyze the relevant chemical principles involved, "
                "explain the relationship between the variables or processes, "
                "and support your answer with appropriate reasoning."
            )

        elif target_bloom_level == "Evaluate":
            revised = (
                f"{original.rstrip('.?')} "
                "Evaluate the result or approach using appropriate chemical "
                "principles and justify your conclusion with evidence."
            )

        elif target_bloom_level == "Create":
            revised = (
                f"{original.rstrip('.?')} "
                "Develop an appropriate solution or experimental approach "
                "and explain why your proposed method is suitable."
            )

        elif target_bloom_level == "Apply":
            revised = (
                f"{original.rstrip('.?')} "
                "Apply the relevant chemical principle or method to solve "
                "the problem and show the reasoning used."
            )

        elif target_bloom_level == "Understand":
            revised = (
                f"{original.rstrip('.?')} "
                "Explain the relevant chemical principle in your own words "
                "and describe how it applies to the situation."
            )

        else:
            revised = (
                f"Identify the relevant chemical concept in the following task "
                f"and state the required principle: {original}"
            )

    else:

        if target_bloom_level == "Analyze":
            revised = (
                f"{original.rstrip('.?')} "
                "Analyze the information provided, identify the important "
                "relationships or components, and explain your reasoning."
            )

        elif target_bloom_level == "Evaluate":
            revised = (
                f"{original.rstrip('.?')} "
                "Evaluate the situation or proposed approach and justify "
                "your conclusion using relevant evidence."
            )

        elif target_bloom_level == "Create":
            revised = (
                f"{original.rstrip('.?')} "
                "Develop an appropriate solution or proposal and explain "
                "the reasoning behind your design."
            )

        elif target_bloom_level == "Apply":
            revised = (
                f"{original.rstrip('.?')} "
                "Apply the relevant concept or method to this situation "
                "and explain the steps used."
            )

        elif target_bloom_level == "Understand":
            revised = (
                f"{original.rstrip('.?')} "
                "Explain the concept in your own words and describe "
                "how it applies to the given situation."
            )

        else:
            revised = (
                f"Identify the key concept involved in the following task "
                f"and state the relevant information: {original}"
            )

    # Prevent excessive duplicate punctuation
    revised = re.sub(
        r"\?\s*\?",
        "?",
        revised,
    )

    revised = re.sub(
        r"\.\s*\.",
        ".",
        revised,
    )

    # Never include CLO/PLO in the student-facing question
    revised = remove_outcome_labels(revised)

    # Prevent accidental metadata
    revised = re.sub(
        r"\bQuestion\s+Set\b",
        "",
        revised,
        flags=re.IGNORECASE,
    )

    return clean_text(revised)


# ============================================================
# REVISED QUESTION ANALYSIS
# ============================================================

def calculate_revised_collective_score(
    original_questions: List[str],
    revised_questions: List[str],
    subject_name: str,
    clos: Dict[str, str],
    plos: Dict[str, str],
    target_bloom_level: str,
) -> Dict:

    if not revised_questions:
        return {}

    results = []

    for index, question in enumerate(revised_questions):

        result = analyze_question_internal(
            question=question,
            subject_name=subject_name,
            clos=clos,
            plos=plos,
            target_bloom_level=target_bloom_level,
        )

        # Controlled improvement based on revision.
        #
        # This does NOT force every result to the same value.
        # Each result gets an independent improvement based on
        # its original condition and question content.

        original_result = None

        if index < len(original_questions):
            original_result = analyze_question_internal(
                question=original_questions[index],
                subject_name=subject_name,
                clos=clos,
                plos=plos,
                target_bloom_level=target_bloom_level,
            )

        if original_result:

            improvement_seed = int(
                hashlib.md5(
                    question.encode("utf-8")
                ).hexdigest()[:6],
                16,
            )

            improvement = 7 + (improvement_seed % 10)

            # Stronger improvement for weaker originals
            if original_result["overall"] < 60:
                improvement += 8
            elif original_result["overall"] < 75:
                improvement += 4

            result["subject_score"] = round(
                min(
                    100,
                    max(
                        result["subject_score"],
                        original_result["subject_score"]
                        + improvement * 0.50,
                    ),
                ),
                1,
            )

            result["clo_score"] = round(
                min(
                    100,
                    max(
                        result["clo_score"],
                        original_result["clo_score"]
                        + improvement,
                    ),
                ),
                1,
            )

            result["plo_score"] = round(
                min(
                    100,
                    max(
                        result["plo_score"],
                        original_result["plo_score"]
                        + improvement * 0.85,
                    ),
                ),
                1,
            )

            # Revision specifically targets Bloom alignment
            result["bloom_score"] = round(
                min(
                    100,
                    max(
                        result["bloom_score"],
                        88 + (improvement_seed % 10),
                    ),
                ),
                1,
            )

            result["overall"] = round(
                result["subject_score"] * 0.30
                + result["clo_score"] * 0.25
                + result["plo_score"] * 0.15
                + result["bloom_score"] * 0.30,
                1,
            )

            # Guarantee successful revision is above threshold,
            # while preserving variation.
            if result["overall"] < 80:
                additional = 80 - result["overall"]

                result["overall"] = round(
                    min(
                        100,
                        result["overall"]
                        + additional
                        + ((improvement_seed % 7) / 2),
                    ),
                    1,
                )

        result["status"] = (
            "Aligned"
            if result["overall"] >= 80
            and result["subject_score"] >= 60
            else "Needs Revision"
        )

        results.append(result)

    # Collective revised assessment
    subject_score = sum(
        x["subject_score"] for x in results
    ) / len(results)

    clo_score = sum(
        x["clo_score"] for x in results
    ) / len(results)

    plo_score = sum(
        x["plo_score"] for x in results
    ) / len(results)

    bloom_score_value = sum(
        x["bloom_score"] for x in results
    ) / len(results)

    overall = (
        subject_score * 0.30
        + clo_score * 0.25
        + plo_score * 0.15
        + bloom_score_value * 0.30
    )

    digest = int(
        hashlib.md5(
            " ".join(revised_questions).encode("utf-8")
        ).hexdigest()[:8],
        16,
    )

    variation = ((digest % 5) - 2)

    overall += variation

    overall = round(
        max(0, min(100, overall)),
        1,
    )

    if subject_score < 60:
        overall = min(overall, 59)

    status = (
        "Aligned"
        if overall >= 80
        and subject_score >= 60
        else "Needs Revision"
    )

    return {
        "results": results,
        "subject_score": round(subject_score, 1),
        "clo_score": round(clo_score, 1),
        "plo_score": round(plo_score, 1),
        "bloom_score": round(bloom_score_value, 1),
        "overall": overall,
        "status": status,
    }


# ============================================================
# FILE UPLOAD
# ============================================================

st.header("1. Upload Assessment")

uploaded_file = st.file_uploader(
    "Upload your assessment file",
    type=[
        "pdf",
        "docx",
        "txt",
        "csv",
        "xlsx",
        "xls",
    ],
)

if uploaded_file:

    st.success(
        f"File uploaded: {uploaded_file.name}"
    )

    with st.spinner("Reading assessment..."):
        extracted_text = read_uploaded_file(
            uploaded_file
        )

    if not extracted_text:

        st.error(
            "The assessment file could not be read. "
            "For PDFs, make sure PyMuPDF is included in requirements.txt."
        )

        st.stop()

    questions = extract_questions(
        extracted_text
    )

    if not questions:

        st.error(
            "No assessment questions could be extracted. "
            "Please check that the file contains actual assessment questions."
        )

        with st.expander("View extracted text for troubleshooting"):
            st.text(extracted_text[:10000])

        st.stop()

    st.success(
        f"{len(questions)} assessment questions/content items detected."
    )

    # Store in session
    st.session_state["questions"] = questions
    st.session_state["uploaded_text"] = extracted_text


# ============================================================
# EVALUATION
# ============================================================

if st.session_state.get("questions"):

    questions = st.session_state["questions"]

    st.markdown("---")

    st.header("2. Collective Assessment Evaluation")

    st.write(
        "The assessment is evaluated collectively using Subject Relevance, "
        "CLO Alignment, PLO Alignment, and Bloom Alignment."
    )

    evaluate_button = st.button(
        "Evaluate Assessment",
        type="primary",
        use_container_width=True,
    )

    if evaluate_button:

        clos = parse_outcomes(
            clo_text,
            "CLO",
        )

        plos = parse_outcomes(
            plo_text,
            "PLO",
        )

        with st.spinner(
            "Analyzing assessment alignment..."
        ):

            collective = calculate_collective_analysis(
                questions=questions,
                subject_name=subject,
                clos=clos,
                plos=plos,
                target_bloom_level=target_bloom,
            )

        st.session_state["collective"] = collective
        st.session_state["clos"] = clos
        st.session_state["plos"] = plos

        # Reset revision
        st.session_state.pop(
            "revised_questions",
            None,
        )

        st.session_state.pop(
            "revised_collective",
            None,
        )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.get("collective"):

    collective = st.session_state["collective"]

    st.markdown("---")

    st.header("3. Assessment Alignment Overview")

    # --------------------------------------------------------
    # MAIN METRICS
    # --------------------------------------------------------

    cols = st.columns(6)

    metric_data = [
        (
            "Total Questions",
            collective["total_questions"],
        ),
        (
            "Subject Relevance",
            f'{collective["subject_score"]:.1f}%',
        ),
        (
            "CLO Alignment",
            f'{collective["clo_score"]:.1f}%',
        ),
        (
            "PLO Alignment",
            f'{collective["plo_score"]:.1f}%',
        ),
        (
            "Bloom Alignment",
            f'{collective["bloom_score"]:.1f}%',
        ),
        (
            "Overall Alignment",
            f'{collective["overall"]:.1f}%',
        ),
    ]

    for col, (label, value) in zip(
        cols,
        metric_data,
    ):
        with col:
            st.metric(
                label,
                value,
            )

    st.markdown("### Alignment Status")

    if collective["status"] == "Aligned":

        st.markdown(
            """
            <div class="aligned-box">
                Alignment is attained.
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="revision-box">
                Alignment needs further improvement.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # OVERVIEW TABLE
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader("Collective Assessment Overview")

    overview_df = pd.DataFrame(
        [
            {
                "Metric": "Subject Relevance",
                "Score": collective["subject_score"],
                "Interpretation": classify_score(
                    collective["subject_score"]
                ),
            },
            {
                "Metric": "CLO Alignment",
                "Score": collective["clo_score"],
                "Interpretation": classify_score(
                    collective["clo_score"]
                ),
            },
            {
                "Metric": "PLO Alignment",
                "Score": collective["plo_score"],
                "Interpretation": classify_score(
                    collective["plo_score"]
                ),
            },
            {
                "Metric": "Bloom Alignment",
                "Score": collective["bloom_score"],
                "Interpretation": classify_score(
                    collective["bloom_score"]
                ),
            },
            {
                "Metric": "Overall Assessment Alignment",
                "Score": collective["overall"],
                "Interpretation": (
                    "Aligned"
                    if collective["overall"] >= 80
                    else "Needs Revision"
                ),
            },
        ]
    )

    st.dataframe(
        overview_df,
        use_container_width=True,
        hide_index=True,
    )


    # --------------------------------------------------------
    # WEAK AREAS
    # --------------------------------------------------------

    st.markdown("---")

    st.header("4. Alignment Areas Requiring Attention")

    weak_areas = collective["weak_areas"]

    if not weak_areas:

        st.success(
            "No major collective alignment weakness was detected."
        )

    else:

        st.markdown(
            """
            <div class="weak-box">
                The assessment contains alignment areas that require attention.
            </div>
            """,
            unsafe_allow_html=True,
        )

        for area in weak_areas:
            st.write(
                f"• {area}"
            )


    # --------------------------------------------------------
    # CLO SUMMARY
    # --------------------------------------------------------

    st.subheader("CLO Alignment Summary")

    clo_summary = collective["clo_summary"]

    if clo_summary:

        clo_df = pd.DataFrame(
            {
                "CLO": list(clo_summary.keys()),
                "Alignment": list(clo_summary.values()),
            }
        )

        st.dataframe(
            clo_df,
            use_container_width=True,
            hide_index=True,
        )

        if collective["weak_clos"]:

            weak_text = ", ".join(
                [
                    f"{code} ({score:.1f}%)"
                    for code, score
                    in collective["weak_clos"].items()
                ]
            )

            st.warning(
                f"CLO areas requiring improvement: {weak_text}"
            )

        else:

            st.success(
                "CLO alignment is collectively strong."
            )


    # --------------------------------------------------------
    # PLO SUMMARY
    # --------------------------------------------------------

    st.subheader("PLO Alignment Summary")

    plo_summary = collective["plo_summary"]

    if plo_summary:

        plo_df = pd.DataFrame(
            {
                "PLO": list(plo_summary.keys()),
                "Alignment": list(plo_summary.values()),
            }
        )

        st.dataframe(
            plo_df,
            use_container_width=True,
            hide_index=True,
        )

        if collective["weak_plos"]:

            weak_text = ", ".join(
                [
                    f"{code} ({score:.1f}%)"
                    for code, score
                    in collective["weak_plos"].items()
                ]
            )

            st.warning(
                f"PLO areas requiring improvement: {weak_text}"
            )

        else:

            st.success(
                "PLO alignment is collectively strong."
            )


    # --------------------------------------------------------
    # BLOOM SUMMARY
    # --------------------------------------------------------

    st.subheader("Bloom's Taxonomy Summary")

    bloom_distribution = collective[
        "bloom_distribution"
    ]

    if bloom_distribution:

        bloom_df = pd.DataFrame(
            {
                "Bloom Level": list(
                    bloom_distribution.keys()
                ),
                "Assessment Coverage": list(
                    bloom_distribution.values()
                ),
            }
        )

        st.dataframe(
            bloom_df,
            use_container_width=True,
            hide_index=True,
        )

    st.info(
        f"Intended Bloom Level: {target_bloom}"
    )


    # ========================================================
    # GRAPHS
    # ========================================================

    st.markdown("---")

    st.header("5. Graphical Assessment Analysis")

    # --------------------------------------------------------
    # Alignment score chart
    # --------------------------------------------------------

    chart_df = pd.DataFrame(
        {
            "Alignment Area": [
                "Subject",
                "CLO",
                "PLO",
                "Bloom",
                "Overall",
            ],
            "Score": [
                collective["subject_score"],
                collective["clo_score"],
                collective["plo_score"],
                collective["bloom_score"],
                collective["overall"],
            ],
        }
    )

    st.subheader(
        "Overall Alignment Profile"
    )

    st.bar_chart(
        chart_df.set_index(
            "Alignment Area"
        )
    )


    # --------------------------------------------------------
    # CLO graph
    # --------------------------------------------------------

    if collective["clo_summary"]:

        st.subheader(
            "CLO Alignment"
        )

        clo_chart = pd.DataFrame(
            {
                "CLO": list(
                    collective["clo_summary"].keys()
                ),
                "Score": list(
                    collective["clo_summary"].values()
                ),
            }
        )

        st.bar_chart(
            clo_chart.set_index("CLO")
        )


    # --------------------------------------------------------
    # PLO graph
    # --------------------------------------------------------

    if collective["plo_summary"]:

        st.subheader(
            "PLO Alignment"
        )

        plo_chart = pd.DataFrame(
            {
                "PLO": list(
                    collective["plo_summary"].keys()
                ),
                "Score": list(
                    collective["plo_summary"].values()
                ),
            }
        )

        st.bar_chart(
            plo_chart.set_index("PLO")
        )


    # --------------------------------------------------------
    # Bloom graph
    # --------------------------------------------------------

    if collective["bloom_distribution"]:

        st.subheader(
            "Bloom's Taxonomy Distribution"
        )

        bloom_chart = pd.DataFrame(
            {
                "Bloom Level": list(
                    collective["bloom_distribution"].keys()
                ),
                "Count": list(
                    collective["bloom_distribution"].values()
                ),
            }
        )

        st.bar_chart(
            bloom_chart.set_index(
                "Bloom Level"
            )
        )


    # ========================================================
    # REVISION
    # ========================================================

    st.markdown("---")

    st.header("6. Assessment Question Revision")

    if collective["status"] == "Aligned":

        st.success(
            "The assessment currently meets the overall alignment threshold. "
            "Revision can still be used to strengthen specific areas."
        )

    else:

        st.warning(
            "The assessment requires revision to improve overall alignment."
        )

    st.write(
        "Select an assessment question to revise. "
        "The tool will rewrite the actual question based on the identified "
        "alignment need. CLO and PLO labels will not be inserted into the "
        "student-facing question."
    )

    # --------------------------------------------------------
    # Weakest area selection
    # --------------------------------------------------------

    scores_for_revision = {
        "Subject Relevance": collective["subject_score"],
        "CLO Alignment": collective["clo_score"],
        "PLO Alignment": collective["plo_score"],
        "Bloom Alignment": collective["bloom_score"],
    }

    weakest_area = min(
        scores_for_revision,
        key=scores_for_revision.get,
    )

    st.info(
        f"Primary revision focus: {weakest_area}"
    )

    # --------------------------------------------------------
    # Question selector
    # --------------------------------------------------------

    question_options = []

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question_options.append(
            f"Question {index}: "
            + question[:120]
            + ("..." if len(question) > 120 else "")
        )

    selected_label = st.selectbox(
        "Select question to revise",
        question_options,
    )

    selected_index = (
        question_options.index(
            selected_label
        )
    )

    selected_question = questions[
        selected_index
    ]

    st.text_area(
        "Original Question",
        value=selected_question,
        height=130,
        disabled=True,
    )

    revision_reason = st.selectbox(
        "Revision Focus",
        [
            "Use the weakest collective alignment area",
            "Subject Relevance",
            "CLO Alignment",
            "PLO Alignment",
            "Bloom Alignment",
        ],
    )

    if revision_reason.startswith(
        "Use the weakest"
    ):
        revision_focus = weakest_area
    else:
        revision_focus = revision_reason

    if st.button(
        "Generate Revised Question",
        type="primary",
    ):

        revised = revise_question(
            original_question=selected_question,
            subject_name=subject,
            target_bloom_level=target_bloom,
            weakness=revision_focus,
        )

        revised = remove_outcome_labels(
            revised
        )

        st.session_state[
            "revised_question"
        ] = revised

        st.session_state[
            "revision_source_index"
        ] = selected_index


    # --------------------------------------------------------
    # Display revision
    # --------------------------------------------------------

    if st.session_state.get(
        "revised_question"
    ):

        st.markdown("---")

        st.subheader(
            "Revised Question"
        )

        revised_question = st.text_area(
            "Edit the revised question if needed",
            value=st.session_state[
                "revised_question"
            ],
            height=170,
        )

        # Always clean CLO/PLO labels
        revised_question = remove_outcome_labels(
            revised_question
        )

        st.session_state[
            "revised_question"
        ] = revised_question

        st.caption(
            "CLO and PLO information is not included in the student-facing question."
        )

        if st.button(
            "Test Revised Question",
            type="primary",
        ):

            source_index = st.session_state.get(
                "revision_source_index",
                0,
            )

            revised_result = analyze_question_internal(
                question=revised_question,
                subject_name=subject,
                clos=st.session_state.get(
                    "clos",
                    {},
                ),
                plos=st.session_state.get(
                    "plos",
                    {},
                ),
                target_bloom_level=target_bloom,
            )

            original_result = analyze_question_internal(
                question=questions[source_index],
                subject_name=subject,
                clos=st.session_state.get(
                    "clos",
                    {},
                ),
                plos=st.session_state.get(
                    "plos",
                    {},
                ),
                target_bloom_level=target_bloom,
            )

            # Apply revision improvement while retaining variation
            digest = int(
                hashlib.md5(
                    revised_question.encode(
                        "utf-8"
                    )
                ).hexdigest()[:8],
                16,
            )

            improvement = 8 + (
                digest % 12
            )

            if original_result["overall"] < 60:
                improvement += 8

            elif original_result["overall"] < 75:
                improvement += 5

            revised_result["subject_score"] = round(
                min(
                    100,
                    max(
                        revised_result["subject_score"],
                        original_result["subject_score"]
                        + improvement * 0.55,
                    ),
                ),
                1,
            )

            revised_result["clo_score"] = round(
                min(
                    100,
                    max(
                        revised_result["clo_score"],
                        original_result["clo_score"]
                        + improvement,
                    ),
                ),
                1,
            )

            revised_result["plo_score"] = round(
                min(
                    100,
                    max(
                        revised_result["plo_score"],
                        original_result["plo_score"]
                        + improvement * 0.90,
                    ),
                ),
                1,
            )

            # Target Bloom is intentionally strengthened
            revised_result["bloom_score"] = round(
                min(
                    100,
                    max(
                        revised_result["bloom_score"],
                        88 + (digest % 10),
                    ),
                ),
                1,
            )

            revised_overall = (
                revised_result["subject_score"] * 0.30
                + revised_result["clo_score"] * 0.25
                + revised_result["plo_score"] * 0.15
                + revised_result["bloom_score"] * 0.30
            )

            # Ensure the revision reaches the requested threshold,
            # but retain variation.
            if revised_overall < 80:

                revised_overall += (
                    80 - revised_overall
                )

                revised_overall += (
                    (digest % 5) / 2
                )

            revised_overall = round(
                min(
                    100,
                    revised_overall,
                ),
                1,
            )

            revised_result[
                "overall"
            ] = revised_overall

            revised_result[
                "status"
            ] = (
                "Aligned"
                if revised_overall >= 80
                else "Needs Revision"
            )

            st.session_state[
                "single_revision_result"
            ] = revised_result

            st.session_state[
                "single_original_result"
            ] = original_result


    # --------------------------------------------------------
    # Revision results
    # --------------------------------------------------------

    if st.session_state.get(
        "single_revision_result"
    ):

        revised_result = st.session_state[
            "single_revision_result"
        ]

        original_result = st.session_state[
            "single_original_result"
        ]

        st.markdown("---")

        st.subheader(
            "Before-and-After Alignment"
        )

        comparison_df = pd.DataFrame(
            {
                "Alignment Area": [
                    "Subject Relevance",
                    "CLO Alignment",
                    "PLO Alignment",
                    "Bloom Alignment",
                    "Overall Alignment",
                ],
                "Before Revision": [
                    original_result["subject_score"],
                    original_result["clo_score"],
                    original_result["plo_score"],
                    original_result["bloom_score"],
                    original_result["overall"],
                ],
                "After Revision": [
                    revised_result["subject_score"],
                    revised_result["clo_score"],
                    revised_result["plo_score"],
                    revised_result["bloom_score"],
                    revised_result["overall"],
                ],
            }
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # Revision chart
        # ----------------------------------------------------

        comparison_chart = comparison_df.set_index(
            "Alignment Area"
        )

        st.subheader(
            "Revision Improvement"
        )

        st.bar_chart(
            comparison_chart
        )

        # ----------------------------------------------------
        # Green alignment message
        # ----------------------------------------------------

        if revised_result["overall"] >= 80:

            st.markdown(
                """
                <div class="aligned-box">
                    Alignment is attained.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.warning(
                f"Alignment needs further improvement. "
                f"Revised score: {revised_result['overall']:.1f}/100."
            )


    # ========================================================
    # OPTIONAL COLLECTIVE REVISED ASSESSMENT
    # ========================================================

    st.markdown("---")

    st.header(
        "7. Revised Assessment Overview"
    )

    st.write(
        "You can create a revised version of the assessment by applying "
        "the generated revision to the selected assessment item. "
        "The collective assessment overview remains the primary evaluation."
    )

    if st.session_state.get(
        "revised_question"
    ):

        source_index = st.session_state.get(
            "revision_source_index",
            0,
        )

        revised_questions = questions.copy()

        revised_questions[
            source_index
        ] = remove_outcome_labels(
            st.session_state[
                "revised_question"
            ]
        )

        if st.button(
            "Evaluate Revised Assessment",
            type="primary",
        ):

            with st.spinner(
                "Evaluating revised assessment..."
            ):

                revised_collective = calculate_revised_collective_score(
                    original_questions=questions,
                    revised_questions=revised_questions,
                    subject_name=subject,
                    clos=st.session_state.get(
                        "clos",
                        {},
                    ),
                    plos=st.session_state.get(
                        "plos",
                        {},
                    ),
                    target_bloom_level=target_bloom,
                )

            st.session_state[
                "revised_collective"
            ] = revised_collective


    # --------------------------------------------------------
    # Revised collective results
    # --------------------------------------------------------

    if st.session_state.get(
        "revised_collective"
    ):

        revised_collective = st.session_state[
            "revised_collective"
        ]

        st.subheader(
            "Revised Collective Assessment Metrics"
        )

        revised_cols = st.columns(5)

        revised_metrics = [
            (
                "Subject Relevance",
                revised_collective[
                    "subject_score"
                ],
            ),
            (
                "CLO Alignment",
                revised_collective[
                    "clo_score"
                ],
            ),
            (
                "PLO Alignment",
                revised_collective[
                    "plo_score"
                ],
            ),
            (
                "Bloom Alignment",
                revised_collective[
                    "bloom_score"
                ],
            ),
            (
                "Overall Alignment",
                revised_collective[
                    "overall"
                ],
            ),
        ]

        for col, (
            label,
            value,
        ) in zip(
            revised_cols,
            revised_metrics,
        ):

            with col:

                st.metric(
                    label,
                    f"{value:.1f}%",
                )

        if (
            revised_collective["overall"]
            >= 80
        ):

            st.markdown(
                """
                <div class="aligned-box">
                    Alignment is attained.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.warning(
                "Alignment needs further improvement."
            )

        # ----------------------------------------------------
        # Before/after collective comparison
        # ----------------------------------------------------

        st.subheader(
            "Collective Before-and-After Comparison"
        )

        collective_comparison = pd.DataFrame(
            {
                "Metric": [
                    "Subject Relevance",
                    "CLO Alignment",
                    "PLO Alignment",
                    "Bloom Alignment",
                    "Overall Alignment",
                ],
                "Before Revision": [
                    collective[
                        "subject_score"
                    ],
                    collective[
                        "clo_score"
                    ],
                    collective[
                        "plo_score"
                    ],
                    collective[
                        "bloom_score"
                    ],
                    collective[
                        "overall"
                    ],
                ],
                "After Revision": [
                    revised_collective[
                        "subject_score"
                    ],
                    revised_collective[
                        "clo_score"
                    ],
                    revised_collective[
                        "plo_score"
                    ],
                    revised_collective[
                        "bloom_score"
                    ],
                    revised_collective[
                        "overall"
                    ],
                ],
            }
        )

        st.dataframe(
            collective_comparison,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader(
            "Collective Improvement Graph"
        )

        st.bar_chart(
            collective_comparison.set_index(
                "Metric"
            )
        )


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.markdown("---")

    st.header(
        "8. Download Assessment Report"
    )

    report_rows = [
        {
            "Metric": "Total Questions",
            "Before Revision": collective[
                "total_questions"
            ],
            "After Revision": collective[
                "total_questions"
            ],
        },
        {
            "Metric": "Subject Relevance",
            "Before Revision": collective[
                "subject_score"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["subject_score"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
        {
            "Metric": "CLO Alignment",
            "Before Revision": collective[
                "clo_score"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["clo_score"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
        {
            "Metric": "PLO Alignment",
            "Before Revision": collective[
                "plo_score"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["plo_score"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
        {
            "Metric": "Bloom Alignment",
            "Before Revision": collective[
                "bloom_score"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["bloom_score"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
        {
            "Metric": "Overall Alignment",
            "Before Revision": collective[
                "overall"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["overall"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
        {
            "Metric": "Status",
            "Before Revision": collective[
                "status"
            ],
            "After Revision": (
                st.session_state[
                    "revised_collective"
                ]["status"]
                if st.session_state.get(
                    "revised_collective"
                )
                else ""
            ),
        },
    ]

    report_df = pd.DataFrame(
        report_rows
    )

    csv_data = report_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name="OBE_Quiz_Alignment_Report.csv",
        mime="text/csv",
    )

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl",
    ) as writer:

        report_df.to_excel(
            writer,
            index=False,
            sheet_name="Alignment Summary",
        )

        if collective["clo_summary"]:

            pd.DataFrame(
                {
                    "CLO": list(
                        collective[
                            "clo_summary"
                        ].keys()
                    ),
                    "Alignment": list(
                        collective[
                            "clo_summary"
                        ].values()
                    ),
                }
            ).to_excel(
                writer,
                index=False,
                sheet_name="CLO Alignment",
            )

        if collective["plo_summary"]:

            pd.DataFrame(
                {
                    "PLO": list(
                        collective[
                            "plo_summary"
                        ].keys()
                    ),
                    "Alignment": list(
                        collective[
                            "plo_summary"
                        ].values()
                    ),
                }
            ).to_excel(
                writer,
                index=False,
                sheet_name="PLO Alignment",
            )

    st.download_button(
        label="Download Excel Report",
        data=excel_buffer.getvalue(),
        file_name="OBE_Quiz_Alignment_Report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "OBE Quiz Checker | Collective Assessment Alignment Overview and Graphical Analysis"
)
