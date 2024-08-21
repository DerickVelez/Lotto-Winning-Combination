from bs4 import BeautifulSoup
import requests

url = "https://www.pcso.gov.ph"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}#fake agent
 
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.content, "html.parser")
results = soup.find(id="cphContainer_LottoResults_pDrawResults")
print(results.prettify())


lotto_types = ["cphContainer_LottoResults_ultra", "cphContainer_LottoResults_grand",
         "cphContainer_LottoResults_super", "cphContainer_LottoResults_mega", "cphContainer_LottoResults_lotto"]

lotto_elements = ['1','2','3','4','5','6','Amount','Winner', 'Date']

list_of_combinations = []

for lotto_type in lotto_types:
    for lotto_element in lotto_elements:
        result = soup.find("span",id= f"{lotto_type}{lotto_element}")
        list_of_combinations.append(result.text)   
        

print(list_of_combinations)