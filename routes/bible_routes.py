from flask import request
from flask_restful import Resource
import sqlite3

class BibleVerse(Resource):
    def get(self, version, book, chapter, verse):
        # Lógica para buscar o versículo no banco de dados
        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        query = '''
            SELECT text FROM bible
            WHERE version = ? AND book = ? AND chapter = ? AND verse = ?;
        '''
        result = cursor.execute(query, (version, book, chapter, verse)).fetchone()
        connection.close()

        if result:
            return {"verse": result[0]}, 200
        return {"error": "Verse not found"}, 404
    
class BibleSearch(Resource):
    def get(self):
        # Parâmetro 'q' para a palavra-chave
        keyword = request.args.get('q')
        version = request.args.get('version', 'NVI')  # Versão padrão 'NVI' se não for fornecida
        
        if not keyword:
            return {"error": "Keyword is required"}, 400

        # Conectar ao banco de dados SQLite
        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        # Consulta SQL para buscar versículos que contenham a palavra-chave
        query = '''
            SELECT book, chapter, verse, text, version
            FROM bible
            WHERE text LIKE ? AND version = ?;
        '''
        
        # Executar consulta e buscar os resultados
        results = cursor.execute(query, (f"%{keyword}%", version)).fetchall()
        connection.close()

        if not results:
            return {"message": "No results found"}, 404
        
        # Formatando os resultados
        verses = [
            {"book": row[0], "chapter": row[1], "verse": row[2], "text": row[3], "version": row[4]}
            for row in results
        ]
        
        return {"results": verses}, 200
    
class RelatedReadings(Resource):
    def get(self, theme):
        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        # Consulta para buscar leituras relacionadas ao tema
        query = "SELECT reference FROM related_readings WHERE theme = ?"
        results = cursor.execute(query, (theme,)).fetchall()
        connection.close()

        if results:
            references = [row[0] for row in results]
            return {"theme": theme, "related_readings": references}, 200
        return {"error": f"No related readings found for theme '{theme}'"}, 404
    
class ContextualExplanations(Resource):
    def get(self):
        # Recebe o tipo e referência como parâmetros da requisição
        explanation_type = request.args.get('type')
        reference = request.args.get('reference')

        if not explanation_type or not reference:
            return {"error": "Both 'type' and 'reference' parameters are required"}, 400

        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        # Consulta para buscar a explicação no banco de dados
        query = "SELECT explanation FROM contextual_explanations WHERE type = ? AND reference = ?"
        result = cursor.execute(query, (explanation_type, reference)).fetchone()
        connection.close()

        if result:
            return {"type": explanation_type, "reference": reference, "explanation": result[0]}, 200
        return {"error": "No explanation found for the provided reference"}, 404
    
class AddContextualExplanation(Resource):
    def post(self):
        data = request.get_json()
        explanation_type = data.get('type')
        reference = data.get('reference')
        explanation = data.get('explanation')

        if not explanation_type or not reference or not explanation:
            return {"error": "All fields are required: type, reference, explanation"}, 400

        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        query = "INSERT INTO contextual_explanations (type, reference, explanation) VALUES (?, ?, ?)"
        cursor.execute(query, (explanation_type, reference, explanation))
        connection.commit()
        connection.close()

        return {"message": "Contextual explanation added successfully"}, 201

class AddVerseToTheme(Resource):
    def post(self):
        data = request.get_json()
        theme = data.get('theme')
        verse = data.get('verse')

        if not theme or not verse:
            return {"error": "Both 'theme' and 'verse' fields are required"}, 400

        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        query = "INSERT INTO related_readings (theme, verse) VALUES (?, ?)"
        cursor.execute(query, (theme, verse))
        connection.commit()
        connection.close()

        return {"message": "Verse added to theme successfully"}, 201

class ListThemes(Resource):
    def get(self):
        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        query = "SELECT DISTINCT theme FROM related_readings"
        result = cursor.execute(query).fetchall()
        connection.close()

        themes = [row[0] for row in result]
        return {"themes": themes}, 200

class LearnData(Resource):
    def post(self):
        data = request.get_json()

        theme = data.get('theme')
        explanation = data.get('explanation')
        recommendations = data.get('recommendations', [])  # Lista de versículos relacionados

        if not theme or not explanation:
            return {"error": "Theme and explanation are required"}, 400

        # Conectar ao banco de dados
        connection = sqlite3.connect('./database/bible.db')
        cursor = connection.cursor()

        try:
            # Inserir ou atualizar tema e explicação
            cursor.execute('''
                INSERT INTO explanations (theme, explanation)
                VALUES (?, ?)
                ON CONFLICT(theme) DO UPDATE SET explanation = excluded.explanation
            ''', (theme, explanation))

            # Inserir recomendações de leitura (se existirem)
            for verse in recommendations:
                cursor.execute('''
                    INSERT INTO recommendations (theme, verse)
                    VALUES (?, ?)
                ''', (theme, verse))

            connection.commit()
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}, 500
        finally:
            connection.close()

        return {"message": "Data added/updated successfully"}, 200

def initialize_routes(api):
    api.add_resource(BibleVerse, "/api/bible/<string:version>/<string:book>/<int:chapter>/<int:verse>")

    api.add_resource(BibleSearch, "/api/bible/search")

    api.add_resource(ListThemes, "/api/bible/related_readings")

    api.add_resource(RelatedReadings, "/api/bible/related_readings/<string:theme>")

    api.add_resource(ContextualExplanations, "/api/bible/contextual_explanations")

    api.add_resource(LearnData, "/api/learn")  # Nova rota para aprendizado

