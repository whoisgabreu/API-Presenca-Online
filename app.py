from flask import Flask, request, jsonify
from modules.google import GoogleTransparency
from modules.google import GoogleBusiness
from modules.cnpja_api import search

app = Flask(__name__)

API_KEY = "BANANINHA123"

def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if key != API_KEY:
            return jsonify(
                {"error": "Unauthorized"}
            ), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/analise/presenca-online", methods=["GET"])
@require_api_key
def presenca_online():

    try:
        cnpj = request.args.get("cnpj")

        business_info = search(cnpj = cnpj)
        # print("Info 1:",business_info)
        business_info = GoogleTransparency().analyse(business_info)
        # print("Info 2:",business_info)
        # business_info = GoogleBusiness().analyse(business_info)
        # print("Info 3:",business_info)


        return jsonify(business_info)
    
    except Exception as e:

        return jsonify(
            {
                "erro": f"{e}"
            }
        ), 400
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
