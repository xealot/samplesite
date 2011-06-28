import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from forms import LoginForm, SampleForm
from extra.middleware.abort import abort
from extra.utils.view import render_to
from extra.rpc import rpc
#from extra.uspsvalidation import usps_conn
from sample.models import Product, Sample

try:
    import simplejson as json
except ImportError:
    import json




@render_to('index.html')
def index(request):
    return {}

@render_to('start.html')
def start(request):
    credit = rpc.bank.amount(settings.CREDIT_TYPE)
    return {'products': get_products(), 'credit': credit}

@render_to('step_one.html')
def step_one(request, code):
    request.step_num = 1
    user = request.user
    form = SampleForm(request.POST)

    if request.method == 'POST' and form.validate():
        #Store main.
        sample = Sample.objects.create(
            user_ref=user.user_ref,
            sample_data=form.data
        )
        messages.add_message(request, messages.SUCCESS, 'Sample Created and Added to Cart')
        if form.data.get('country') == 'US':
            return redirect(reverse('step_one_validate', kwargs={'pending_id': sample.pk}))
        return redirect(reverse('step_two'))
    return {'form': form}

@render_to('step_one.html')
def step_one_edit(request, pending_id):
    request.step_num = 1
    form = SampleForm(request.POST)

    try:
        pending = Sample.objects.get(pk=pending_id)
    except Sample.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Sample Not Available to Edit')
        return redirect(reverse('step_two'))

    if request.method == 'POST' and form.validate():
        pending.sample_data = form.data
        pending.save()
        if form.data.get('country') == 'US':
            return redirect(reverse('step_one_validate', kwargs={'pending_id': pending_id}))
        messages.add_message(request, messages.SUCCESS, 'Sample Saved')
        return redirect(reverse('step_two'))
    else:
        form = SampleForm(**pending.sample_data) #Since this is a dictionary, not an object... KW population.
    return {'form': form, 'obj': pending}

@render_to('step_one_validate.html')
def step_one_validate(request, pending_id):
    request.step_num = 1

    try:
        pending = Sample.objects.get(pk=pending_id)
    except Sample.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Sample Not Available to Validate')
        return redirect(reverse('start'))

    sample = pending.sample_data

    #Verify Address with USPS if Country is US
    if sample.get('country') != 'US':
        return redirect(reverse('step_two'))

    result = usps_conn.check_address(street=sample.get('address1'),
                                    city=sample.get('city'),
                                    state=sample.get('state'),
                                    zip=sample.get('postal'),
                                    unit=sample.get('address2'))

    if request.method == 'POST':
        sample.update({'address1': result.street,
                       'address2': result.unit,
                       'city': result.city,
                       'state': result.state,
                       'postal': result.zip})
        pending.sample_data = sample
        pending.save()
        return redirect(reverse('step_two'))

    return {'sample': sample, 'addr': result, 'id': pending_id}

@render_to('step_two.html')
def step_two(request):
    request.step_num = 2
    pending, count = has_samples(request, 'start')

    if request.method == 'POST':
        request.session['cart'] = [p.pk for p in pending]
        return redirect(reverse('step_three'))
    return {'pending': pending, 'count': count, 'cost': SAMPLE_PRICE, 'total': SAMPLE_PRICE*count}

def step_three(request):
    pass

#This shoudl be on referenced from the HP rig in the JS. Not proxied.
nonalnum = re.compile(r'[^0-9A-Za-z]')
def ajax_zip_lookup(request, country, zip):
    zipcode = rpc.geo.postalLookup(country, nonalnum.sub('', zip), _safe=True)
    if zipcode is not None:
        return HttpResponse(json.dumps(zipcode))
    raise Http404

#BOILERPLATE
def sign_up(request):
    pass

@render_to('login.html')
def sign_in(request):
    login_form = LoginForm(request.POST)

    if request.method == 'POST' and login_form.validate():
        user = authenticate(username=login_form.username.data, password=login_form.password.data)
        print user
        if user is not None:
            login(request, user)
            request.session['user'] = user
            messages.add_message(request, messages.SUCCESS, 'Login Successful')
            return redirect(reverse('start'))
        else:
            messages.add_message(request, messages.ERROR, 'Login Failed')

    return dict(login_form=login_form)

def sign_out(request):
    logout(request)
    return redirect(reverse('index'))



import braintree, re


def get_products():
    return Product.on_site.filter().order_by('priority')

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    "ss37wjw57f8wz9k4",
    "y5jq7rw2c8p52ngf",
    "mgqq3836tjc6sq55"
)
# Allow unsafe SSL, removes dependency on PycURL C-ext.
braintree.Configuration.use_unsafe_ssl = True

TZ_ATTR = 'tzinfo'


def has_samples(request, view_name):
    user = request.user

    pending = Sample.objects.select_related('product').filter(user_ref=user.user_ref, purchased=False)
    count = len(pending)
    if count <= 0:
        messages.add_message(request, messages.INFO, 'You do not have any samples yet, let\'s create one.')
        abort(redirect(reverse(view_name)))
    return pending, count

def verify_cart(view_name):
    auth_db()
    count, cart = 0, ()
    cart_ids = session.get('cart', ())
    if cart_ids:
        cart = g.db.samples.find({'_id': {'$in': [ObjectId(id) for id in cart_ids]}})
        count = cart.count()
    if count <= 0:
        flash('You must have a few samples before completing the purchase.', 'error')
        abort(redirect(view_name))
    return cart, cart.count()