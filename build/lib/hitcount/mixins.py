from json import JSONEncoder
import json
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.views.generic import FormView, View



class LazyEncoder(JSONEncoder):


    """Encodes django's lazy i18n strings.
    Used to serialize translated strings to JSON, because
    simplejson chokes on it otherwise.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return obj

