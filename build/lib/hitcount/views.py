import json

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.generic import View
from core.mixins import AjaxableResponseMixin
from core.tools import LazyEncoder

from .utils import get_ip
from .models import Hit, HitCount, BlacklistIP, BlacklistUserAgent
from django.utils.translation import ugettext_lazy as _

def _update_hit_count(request, hitcount):
    """
    Evaluates a request's Hit and corresponding HitCount object and,
    after a bit of clever logic, either ignores the request or registers
    a new Hit.

    This is NOT a view!  But should be used within a view ...

    Returns True if the request was considered a Hit; returns False if not.
    """
    user = request.user

    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key
    ip = get_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    hits_per_ip_limit = getattr(settings, 'HITCOUNT_HITS_PER_IP_LIMIT', 0)
    exclude_user_group = getattr(settings, 'HITCOUNT_EXCLUDE_USER_GROUP', None)

    # first, check our request against the blacklists before continuing
    if BlacklistIP.objects.filter(ip__exact=ip) or BlacklistUserAgent.objects.filter(
            user_agent__exact=user_agent):
        return False

    # second, see if we are excluding a specific user group or not
    if exclude_user_group and user.is_authenticated():
        if user.groups.filter(name__in=exclude_user_group):
            return False

    # start with a fresh active query set (HITCOUNT_KEEP_HIT_ACTIVE )
    qs = Hit.objects.filter_active()

    # check limit on hits from a unique ip address (HITCOUNT_HITS_PER_IP_LIMIT)
    if hits_per_ip_limit:
        if qs.filter(ip__exact=ip).count() > hits_per_ip_limit:
            return False

    # create a generic Hit object with request data
    hit = Hit(session=session_key, hitcount=hitcount, ip=get_ip(request),
              user_agent=request.META.get('HTTP_USER_AGENT', '')[:255], )

    # first, use a user's authentication to see if they made an earlier hit
    if user.is_authenticated():
        target_object = hitcount.get_content_object_target()
        if hasattr(target_object, 'author') and target_object.author == request.user:
            return False
        if not qs.filter(user=user, hitcount=hitcount):
            hit.user = user #associate this hit with a user
            hit.save()
            return True

    # if not authenticated, see if we have a repeat session
    else:
        if not qs.filter(session=session_key, hitcount=hitcount):
            hit.save()
            # forces a save on this anonymous users session
            request.session.modified = True

            return True

    return False


def json_error_response(error_message):
    return HttpResponse(json.dumps(dict(success=False, error_message=error_message)))


# TODO better status responses - consider model after django-voting,
# right now the django handling isn't great.  should return the current
# hit count so we could update it via javascript (since each view will
# be one behind).

class UpdateHitCountAjax(View):
    """
    Ajax call that can be used to update a hit count.

    Ajax is not the only way to do this, but probably will cut down on
    bots and spiders.

    See template tags for how to implement.
    """

    # make sure this is an ajax request

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context, cls=LazyEncoder)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get(self,request):
        data={}
        data['error'] = {}
        data['error']['message'] = _("Hits counted via POST only.")
        data['error']['title'] = _("You did wrong!")
        return self.render_to_json_response(data,status=405)

    def post(self,request):
        hitcount_pk = self.request.POST.get('hitcount_pk')
        data={}
        try:
            hitcount = HitCount.objects.get(pk=hitcount_pk)
        except:
            return HttpResponseBadRequest("HitCount object_pk not working")

        result = _update_hit_count(request, hitcount)
        data['success'] = {}
        data['success']['title'] = _("Hit count")
        if result:
            data['success']['status'] = _("success")
        else:
            data['success']['status'] = _("no hit recorded")

        return self.render_to_json_response(data, status=200)
