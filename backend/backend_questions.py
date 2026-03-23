# Question bank for different genes
QUESTION_BANK = {
    "CTLA4": [
        {"question": "Do you have a family history of Type 1 Diabetes?", "category": "family_history", "weight": 0.8},
        {"question": "Have you experienced unexplained weight loss recently?", "category": "symptoms", "weight": 0.6},
        {"question": "Do you feel unusual thirst and frequent urination?", "category": "symptoms", "weight": 0.7},
        {"question": "Have you been diagnosed with other autoimmune diseases?", "category": "medical_history", "weight": 0.9},
    ],
    "IL6": [
        {"question": "Do you have elevated inflammation markers in blood tests?", "category": "lab_results", "weight": 0.85},
        {"question": "Do you experience chronic joint or muscle pain?", "category": "symptoms", "weight": 0.7},
        {"question": "Have you been diagnosed with Type 2 Diabetes?", "category": "diagnosis", "weight": 0.8},
        {"question": "Do you have a family history of metabolic disorders?", "category": "family_history", "weight": 0.6},
    ],
    "VEGFA": [
        {"question": "Have you experienced vision problems or diabetic retinopathy?", "category": "complications", "weight": 0.9},
        {"question": "Do you have kidney disease or proteinuria?", "category": "complications", "weight": 0.85},
        {"question": "Have you been diagnosed with diabetes complications?", "category": "medical_history", "weight": 0.8},
        {"question": "Do you have elevated blood pressure?", "category": "symptoms", "weight": 0.6},
    ],
    "CDKN2A": [
        {"question": "Do you have Type 2 Diabetes diagnosis?", "category": "diagnosis", "weight": 0.85},
        {"question": "Is your BMI greater than 25?", "category": "anthropometry", "weight": 0.7},
        {"question": "Do you have a family history of diabetes or heart disease?", "category": "family_history", "weight": 0.75},
        {"question": "Are you above 45 years of age?", "category": "demographics", "weight": 0.6},
    ],
    "PPARG": [
        {"question": "Do you have insulin resistance symptoms?", "category": "symptoms", "weight": 0.8},
        {"question": "Do you struggle with weight management?", "category": "lifestyle", "weight": 0.7},
        {"question": "Have you been diagnosed with metabolic syndrome?", "category": "diagnosis", "weight": 0.85},
        {"question": "Do you have elevated triglycerides?", "category": "lab_results", "weight": 0.75},
    ],
    "FTO": [
        {"question": "Do you find it difficult to maintain weight?", "category": "lifestyle", "weight": 0.8},
        {"question": "Do you have increased appetite or hunger cues?", "category": "symptoms", "weight": 0.75},
        {"question": "Is your BMI above 30?", "category": "anthropometry", "weight": 0.85},
        {"question": "Do you have a family history of obesity?", "category": "family_history", "weight": 0.7},
    ],
    "LCT": [
        {"question": "Do you experience bloating after consuming dairy?", "category": "symptoms", "weight": 0.9},
        {"question": "Do you have gas or diarrhea after milk consumption?", "category": "symptoms", "weight": 0.85},
        {"question": "Do you have stomach cramps with dairy products?", "category": "symptoms", "weight": 0.8},
        {"question": "Do you avoid milk and prefer lactose-free products?", "category": "lifestyle", "weight": 0.75},
    ],
    "MCM6": [
        {"question": "Do you have difficulty digesting fresh milk?", "category": "symptoms", "weight": 0.85},
        {"question": "Have you noticed lactose intolerance symptoms?", "category": "symptoms", "weight": 0.9},
        {"question": "Can you tolerate aged cheeses but not fresh milk?", "category": "lifestyle", "weight": 0.7},
        {"question": "Do you prefer fermented dairy products like yogurt?", "category": "lifestyle", "weight": 0.75},
    ],
}

def get_questions_for_gene(gene_name):
    """Get questions for a specific gene, falling back to general screening prompts."""
    gene_specific_questions = QUESTION_BANK.get(gene_name)
    if gene_specific_questions:
        return gene_specific_questions

    fallback_questions = []
    for question in get_all_questions():
        if gene_name in question.get("genes", []):
            fallback_questions.append({
                "question": question["question"],
                "category": "general_screening",
                "weight": question.get("weight", 0.5),
            })

    return fallback_questions

def get_all_questions():
    """Get all questions for initial screening"""
    general_questions = [
        {"question": "Do you have Type 1 Diabetes?", "genes": ["CTLA4", "IL10", "PTPN22"], "weight": 0.9},
        {"question": "Do you have Type 2 Diabetes?", "genes": ["IL6", "CDKN2A", "PPARG", "FTO", "TCF7L2"], "weight": 0.9},
        {"question": "Do you experience lactose intolerance symptoms?", "genes": ["LCT", "MCM6"], "weight": 0.85},
        {"question": "Do you have obesity or weight management issues?", "genes": ["FTO", "MC4R", "LEP", "LEPR"], "weight": 0.8},
        {"question": "Do you have elevated cholesterol or triglycerides?", "genes": ["APOE", "CETP", "PCSK9"], "weight": 0.75},
        {"question": "Do you experience inflammation or joint pain?", "genes": ["IL6", "IL10", "IFIH1"], "weight": 0.7},
    ]
    return general_questions
