from flask import Flask, request, jsonify
from flask_restful import Api, Resource, request
from components import whitelist, blacklist, popularityrank
from flask_cors import CORS
import requests

app = Flask("ListAPI")
CORS(app)
api = Api(app)

class WhitelistAPI(Resource):
    def get(self):
        args = request.args
        url = args.get("url")

        if url == "" or url is None:
            return jsonify({"error": "URL not provided"})
        # Check if URL is in whitelist
        result = whitelist.check_url(url)
        return jsonify(result)
    

class BlacklistAPI(Resource):
    def get(self):
        args = request.args
        url = args.get("url")

        if url == "" or url is None:
            return jsonify({"error": "URL not provided"})
        
        # Check if URL is in blacklist
        result = blacklist.check_url(url)
        return jsonify(result)    

class PopularityRankAPI(Resource):
    def get(self):
        args = request.args
        url = args.get("url")
        
        if url == "" or url is None:
            return jsonify({"error": "URL not provided"})
        
        # Get PageRank for URL
        result = popularityrank.get_page_rank(url)
        return jsonify(result)

class fetch_html(Resource): # For fetching HTML content of a URL
    def get(self):
        args = request.args
        url = args.get("url")
        
        if url == "" or url is None:
            return jsonify({"error": "URL not provided"})
        
        try:
            response = requests.get(url)
            response.raise_for_status()

            return response.text
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)})

api.add_resource(WhitelistAPI, '/whitelist')
api.add_resource(BlacklistAPI, '/blacklist')
api.add_resource(PopularityRankAPI, '/popularityrank')
api.add_resource(fetch_html, '/fetch_html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)