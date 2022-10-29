import re
import uvicorn

from fastapi import FastAPI, Request
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from starlette.responses import JSONResponse

app = FastAPI()
tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

min_negative = 0.4
min_positive = 0.4
min_neutral = 0.85


def get_rate(result):
    try:
        negative = result['negative']
        positive = result['positive']
        neutral = result['neutral']
        if neutral >= min_neutral and neutral >= positive and neutral >= negative:
            return "neutral"
        if negative > min_negative or positive > min_positive:
            if negative > positive:
                return "negative"
            else:
                return "positive"
        if negative > positive and negative > neutral:
            # return "negative"
            return "neutral"

        if positive > negative and positive > neutral:
            return "positive"
        return "neutral"
    except Exception:
        return "neutral"


def remove_html_tags(text):
    try:
        if text is None:
            return ""
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        clean = re.compile(u'('
                           u'\ud83c[\udf00-\udfff]|'
                           u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
                           u'[\u2600-\u26FF\u2700-\u27BF])+',
                           re.UNICODE)
        return re.sub(clean, '', text).replace("", "").replace(':)', '').replace(':D', '').replace(":(", "").replace(":-(",
                                                                                                                     "")
    except Exception:
        return ""


@app.post('/api/text')
async def index(request: Request):
    ids = []
    texts = []
    body_json = await request.json()

    for data in body_json:
        ids.append(data['id'])
        texts.append(remove_html_tags(data['text']))

    dost_results = model.predict(texts, k=5)
    res = []
    for i in range(len(ids)):
        res.append({'id': ids[i], 'rate': get_rate(dost_results[i])})
    return JSONResponse(content=res)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
