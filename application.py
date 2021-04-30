from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from app_config import host, port
from semantic_similarity.main import QnodeSimilarity
from semantic_similarity.main import NN
from semantic_similarity.main import Paths

app = Flask(__name__)
CORS(app)

api = Api(app)

api.add_resource(NN, '/nearest-neighbors')
api.add_resource(QnodeSimilarity, '/similarity_api')
api.add_resource(Paths, '/paths')

if __name__ == '__main__':
    app.run(host=host, port=port)
