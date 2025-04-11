from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import script

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

class Test(Resource):
    def get(self):
        return 'Welcome to, Test App API!'

    def post(self):
        try:
            value = request.get_json()
            if(value):
                return {'Post Values': value}, 201
            return {"error":"Invalid format."}
        except Exception as error:
            return {'error': str(error)}
    
class GetDepressionPredictionOutput(Resource):
    def get(self):
        try:
            pred = int(script.predict_depression())
            return {'prediction_file': pred}
        
        except Exception as error:
            return {"error": str(error)}, 500

    
    def post(self):
        return {"error": "Invalid Method."}
    
class GetAnxietyPredictionOutput(Resource):
    def get(self):
        try:
            pred = script.predict_anxiety()
            return {'prediction_file': pred}
        
        except Exception as error:
            return {"error": str(error)}, 500

    
    def post(self):
        return {"error": "Invalid Method."}
    
class GetStressPredictionOutput(Resource):
    def get(self):
        try:
            pred = int(script.predict_stress())  # ✅ Convert int64 to int
            return {'prediction_file': pred}
        except Exception as error:
            return {"error": str(error)}, 500

    
    def post(self):
        return {"error": "Invalid Method."}
        

api.add_resource(Test, '/')
api.add_resource(GetDepressionPredictionOutput, '/getDepressionPredictionOutput')
api.add_resource(GetAnxietyPredictionOutput, '/getAnxietyPredictionOutput')
api.add_resource(GetStressPredictionOutput, '/getStressPredictionOutput')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5500, debug=True)