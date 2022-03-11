"""
TEST API
""" # noqa: E501
import os
import sys
from flask import Flask, jsonify, url_for, render_template, redirect
from flask_cors import CORS
from apifairy import APIFairy, response, arguments, body
from brewery.blueprint import api, brewery_blueprint
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from flask_servant import create_app, run_app, get_socket
from flask_servant.schema import create_schema
from brewery.models import Brewery, session
from flask_servant.orm import query_table

# app = Flask(__name__)
app = create_app(__name__, template_folder='./templates', secret_key='test') # noqa: F401
cors = CORS(app)
apifairy = APIFairy(app)
print('apifairy: ', apifairy)
socket = get_socket()


app.register_blueprint(brewery_blueprint)
print('app: ', app)
print('app secret: ', app.config['SECRET_KEY'])

@socket.on('message')
def handle_message(msg):
    print(f'received message: "{msg}"')


@socket.on('connect')
def on_connect():
    socket.emit('my response', {'data': 'Connected'})

@app.route('/home')
def hello():
    return render_template('main.html')
    # return jsonify({ 'message': 'hello world' })

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return jsonify({ 'links': links})

brewery_schema = create_schema(Brewery, session=session)
@app.route('/breweries/find')
@response(brewery_schema(many=True))
@arguments(brewery_schema)
def find_breweries(brewery):
    print('brewery is: ', brewery)
    return query_table(Brewery, session, **brewery_schema().dump(brewery))

@app.route('/')
def redirect_to_swagger():
    print('redirect: ', redirect(url_for='/help'))
    return redirect(url_for='/help')


if __name__ == '__main__':
    # app.run()
    run_app(port=5000, debug=True)
    print('running?')