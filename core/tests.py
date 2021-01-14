from django.test import TestCase

# Create your tests here.
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class Test(View):
    @classmethod
    def post(self, request, *args, **kwargs):
        text = [json.loads(request.body)['text']]
        tokenizer = RegexTokenizer()
        model = FastTextSocialNetworkModel(tokenizer=tokenizer)
        result = model.predict(text, k=5)[0]
        negative = result['negative']
        positive = result['positive']
        neutral = result['neutral']
        min_negative = 0.3
        min_pos