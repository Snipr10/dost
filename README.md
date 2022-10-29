# Docker
docker build -t dost .

docker run -d --name dost-container -p 8000:8000 dost



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
