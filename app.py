
from flask import Flask, request, jsonify, render_template, Response, url_for, send_from_directory
from pipeline.pipeline import Pipeline, InvalidRequestException
import json
from datetime import datetime
from werkzeug.exceptions import HTTPException, BadRequest
from flask_swagger_ui import get_swaggerui_blueprint
from representations import *
from content_negotiation import *

app = Flask(__name__, static_folder='static')
pipeline = Pipeline("sentence-transformers/distiluse-base-multilingual-cased-v1",16)

SWAGGER_URL = '/docs' 
OPEN_API_FILE = '/openapi.yml' 

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    OPEN_API_FILE,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)

@app.route("/predict",methods=["POST"])
@produces(MIME_TYPE_APPLICATION_JSON,MIME_TYPE_RESULTS_V1_JSON, default_mime_type=MIME_TYPE_RESULTS_V1_JSON)
@consumes(MIME_TYPE_JOBS_V1_JSON,MIME_TYPE_APPLICATION_JSON)
def api():
    args = request.args
    top_answers_n = None

    if "top" in args and args["top"]:
        top_answers_n = int(args["top"])
    try:
        response_payload = pipeline.process(request.json,top_answers_n)
        response_payload["_links"] = [
            {
                "rel":"prediction",
                "href": url_for("api")
            },
            {
                "rel":"base",
                "href": url_for("base")
            }
        ]

        response = jsonify(response_payload)
        #response.mimetype=MIME_TYPE_RESULTS_V1_JSON
        return response
    except InvalidRequestException as e:
        raise BadRequest(description = e.message)


@app.route("/",methods=["GET"])
@produces(MIME_TYPE_APPLICATION_XHTML_XML,MIME_TYPE_TEXT_HTML,MIME_TYPE_HYPERMEDIA_V1_JSON,MIME_TYPE_APPLICATION_JSON)
def base():
    if MIME_TYPE_APPLICATION_XHTML_XML in list(request.accept_mimetypes.values()) or MIME_TYPE_TEXT_HTML in list(request.accept_mimetypes.values()):
        return render_template("index.html")
    else:
        response = jsonify({
            "_links":[
                {
                    "rel":"prediction",
                    "href": url_for("api")
                },
                {
                    "rel":"self",
                    "href": url_for("base")
                }
            ]
        })
        response.mimetype = MIME_TYPE_HYPERMEDIA_V1_JSON
        return response

@app.route('/openapi.yml')
def send_docs():
    return send_from_directory(app.static_folder, 'OpenAPI.yml')

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "status": e.code,
        "error": e.name,
        "message": e.description,
        "path": request.url,
        "links_":[
                {
                    "rel":"base",
                    "href": url_for("base")
                },
                {
                    "rel":"docs",
                    "href": SWAGGER_URL
                }
            ]
    })
    response.content_type = MIME_TYPE_ERROR_V1_JSON
    return response

'''
if __name__ == '__main__':
    pipeline = Pipeline("sentence-transformers/distiluse-base-multilingual-cased-v1",1000)
    
    input = {
        "jobs":[
            {
                "jobId": "j1",
                "name": "testSchema",
                "targetSentences": [
                    "The key for accessing this Web API", 
                    "The name of the city",
                    "The city's unique identifier",
                    "The name of the country",
                    "The distance north or south of the equator, also called latitude",
                    "The distance west or east of the prime meridian, also called longitude", 
                    "The unique postal code of the location, also known as ZIP",
                    "The current state of the application",
                    "The unit system used for measurements embedded in this resource"
                ], 
                "sentences":[
                    {
                        "sentenceId": "s1",
                        "name": "first sentence",
                        "value": "The ZIP"
                    },
                    {
                        "sentenceId": "s2",
                        "name": "second sentence",
                        "value": "The auth token"
                    }
                    
                ]
            },
            {
                "jobId": "j2",
                "name": "multiLanguageTest",
                "targetSentences": [
                    "Web API for multilingual textual similarity",
                    "Web-API für mehrsprachige textuelle Ähnlichkeit",
                    "API web para la similitud textual multilingüe",
                    "API web per la similarità del testo multilingue",
                    "My name is John Doe",
                    "Ich heiße John Doe",
                    "Me llamo John Doe",
                    "Mi chiamo John Doe",
                    "Mio nome è John Doe",
                    "Il mio nome è John Doe"
                ], 
                "sentences":[
                    {
                        "sentenceId": "s1",
                        "value": "Eine Schnittstelle für mehrsprachige Dinge"
                    },
                    {
                        "sentenceId": "s2",
                        "name": "second sentence",
                        "value": "Der Name einer Person"
                    }
                    
                ]
            }
        ]
    }
    results = pipeline.process(input)
    print(json.dumps(results, indent=2))
'''