import psycopg2
import psycopg2.extras
import json
import os
from datetime import date, datetime

def _make_json_safe(value):
    """Recursively convert DB values into JSON-safe Python primitives."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(item) for item in value]
    return value

def _row_to_dict(row):
    if row is None:
        return None
    return _make_json_safe(dict(row))

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.init_database()

    def get_connection(self):
        return psycopg2.connect(self.database_url)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genes (
                id SERIAL PRIMARY KEY,
                gene_name TEXT UNIQUE NOT NULL,
                description TEXT,
                function TEXT,
                disease TEXT,
                aliases TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutations (
                id SERIAL PRIMARY KEY,
                gene_id INTEGER NOT NULL REFERENCES genes(id),
                snp_id TEXT,
                genotype TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_recommendations (
                id SERIAL PRIMARY KEY,
                gene_id INTEGER NOT NULL REFERENCES genes(id),
                recommendations TEXT,
                supplements TEXT,
                restricted_foods TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                gene_id INTEGER NOT NULL REFERENCES genes(id),
                question TEXT NOT NULL,
                category TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnosis_results (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                gene_id INTEGER,
                confidence_score REAL,
                answers TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()

    def load_gene_data(self, json_file):
        try:
            with open(json_file, 'r') as f:
                genes_data = json.load(f)

            conn = self.get_connection()
            cursor = conn.cursor()

            for gene in genes_data:
                cursor.execute('''
                    INSERT INTO genes (gene_name, description, function, disease, aliases)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (gene_name) DO UPDATE SET
                        description = EXCLUDED.description,
                        function = EXCLUDED.function,
                        disease = EXCLUDED.disease,
                        aliases = EXCLUDED.aliases
                    RETURNING id
                ''', (
                    gene['gene'],
                    gene['description'],
                    gene['function'],
                    gene['disease'],
                    gene.get('aliases', '')
                ))

                gene_id = cursor.fetchone()[0]

                cursor.execute('DELETE FROM mutations WHERE gene_id = %s', (gene_id,))
                for snp, genotype in zip(gene.get('snp_ids', []), gene.get('genotypes', [])):
                    cursor.execute(
                        'INSERT INTO mutations (gene_id, snp_id, genotype) VALUES (%s, %s, %s)',
                        (gene_id, snp, genotype)
                    )

                cursor.execute('DELETE FROM diet_recommendations WHERE gene_id = %s', (gene_id,))
                cursor.execute('''
                    INSERT INTO diet_recommendations (gene_id, recommendations, supplements, restricted_foods)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    gene_id,
                    gene.get('diet_recommendations', ''),
                    gene.get('nutrient_supplements', ''),
                    gene.get('restricted_food', '')
                ))

            conn.commit()
            cursor.close()
            conn.close()
            print(f"Loaded {len(genes_data)} genes into database")
            return True
        except Exception as e:
            print(f"Error loading gene data: {e}")
            return False

    def get_gene_by_name(self, gene_name):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute('SELECT * FROM genes WHERE gene_name = %s', (gene_name,))
        gene = cursor.fetchone()

        if gene:
            gene_id = gene['id']

            cursor.execute('SELECT * FROM mutations WHERE gene_id = %s', (gene_id,))
            mutations = cursor.fetchall()

            cursor.execute('SELECT * FROM diet_recommendations WHERE gene_id = %s', (gene_id,))
            diet = cursor.fetchone()

            cursor.close()
            conn.close()

            return _make_json_safe({
                'gene': _row_to_dict(gene),
                'mutations': [_row_to_dict(m) for m in mutations],
                'diet': _row_to_dict(diet)
            })

        cursor.close()
        conn.close()
        return None

    def save_diagnosis_result(self, user_id, gene_id, confidence_score, answers, result):
        conn = self.get_connection()
        cursor = conn.cursor()
        safe_answers = _make_json_safe(answers)
        safe_result = _make_json_safe(result)

        cursor.execute('''
            INSERT INTO diagnosis_results (user_id, gene_id, confidence_score, answers, result)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            user_id,
            gene_id,
            confidence_score,
            json.dumps(safe_answers),
            json.dumps(safe_result),
        ))

        result_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return result_id

    def get_all_genes(self):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute('SELECT * FROM genes')
        genes = cursor.fetchall()
        cursor.close()
        conn.close()

        return [_row_to_dict(g) for g in genes]
