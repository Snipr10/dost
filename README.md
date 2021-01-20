## ENV (if needed)
    python3 -m venv venv
    source ./venv/bin/activate
    
## Requirements
pip3 install -r requirements.txt

## Dosotoevsky data (https://pypi.org/project/dostoevsky/)
python3 -m dostoevsky download fasttext-social-network-model

## Run 
python3 manage.py runserver

## Example
POST http://127.0.0.1:8000/api/text/
body 


[ {
    "text": "17 площадок оборудованы освещением по обращениям жителей, 3 из них - по поручению губернатора Александра Беглова.",
    "id" : 1
}]

result 

[
    {
        "id": 1,
        "rate": "neutral"
    }
]