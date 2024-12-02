from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from routes.bible_routes import initialize_routes

app = Flask(__name__)
CORS(app)
api = Api(app)

# Inicializa as rotas
initialize_routes(api)

if __name__ == "__main__":
    app.run(debug=True)
