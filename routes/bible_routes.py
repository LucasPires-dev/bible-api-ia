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

def initialize_routes(api):
    api.add_resource(BibleVerse, "/api/bible/<string:version>/<string:book>/<int:chapter>/<int:verse>")

    api.add_resource(BibleSearch, "/api/bible/search")
