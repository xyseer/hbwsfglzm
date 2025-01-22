import flask
from flask import Flask, request, render_template, redirect
from datetime import datetime
from auto_fill import autofill

app = Flask(__name__, static_folder='/static')


@app.route("/whopper", methods=["GET"])
def get():
	shop = "21090"
	if request.args.get("shop"):
		shop = request.args["shop"]
	locale = "CA"
	if request.args.get("locale"):
		shop = request.args["locale"]

	time = "12:00PM01-01-2024"
	if request.args["time"]:
		time = request.args["time"]

	time_d = datetime.strptime(time, "%I:%M%p%m-%d-%Y")
	code = autofill(shop, locale, time_d)
	return code
