import requests
import datetime

def search(cnpj) -> dict:
    symbols = ["-", "/", "."]
    for s in symbols:
        cnpj = cnpj.replace(s, "")

    # url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    url = f"https://open.cnpja.com/office/{cnpj}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()


            fundacao_date = datetime.datetime.strptime(data["founded"], "%Y-%m-%d").date()
            hoje = datetime.date.today()
            tempo_de_vida = (hoje - fundacao_date).days  # diferença em dias


            print(f'Nome: {data["company"]["name"]}', f'Capital Social: {data["company"]["equity"]}')
            return {
                "empresa": {
                    "razao_social": data["company"]["name"],
                    "capital_social": data["company"]["equity"],
                    "nome_fantasia": data.get("alias"),
                },
                "tempo_de_vida": {
                    "data_fundacao": fundacao_date,
                    "dias": (hoje-fundacao_date).days,
                    "anos": round(tempo_de_vida/365,1),
                },
                "contato": {
                    "telefone": data["phones"][0]["area"]+data["phones"][0]["number"],
                    "email": data["emails"][0]["address"],
                    "dominio": data["emails"][0]["domain"]
                }
            }

        else:
            print(f"Erro: Status code {response.status_code}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")


# print(search("32161525000103"))