Django-HitCount
===============

Basic app that allows you to track the number of hits/views for a particular
object.

For more information you can view comments in the source code or visit:

<http://damontimm.com/code/django-hitcount/>

What it is not
--------------

This is not meant to be a user tracking app (see: [django-tracking][1]) or a
comprehensive site traffic monitoring tool (see: Google Analytics).

It's meant to serve as a simple hit counter for chosen objects with a couple
useful features (user-agent, session, and IP tracking) and tools to help you
on your way.

Contribute
----------

I would love to make it better.  Please fork and push.  Some fun additions
might be [1] a nice graphing utility for the admin site, [2] another approach
to caputring a hit (other than jQuery), and [3] a cleanup tool that can remove
Hit objects after a certain period (cron job).

Installation:
-------------

Simplest way to formally install is to run:

    ./setup.py install

Or, you could do a PIP installation:

    pip install -e git://github.com/scottwrobinson/django-hitcount.git#egg=django-hitcount

Or, you can link the source to your `site-packages` directory.  This is useful
if you plan on pulling future changes and don't want to keep running
`./setup.py install`.

    cd ~/src
    git clone https://github.com/scottwrobinson/django-hitcount.git
    sudo ln -s `pwd`/django-hitcount/hitcount `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/hitcount


Then modify your settings.py, adding the package hitcount in INSTALLED_APPS

    INSTALLED_APPS = (
        '...',
        'hitcount',
    )
 

There are three additional settings you can add to your settings.py file:

    HITCOUNT_KEEP_HIT_ACTIVE = { 'days': 7 }
    HITCOUNT_HITS_PER_IP_LIMIT = 0
    HITCOUNT_EXCLUDE_USER_GROUP = ( 'Editor', )


HITCOUNT_KEEP_HIT_ACTIVE: is the number of days, weeks, months, hours, etc (timedelta kwargs), that an Hit is kept ‘active’. If a Hit is ‘active’ a repeat viewing will not be counted. After the active period ends, however, a new Hit will be recorded. You can decide how long you want this period to last …

HITCOUNT_HITS_PER_IP_LIMIT: limit the number of ‘active’ hits from a single IP address. 0 means that it is unlimited. You may want to set this, or not.

HITCOUNT_EXCLUDE_USER_GROUP: don’t count any hits from certain logged in users. In the example above, I don’t want any of my editors inflating the total Hit count.


You need to add one line to your urls.py file.
----------------------------------------------
    urlpatterns = patterns('',
        url(r'^ajax/hit/$', # you can change this url if you would like
            update_hit_count_ajax,
            name='hitcount_update_ajax'), # keep this name the same


Edit your templates
-------------------
    {% load hitcount_tags %}
    <script type="text/javascript">
        var csrf_token = '{{ csrf_token }}';
        $(document).ready(function() {
            {% get_hit_count_javascript for object %}
        });
    </script>


Display the hits!
-----------------
- Return total hits for an object:
  {% get_hit_count for [object] %}
 
- Get total hits for an object as a specified variable:
  {% get_hit_count for [object] as [var] %}
 
- Get total hits for an object over a certain time period:
  {% get_hit_count for [object] within ["days=1,minutes=30"] %}
 
- Get total hits for an object over a certain time period as a variable:
  {% get_hit_count for [object] within ["days=1,minutes=30"] as [var] %}