import wtforms as forms
from wtforms import validators, widgets
from wtforms.widgets.core import HTMLString, html_params

from extra.lib.regions import REGION_CHOICES, COUNTRY_CHOICES
from extra.formfields import ExpDateField

class OptGroupSelect(widgets.Select):
    def iter_group(self, field, group):
        for value, label in group:
            yield (value, label, field.coerce(value) == field.data)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            #NEW STUFF
            if hasattr(label, '__iter__'):
                html.append(u'<optgroup %s>' % html_params(label=val))
                for v, l, s in self.iter_group(field, label):
                    html.append(self.render_option(v, l, s))
                html.append(u'</optgroup>')
            else:
                html.append(self.render_option(val, label, selected))
            #/NEW STUFF
        html.append(u'</select>')
        return HTMLString(u''.join(html))


class MediumLen(object):
    field_flags = ('medium_len', )
    def __call__(self, form, field):
        pass



class SampleForm(forms.Form):
    transaction__credit_card__cardholder_name           = forms.TextField('Your Name', [validators.Required()])
    transaction__customer__email                        = forms.TextField('E-Mail Address', [validators.Required(), validators.Email('A valid e-mail is important here.')])
    transaction__customer__phone                        = forms.TextField('Phone Number', [validators.Required()])
    transaction__billing__extended_address             = forms.TextField('Apt or Suite #')
    transaction__billing__street_address               = forms.TextField('Street', [validators.Required()])
    transaction__billing__locality              = forms.TextField('City', [validators.Required()])
    #transaction__billing__region               = forms.SelectField('State/Provence', [validators.Required()], choices=REGION_CHOICES, widget=OptGroupSelect())
    transaction__billing__region                = forms.TextField('State/Provence', [validators.Required()])
    transaction__billing__country_code_alpha2   = forms.SelectField('Country', [validators.Required()], choices=COUNTRY_CHOICES)
    postal                                              = forms.TextField('Postal / City / State or Province', [validators.Required()])

    
    transaction__credit_card__number                    = forms.TextField('Credit card number', [validators.Required()])
    expdate                                             = ExpDateField('Expiration Date', [validators.Required()], field_names=('transaction__credit_card__expiration_month', 'transaction__credit_card__expiration_year'))
    transaction__credit_card__cvv                       = forms.IntegerField('Security Code', [validators.Required()])
    transaction__billing__postal_code           = forms.TextField('Billing Postal Code', [validators.Required()])
    tr_data                                             = forms.HiddenField()
    #I render these fields manually.
    #transaction__options__store_in_vault               = forms.BooleanField('Remember My Information', default=True)
