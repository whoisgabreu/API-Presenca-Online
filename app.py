from flask import Flask, request, jsonify
from modules.google import GoogleTransparency
from modules.google import GoogleBusiness
from modules.cnpja_api import search

app = Flask(__name__)


@app.route("/analise/presenca-online", methods=["GET"])
def presenca_online():

    try:
        cnpj = request.args.get("cnpj")

        business_info = search(cnpj = cnpj)
        print("Info 1:",business_info)
        business_info = GoogleTransparency().analyse(business_info)
        print("Info 2:",business_info)
        
        business_info = GoogleBusiness().analyse(business_info)
        print("Info 3:",business_info)


        return jsonify(business_info)
    
    except Exception as e:

        return jsonify(
            {
                "erro": f"{e}"
            }
        ), 400
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
