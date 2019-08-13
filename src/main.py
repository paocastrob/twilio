"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, Person
from twilio.rest import Client #con pipenv run deploy se descarga

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

queue = Queue(mode="FIFO")

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/new', methods=['POST'])
def addQueue():
   user = request.get_json()
   queue.enqueue(user)
   body = request.get_json()

    if body is None:
       raise APIException("Its empty", status_code=400)
   if 'name' not in body:
       raise APIException('You need to add name', status_code=400)
   if 'phone' not in body:
       raise APIException('you need to specify the phone', status_code=400)
   queue.enqueue(body)
   return "ok", 200

return jsonify(user)
@app.route('/next', methods=['GET'])
def deleteQueue():
   queue.dequeue()
   return jsonify(queue.get_queue())
@app.route('/all', methods=['GET'])
def getAllFromList():
   return jsonify(queue.get_queue())


# Download the helper library from https://www.twilio.com/docs/python/install

@app.route('/process', methods=['GET'])
def process():

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'ugfghjiuytrdfghjiuytresdfghuytr' #copiar el ID que me dio Twilio al crear mi cuenta
    auth_token = ';lkjhtsdszxcghjkl;[piyuesdzxfgh'    #este token tambien
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body="Join Earth's mightiest heroes. Like Kevin Bacon.", #este mensaje se puede modificar
        from_='+12222222222', #este numero me lo dio Twilio
        to='+13333333333'     #aqui iria el del cliente donde se enviara el mensaje
    )

    # print(message.sid)
    return ('ciao'), 200


@app.route('/person', methods=['POST', 'GET'])
def handle_person():
    """
    Create person and retrieve all persons
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'username' not in body:
            raise APIException('You need to specify the username', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)

        user1 = Person(username=body['username'], email=body['email'])
        db.session.add(user1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_people = Person.query.all()
        all_people = list(map(lambda x: x.serialize(), all_people))
        return jsonify(all_people), 200

    return "Invalid Method", 404


@app.route('/person/<int:person_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_person(person_id):
    """
    Single person
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)

        if "username" in body:
            user1.username = body["username"]
        if "email" in body:
            user1.email = body["email"]
        db.session.commit()

        return jsonify(user1.serialize()), 200

    # GET request
    if request.method == 'GET':
        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        return jsonify(user1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        user1 = Person.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(user1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT)
