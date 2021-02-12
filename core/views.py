# Create your views here.
import json
import re

from django.http import HttpResponse, JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

min_negative = 0.5
min_positive = 0.5
min_neutral = 0.8


def get_rate(result):
    negative = result['negative']
    positive = result['positive']
    neutral = result['neutral']
    # st = ' n: ' + str(negative) + ' p: ' + str(positive) + ' neu: ' + str(neutral) + ' n/neu: ' + str(negative/neutral)+ ' p/neu: ' + str(positive/neutral)
    if neutral >= min_neutral:
        return "neutral"
    # if negative > min_negative or negative/neutral > min_negative or positive > min_positive or positive/neutral > min_positive:
    if negative > min_negative or positive > min_positive:
        if negative > positive:
            return "neutral"
        else:
            return "positive"
    if negative > positive and negative > neutral:
        return "negative"
    if positive > negative and positive > neutral:
        return "positive"
    return "neutral"


def remove_html_tags(text):
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


@method_decorator(csrf_exempt, name='dispatch')
class PostDostoevsky(View):
    @classmethod
    def post(cls, request, *args, **kwargs):
        ids = []
        texts = []
        for data in json.loads(request.body):
            ids.append(data['id'])
            texts.append(remove_html_tags(data['text']))

        dost_results = model.predict(texts, k=5)
        res = []
        for i in range(len(ids)):
            res.append({'id': ids[i], 'rate': get_rate(dost_results[i])})
        return HttpResponse(json.dumps(res), content_type='application/json')
