from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize db with app
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Pizza Restaurant API</h1>'

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        # Get restaurant pizzas with pizza details
        restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
        
        restaurant_data = restaurant.to_dict()
        restaurant_data['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant_pizzas]
        
        return jsonify(restaurant_data)
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        db.session.delete(restaurant)
        db.session.commit()
        
        return make_response('', 204)

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            # Validate price manually first to match test expectations
            price = data['price']
            if not 1 <= price <= 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
            
            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            
            db.session.add(restaurant_pizza)
            db.session.commit()
            
            return make_response(jsonify(restaurant_pizza.to_dict()), 201)
            
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

# Add resources to API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)