from typing import Dict, List, Tuple
import json

class DiagnosisEngine:
    def __init__(self):
        self.gene_thresholds = {
            "CTLA4": 0.65,
            "IL6": 0.60,
            "VEGFA": 0.70,
            "CDKN2A": 0.65,
            "PPARG": 0.60,
            "FTO": 0.70,
            "TCF7L2": 0.65,
            "INS": 0.65,
            "LCT": 0.75,
            "MCM6": 0.75,
            "MC4R": 0.70,
            "LEP": 0.65,
            "LEPR": 0.60,
        }
    
    def calculate_confidence_score(self, answers: Dict[str, str], question_weights: List[float]) -> float:
        """Calculate confidence score based on answers"""
        positive_count = sum(1 for ans in answers.values() if ans.lower() == "yes")
        maybe_count = sum(1 for ans in answers.values() if ans.lower() == "maybe")
        total = len(answers)
        
        if total == 0:
            return 0.0
        
        # Yes = 1.0, Maybe = 0.5, No = 0.0
        score = (positive_count * 1.0 + maybe_count * 0.5) / total
        
        # Apply question weights
        if question_weights and len(question_weights) == total:
            weighted_score = sum(
                (1.0 if answers[i].lower() == "yes" else 0.5 if answers[i].lower() == "maybe" else 0.0) 
                * question_weights[i]
                for i in range(total)
            ) / sum(question_weights)
            return weighted_score
        
        return score
    
    def diagnose(self, gene_name: str, answers: Dict[str, str], 
                question_weights: List[float] = None) -> Dict:
        """Perform diagnosis for a specific gene"""
        
        confidence_score = self.calculate_confidence_score(answers, question_weights)
        threshold = self.gene_thresholds.get(gene_name, 0.65)
        
        is_positive = confidence_score >= threshold
        
        result = {
            "gene": gene_name,
            "confidence_score": round(confidence_score, 4),
            "threshold": threshold,
            "is_positive": is_positive,
            "status": "LIKELY POSITIVE" if is_positive else "LIKELY NEGATIVE",
            "risk_level": self._get_risk_level(confidence_score),
            "answers_summary": {
                "yes_count": sum(1 for ans in answers.values() if ans.lower() == "yes"),
                "maybe_count": sum(1 for ans in answers.values() if ans.lower() == "maybe"),
                "no_count": sum(1 for ans in answers.values() if ans.lower() == "no"),
                "total_questions": len(answers)
            }
        }
        
        return result
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level based on confidence score"""
        if score >= 0.80:
            return "VERY HIGH RISK"
        elif score >= 0.65:
            return "HIGH RISK"
        elif score >= 0.50:
            return "MODERATE RISK"
        elif score >= 0.35:
            return "LOW RISK"
        else:
            return "VERY LOW RISK"
    
    def multi_gene_diagnosis(self, results: Dict[str, Dict]) -> Dict:
        """Perform multi-gene diagnosis and ranking"""
        ranked_results = sorted(
            results.items(),
            key=lambda x: x[1]['confidence_score'],
            reverse=True
        )
        
        top_genes = [gene for gene, result in ranked_results if result['is_positive']]
        
        return {
            "total_genes_tested": len(results),
            "positive_genes": len(top_genes),
            "top_candidates": top_genes[:3],
            "ranked_results": ranked_results,
            "primary_diagnosis": top_genes[0] if top_genes else None,
            "secondary_diagnoses": top_genes[1:3] if len(top_genes) > 1 else []
        }