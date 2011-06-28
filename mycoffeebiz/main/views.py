import json
import re
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.views.generic.simple import redirect_to
from extra.rpc import rpc
from extra.lib.ng_braintree import braintree
from extra.utils.view import render_to
from mycoffeebiz.main.forms import SampleForm


@render_to('index.html')
def index(request):
    # Verify redirect result and show errors if there are any.
    submit_url = braintree.TransparentRedirect.url()
    
    if 'hash' in request.GET:
        try:
            result = braintree.TransparentRedirect.confirm(request.META['QUERY_STRING'])
        except braintree.exceptions.not_found_error.NotFoundError:
            # There is NO redirect data here.
            return redirect_to(request, reverse('index'), permanent=False)

        if result.is_success:
            print 'SUCCESS'
            #return redirect(url_for('complete', tran_id=result.transaction.id))
        submitted = result.params['transaction']
        form = SampleForm(
            transaction__customer__email=                       submitted['customer']['email'],
            transaction__customer__phone=                       submitted['customer']['phone'],
            transaction__billing__extended_address=            submitted['billing']['extended_address'],
            transaction__billing__street_address=              submitted['billing']['street_address'],
            transaction__billing__postal_code=          submitted['billing']['postal_code'],
            transaction__billing__locality=             submitted['billing']['locality'],
            transaction__billing__region=               submitted['billing']['region'],
            transaction__billing__country_code_alpha2=  submitted['billing']['country_code_alpha2'],
            transaction__credit_card__cardholder_name=          submitted['credit_card']['cardholder_name'],
            #Special Case
            expdate=(submitted['credit_card']['expiration_month'], submitted['credit_card']['expiration_year']),
        )

        #Build Error Structure
        #What we're doing here is just constructing a bunch of functions to add to the field validators list.
        from wtforms import validators
        def rigged_validator(msg):
            def _throw_it(form, field):
                raise validators.StopValidation(msg)
            return _throw_it

        for i in ('customer', 'billing', 'credit_card'):
            for error in result.errors.for_object('transaction').for_object(i):
                formfield = getattr(form, 'transaction__%s__%s' % (i, error.attribute), None)
                if formfield is not None:
                    formfield.validators.insert(0, rigged_validator(error.message))
        form.validate()
    else:
        form = SampleForm(request.POST)
        if request.method == 'POST':
            pass

        tr_data = braintree.Transaction.tr_data_for_sale({
            "transaction": {
                "type": "sale",
                "amount": 9.99,
                "options": {
                    "submit_for_settlement": True,
                    "add_billing_address_to_payment_method": True,
                }
            }
        }, request.build_absolute_uri(reverse('index'))
        )
        form.tr_data.data = tr_data

    return {'form': form, 'submit_url': submit_url}

@render_to('thankyou.html')
def thankyou(request):
    return {}


def step_three(check=None):
    g.step = 3
    user_id = g.user.get('user_ref')
    cart, count = verify_cart('step_two')

    if count <= 0:
        flash('You must have a few samples before completing the purchase.', 'error')
        return redirect('step_two')

    try:
        customer = braintree.Customer.find(user_id)
        if customer is not None:
            #There is a saved customer, we need to show a completely different form/ui here.
            return render_template('step_three_saved.html', customer=customer)
    except braintree.exceptions.not_found_error.NotFoundError:
        pass

    if check == 'verify':
        # Verify redirect result and show errors if there are any.
        try:
            result = braintree.TransparentRedirect.confirm(request.query_string)
        except braintree.exceptions.not_found_error.NotFoundError:
            # There is NO redirect data here.
            return redirect(url_for('step_three'))
        if result.is_success:
            return redirect(url_for('complete', tran_id=result.transaction.id))
        submitted = result.params['transaction']
        form = CheckoutForm(
            transaction__customer__email=               submitted['customer']['email'],
            transaction__customer__phone=               submitted['customer']['phone'],
            transaction__billing__postal_code=          submitted['billing']['postal_code'],
            transaction__billing__locality=             submitted['billing']['locality'],
            transaction__billing__region=               submitted['billing']['region'],
            transaction__credit_card__cardholder_name=  submitted['credit_card']['cardholder_name'],
            #Special Case
            expdate=(submitted['credit_card']['expiration_month'], submitted['credit_card']['expiration_year'])
        )

        #Build Error Structure
        #What we're doing here is just constructing a bunch of functions to add to the field validators list.
        from wtforms import validators
        def rigged_validator(msg):
            def _throw_it(form, field):
                raise validators.StopValidation(msg)
            return _throw_it

        for i in ('customer', 'billing', 'credit_card'):
            for error in result.errors.for_object('transaction').for_object(i):
                formfield = getattr(form, 'transaction__%s__%s' % (i, error.attribute), None)
                if formfield is not None:
                    formfield.validators.insert(0, rigged_validator(error.message))
        form.validate()

        #from pprint import pprint
        #pprint(result.errors.errors.data)
        #pprint(form.errors)

        flash(jinja2.Markup(u'There was an error processing your credit card. You must correct the information and <strong>re-enter your credit card number and your card code.</strong>'), 'error')
    elif request.method == 'POST':
        #Just for testing, we do not submit to ourselves with CC info
        form = CheckoutForm(request.form)
        if form.validate():
            flash('Success?')
    else:
        form = CheckoutForm(request.form, transaction__customer__email=g.user['email'])

    this_year = datetime.datetime.today().year
    form.expdate.years = [(v, v) for v in range(this_year, this_year+6)]
    form.expdate.months = [('%02d' % v, '%02d' % v) for v in range(1, 13)]

    tr_data = braintree.Transaction.tr_data_for_sale({
        "transaction": {
            "type": "sale",
            "amount": SAMPLE_PRICE*count,
            "customer": {
                "id": g.user['user_ref']
            },
            "options": {
                "submit_for_settlement": False,
                "add_billing_to_payment_method": True,
            }
        }
    }, "%s%s" % (request.url_root[:-1], url_for('step_three', check='verify'))
    )
    form.tr_data.data = tr_data
    submit_url = braintree.TransparentRedirect.url()

    return render_template('step_three.html', **{'post_url': submit_url, 'form': form, 'cart': cart,
            'count': count, 'cost': SAMPLE_PRICE, 'total': SAMPLE_PRICE*count})


def complete(tran_id=None):
    """
    IF tran_id is specified, we are landing in this function after a Braintree's
    transparent redirect. If the tran_id is None, this means there should be a
    saved customer, and to complete the transaction in a single step.
    """
    user_id = g.user.get('user_ref')
    cart, count = verify_cart('step_two')

    if tran_id is None:
        # Create a transaction from the vault, based on the current cart.
        try:
            #customer =
            braintree.Customer.find(user_id)
        except braintree.exceptions.not_found_error.NotFoundError:
            flash('Could not find saved data.', 'error')
            redirect(url_for('step_three'))
        result = braintree.Transaction.sale({
            "amount": '%.2f' % (SAMPLE_PRICE*count),
            "customer_id": user_id,
        })
        if not result.is_success:
            flash('There was a problem completing your order with saved payment information. %s' % result.message, 'error')
            return redirect(url_for('step_three'))
        tran_id = result.transaction.id

    try:
        result = braintree.Transaction.submit_for_settlement(tran_id)
    except braintree.exceptions.not_found_error.NotFoundError:
        flash('Transaction not found.', 'error')
    except Exception, e:
        flash('Uncaught Exception, %s. Resetting.' % str(e), 'error')
        braintree.Transaction.void(tran_id)
        return redirect(url_for('step_three'))
    else:
        if not result.is_success:
            flash('There was a problem finalizing your order. %s' % result.message, 'error')
            return redirect(url_for('step_three'))
        #SUCCESS IS HERE!
        for sample in cart:
            g.db.samples.update(
                {'_id': ObjectId(sample['_id'])},
                {'$set': {'complete': True}},
                safe=True
            )
        session.pop('cart')
        flash('Your order was successfully processed.')
    return redirect(url_for('done'))




#This shoudl be on referenced from the HP rig in the JS. Not proxied.
nonalnum = re.compile(r'[^0-9A-Za-z]')
def ajax_zip_lookup(request, country, zip):
    zipcode = rpc.geo.postalLookup(country, nonalnum.sub('', zip), _safe=True)
    if zipcode is not None:
        return HttpResponse(json.dumps(zipcode))
    raise Http404