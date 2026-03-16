from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class Mutation:
    snp_id: str
    genotype: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class DietRecommendation:
    recommendations: str
    supplements: List[str] = field(default_factory=list)
    restricted_foods: List[str] = field(default_factory=list)
    allowed_foods: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class GeneInfo:
    gene: str
    description: str
    function: str
    disease: str
    aliases: str
    mutations: List[Mutation] = field(default_factory=list)
    diet_recommendation: Optional[DietRecommendation] = None
    
    def to_dict(self):
        return {
            'gene': self.gene,
            'description': self.description,
            'function': self.function,
            'disease': self.disease,
            'aliases': self.aliases,
            'mutations': [m.to_dict() for m in self.mutations],
            'diet_recommendation': self.diet_recommendation.to_dict() if self.diet_recommendation else None
        }

@dataclass
class DiagnosisResult:
    gene: str
    confidence_score: float
    status: str
    risk_level: str
    mutation_alleles: List[str] = field(default_factory=list)
    diet_recommendations: Optional[DietRecommendation] = None
    test_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            'gene': self.gene,
            'confidence_score': self.confidence_score,
            'status': self.status,
            'risk_level': self.risk_level,
            'mutation_alleles': self.mutation_alleles,
            'diet_recommendations': self.diet_recommendations.to_dict() if self.diet_recommendations else None,
            'test_date': self.test_date
        }

@dataclass
class ComprehensiveReport:
    primary_diagnosis: str
    secondary_diagnoses: List[str]
    diagnosed_genes: List[GeneInfo] = field(default_factory=list)
    overall_risk: str = "MODERATE"
    recommendations: str = ""
    test_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            'primary_diagnosis': self.primary_diagnosis,
            'secondary_diagnoses': self.secondary_diagnoses,
            'diagnosed_genes': [g.to_dict() for g in self.diagnosed_genes],
            'overall_risk': self.overall_risk,
            'recommendations': self.recommendations,
            'test_date': self.test_date
        }