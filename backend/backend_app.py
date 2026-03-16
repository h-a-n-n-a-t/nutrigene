from flask import Flask, request, jsonify
from flask_cors import CORS
from database import DatabaseManager
from diagnosis_engine import DiagnosisEngine
from questions import QUESTION_BANK, get_all_questions
import json
import uuid

app = Flask(__name__)
CORS(app)

# Initialize database and diagnosis engine
db = DatabaseManager()
diagnosis_engine = DiagnosisEngine()

# Load gene data on startup
db.load_gene_data('gene_data.json')

# ==================== Routes ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "NutriGene API is running"
    }), 200

@app.route('/api/genes', methods=['GET'])
def get_all_genes():
    """Get all available genes"""
    genes = db.get_all_genes()
    return jsonify({
        "success": True,
        "total": len(genes),
        "data": genes
    }), 200

@app.route('/api/gene/<gene_name>', methods=['GET'])
def get_gene(gene_name):
    """Get specific gene information"""
    gene_data = db.get_gene_by_name(gene_name)
    
    if not gene_data:
        return jsonify({
            "success": False,
            "message": f"Gene {gene_name} not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": gene_data
    }), 200

@app.route('/api/questions/initial', methods=['GET'])
def get_initial_questions():
    """Get initial screening questions"""
    questions = get_all_questions()
    return jsonify({
        "success": True,
        "total": len(questions),
        "data": questions
    }), 200

@app.route('/api/questions/<gene_name>', methods=['GET'])
def get_gene_questions(gene_name):
    """Get specific questions for a gene"""
    if gene_name not in QUESTION_BANK:
        return jsonify({
            "success": False,
            "message": f"No questions found for gene {gene_name}"
        }), 404
    
    questions = QUESTION_BANK[gene_name]
    return jsonify({
        "success": True,
        "gene": gene_name,
        "total": len(questions),
        "data": questions
    }), 200

@app.route('/api/diagnose/<gene_name>', methods=['POST'])
def diagnose_gene(gene_name):
    """Diagnose a specific gene based on answers"""
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        question_weights = data.get('weights', None)
        
        if not answers:
            return jsonify({
                "success": False,
                "message": "No answers provided"
            }), 400
        
        # Perform diagnosis
        result = diagnosis_engine.diagnose(gene_name, answers, question_weights)
        
        # Get gene information
        gene_info = db.get_gene_by_name(gene_name)
        
        # Save result to database
        user_id = str(uuid.uuid4())
        gene_id = gene_info['gene']['id'] if gene_info else None
        
        diagnosis_result = {
            "gene": gene_name,
            "confidence_score": result['confidence_score'],
            "status": result['status'],
            "risk_level": result['risk_level'],
            "gene_info": gene_info,
            "answers_summary": result['answers_summary']
        }
        
        db.save_diagnosis_result(user_id, gene_id, result['confidence_score'], answers, diagnosis_result)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "diagnosis": diagnosis_result
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/diagnose-multiple', methods=['POST'])
def diagnose_multiple_genes():
    """Diagnose multiple genes and provide comprehensive report"""
    try:
        data = request.get_json()
        gene_answers = data.get('gene_answers', {})
        
        if not gene_answers:
            return jsonify({
                "success": False,
                "message": "No gene answers provided"
            }), 400
        
        # Diagnose each gene
        all_results = {}
        for gene_name, answers in gene_answers.items():
            result = diagnosis_engine.diagnose(gene_name, answers)
            all_results[gene_name] = result
        
        # Get comprehensive multi-gene diagnosis
        comprehensive = diagnosis_engine.multi_gene_diagnosis(all_results)
        
        # Build detailed report
        report = {
            "primary_diagnosis": comprehensive['primary_diagnosis'],
            "secondary_diagnoses": comprehensive['secondary_diagnoses'],
            "total_genes_tested": comprehensive['total_genes_tested'],
            "positive_genes": comprehensive['positive_genes'],
            "all_results": dict(comprehensive['ranked_results']),
            "detailed_gene_info": {}
        }
        
        # Add detailed info for top candidates
        for gene_name in comprehensive['top_candidates']:
            gene_info = db.get_gene_by_name(gene_name)
            if gene_info:
                report['detailed_gene_info'][gene_name] = gene_info
        
        # Save comprehensive result
        user_id = str(uuid.uuid4())
        db.save_diagnosis_result(user_id, None, 
                                sum(r['confidence_score'] for r in all_results.values()) / len(all_results),
                                gene_answers, report)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "report": report
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/report/format', methods=['POST'])
def format_report():
    """Format a comprehensive health report"""
    try:
        data = request.get_json()
        report = data.get('report', {})
        
        if not report:
            return jsonify({
                "success": False,
                "message": "No report data provided"
            }), 400
        
        # Create formatted report
        formatted = {
            "header": {
                "title": "NutriGene Genetic Mutation & Disease Diagnosis Report",
                "generated_date": "2024",
                "disclaimer": "This report is for informational purposes only and is not a substitute for professional medical advice."
            },
            "executive_summary": {
                "primary_diagnosis": report.get('primary_diagnosis'),
                "secondary_diagnoses": report.get('secondary_diagnoses', []),
                "overall_assessment": f"Based on {report.get('total_genes_tested', 0)} genes analyzed, {report.get('positive_genes', 0)} showed significant risk markers."
            },
            "detailed_findings": report.get('detailed_gene_info', {}),
            "lifestyle_recommendations": _generate_lifestyle_recommendations(report),
            "dietary_guidelines": _generate_dietary_guidelines(report),
            "next_steps": [
                "Consult with a genetic counselor for confirmation testing",
                "Work with a nutritionist specializing in genetic nutrition",
                "Regular monitoring and follow-up assessments",
                "Lifestyle modifications as recommended"
            ]
        }
        
        return jsonify({
            "success": True,
            "formatted_report": formatted
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def _generate_lifestyle_recommendations(report):
    """Generate lifestyle recommendations based on diagnosis"""
    recommendations = []
    
    primary = report.get('primary_diagnosis')
    if primary == 'FTO' or primary == 'MC4R':
        recommendations.extend([
            "Implement regular physical activity (150 min/week moderate intensity)",
            "Practice portion control and mindful eating",
            "Reduce processed food consumption",
            "Maintain consistent meal timing"
        ])
    elif 'Diabetes' in str(primary):
        recommendations.extend([
            "Monitor blood glucose regularly",
            "Maintain healthy weight through diet and exercise",
            "Manage stress levels",
            "Schedule regular medical check-ups"
        ])
    elif primary == 'LCT' or primary == 'MCM6':
        recommendations.extend([
            "Avoid fresh dairy products",
            "Choose fermented dairy alternatives",
            "Consider lactase supplements",
            "Monitor digestive symptoms"
        ])
    
    return recommendations

def _generate_dietary_guidelines(report):
    """Generate dietary guidelines based on diagnosis"""
    guidelines = {}
    
    for gene_name, gene_info in report.get('detailed_gene_info', {}).items():
        if gene_info and gene_info.get('diet'):
            guidelines[gene_name] = {
                "recommendations": gene_info['diet'].get('recommendations', ''),
                "supplements": gene_info['diet'].get('supplements', ''),
                "restricted_foods": gene_info['diet'].get('restricted_foods', ''),
                "allowed_foods": gene_info['diet'].get('recommendations', '')
            }
    
    return guidelines

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)