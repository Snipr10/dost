# Create your views here.
import json
import math
import re

from django.http import HttpResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

tokenizer_sb = GPT2Tokenizer.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2")
gpt3_large_sb = GPT2LMHeadModel.from_pretrained("sberbank-ai/rugpt3large_based_on_gpt2")


tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

min_negative = 0.5
min_positive = 0.5
min_neutral = 0.6


def get_rate(result, texts):
    negative = result['negative']
    positive = result['positive']
    neutral = result['neutral']
    if neutral >= min_neutral:
        return "neutral"
    if negative > min_negative or positive > min_positive:
        if negative > positive:
            return "neutral"
        else:
            return "positive"
    if negative > positive and negative > neutral:
        return "negative"
    if positive > negative and positive > neutral:
        return "positive"

    sentence_positive = 'довольна:' + texts
    sentence_negative = 'недовольна:' + texts

    list_sent = [sentence_positive, sentence_negative]
    ppl_values = []
    try:
        for sentence in list_sent:
            encodings = tokenizer_sb(sentence, return_tensors='pt')

            input_ids = encodings.input_ids
            with torch.no_grad():
                outputs = gpt3_large_sb(input_ids=input_ids, labels=input_ids)
            loss = outputs.loss
            ppl = math.exp(loss.item() * input_ids.size(1))
            ppl_values.append(ppl)
        if ppl_values[0] > ppl_values[1]:
            return 'negative'
        elif ppl_values[0] < ppl_values[1]:
            return 'positive'
    except Exception:
        pass
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
            res.append({'id': ids[i], 'rate': get_rate(dost_results[i], texts[i])})
        return HttpResponse(json.dumps(res), content_type='application/json')
