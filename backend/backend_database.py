import sqlite3
import json
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path='nutrigene.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the database with gene data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create genes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genes (
                id INTEGER PRIMARY KEY,
                gene_name TEXT UNIQUE NOT NULL,
                description TEXT,
                function TEXT,
                disease TEXT,
                aliases TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create mutations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutations (
                id INTEGER PRIMARY KEY,
                gene_id INTEGER NOT NULL,
                snp_id TEXT,
                genotype TEXT,
                FOREIGN KEY (gene_id) REFERENCES genes(id)
            )
        ''')
        
        # Create diet recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_recommendations (
                id INTEGER PRIMARY KEY,
                gene_id INTEGER NOT NULL,
                recommendations TEXT,
                supplements TEXT,
                restricted_foods TEXT,
                FOREIGN KEY (gene_id) REFERENCES genes(id)
            )
        ''')
        
        # Create question bank table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                gene_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                category TEXT,
                FOREIGN KEY (gene_id) REFERENCES genes(id)
            )
        ''')
        
        # Create diagnosis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnosis_results (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                gene_id INTEGER,
                confidence_score REAL,
                answers TEXT,
                result JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gene_id) REFERENCES genes(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_gene_data(self, json_file='gene_data.json'):
        """Load gene data from JSON file"""
        try:
            with open(json_file, 'r') as f:
                genes_data = json.load(f)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for gene in genes_data:
                # Insert gene
                cursor.execute('''
                    INSERT OR REPLACE INTO genes 
                    (gene_name, description, function, disease, aliases)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    gene['gene'],
                    gene['description'],
                    gene['function'],
                    gene['disease'],
                    gene.get('aliases', '')
                ))
                
                gene_id = cursor.lastrowid
                
                # Insert mutations
                for snp, genotype in zip(gene.get('snp_ids', []), gene.get('genotypes', [])):
                    cursor.execute('''
                        INSERT INTO mutations (gene_id, snp_id, genotype)
                        VALUES (?, ?, ?)
                    ''', (gene_id, snp, genotype))
                
                # Insert diet recommendations
                cursor.execute('''
                    INSERT INTO diet_recommendations 
                    (gene_id, recommendations, supplements, restricted_foods)
                    VALUES (?, ?, ?, ?)
                ''', (
                    gene_id,
                    gene.get('diet_recommendations', ''),
                    gene.get('nutrient_supplements', ''),
                    gene.get('restricted_food', '')
                ))
            
            conn.commit()
            conn.close()
            print(f"Loaded {len(genes_data)} genes into database")
            return True
        except Exception as e:
            print(f"Error loading gene data: {e}")
            return False
    
    def get_gene_by_name(self, gene_name):
        """Retrieve gene information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM genes WHERE gene_name = ?', (gene_name,))
        gene = cursor.fetchone()
        
        if gene:
            gene_id = gene['id']
            
            # Get mutations
            cursor.execute('SELECT * FROM mutations WHERE gene_id = ?', (gene_id,))
            mutations = cursor.fetchall()
            
            # Get diet recommendations
            cursor.execute('SELECT * FROM diet_recommendations WHERE gene_id = ?', (gene_id,))
            diet = cursor.fetchone()
            
            conn.close()
            
            return {
                'gene': dict(gene),
                'mutations': [dict(m) for m in mutations],
                'diet': dict(diet) if diet else None
            }
        
        conn.close()
        return None
    
    def save_diagnosis_result(self, user_id, gene_id, confidence_score, answers, result):
        """Save diagnosis result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diagnosis_results 
            (user_id, gene_id, confidence_score, answers, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, gene_id, confidence_score, json.dumps(answers), json.dumps(result)))
        
        conn.commit()
        result_id = cursor.lastrowid
        conn.close()
        
        return result_id
    
    def get_all_genes(self):
        """Get all genes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM genes')
        genes = cursor.fetchall()
        conn.close()
        
        return [dict(g) for g in genes]