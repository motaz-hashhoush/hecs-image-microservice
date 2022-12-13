from app import api
from flask_restx import Resource, fields
from dotenv import dotenv_values
from app.modules.HecsModel import HecsModel

hecs_model = HecsModel(path_to_model=dotenv_values()['modelPath'], label_freq=5, threshold=0.31)


@api.route('/hecs/<string:brand>')
class Hecs(Resource):
    
    def get(self, brand):
        try:
            
            response = {
                'status': 200,
                'labels': hecs_model.prdict(brand),
            }
        except Exception as e:
            response = {
                'status': 400,
                'response': str(e)
            }
            
        return response


brands = api.model('brands', {'brands': fields.List(fields.String(), required=True)})
@api.route('/multihecs/') 
@api.expect(brands, validate=True)
class MultiHecs(Resource):
    
    def post(self):
        try:
            if api.payload.get('brands') is None:
                raise KeyError('brands is required')
            
            response = {
                'status': 200,
                'labels': {},
            }
            
            for brand in api.payload['brands']:
                response['labels'][brand] =  hecs_model.prdict(brand)
            
        except Exception as e:
            response = {
                'status': 400,
                'response': str(e)
            }
            
        return response
