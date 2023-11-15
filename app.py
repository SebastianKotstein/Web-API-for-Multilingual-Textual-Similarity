
from flask import Flask, request, jsonify
from pipeline.s_model import SModel


app = Flask(__name__)
model = SModel("sentence-transformers/distiluse-base-multilingual-cased-v1",16)

@app.route("/",methods=["GET"])
def api():
    model.predict()
    return ""