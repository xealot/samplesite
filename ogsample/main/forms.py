import wtforms as forms
from wtforms import validators, widgets

from extra.formfields import ShowPasswordInput, ExpDateField, ValidateUSZip

class MediumLen(object):
    field_flags = ('medium_len', )
    def __call__(self, form, field):
        pass

class RegistrationForm(forms.Form):
    email      = forms.TextField('E-Mail Address', [validators.Required(), validators.Email('A valid e-mail is important here.')],  
                                 description='This e-mail will be used for receipts and to recover your password.')
    username   = forms.TextField('Username', [validators.Required(), validators.Length(min=4, max=25)],
                                 description="Choose a memorable and unique name, this will be the name you login with.")
    passw      = forms.PasswordField('Password', [validators.Required(), validators.Length(min=4)], widget=ShowPasswordInput(hide_value=False), 
                                     description="Please choose a strong password. It will protect your sensitive information.")
    #name       = forms.TextField('Name', [validators.Required()])
    #last_name  = forms.TextField('Last Name', [validators.Required()])
    #phone      = forms.TextField('Phone Number', [validators.Optional(), validators.Length(min=10, max=35)], 
    #                             description='We will use this if there is a problem with your Credit Card or Order. (e.g. (555)-555-5555)')

class LoginForm(forms.Form):
    username = forms.TextField('Username', [validators.Required()],
                               description="This is your Network Growth username")
    password = forms.PasswordField('Password', [validators.Required()], widget=ShowPasswordInput(hide_value=False))
    remember = forms.BooleanField('Remember Me', [validators.Optional()])


default_note_text = """Hello-
Please enjoy these coffee samples from Organo Gold. Included is one black coffee and one lattee as well as a DVD explaining the business.

Enjoy!
"""

COUNTRY_CHOICES = (
    ('US', 'United States'),
    ('CA', 'Canada')
)

class SampleForm(forms.Form):
    email      = forms.TextField('E-Mail Address', [validators.Required(), validators.Email()], description="Your prospect's e-mail address.")
    name       = forms.TextField('Name', [validators.Required()], description="The name of the person this sample is getting sent to.")
    address2   = forms.TextField('Apt or Suite #', description="If they live in an apt, or have an additional suite number, enter it here.")
    address1   = forms.TextField('Street', [validators.Required()], description="The mailing address, typically a house number and street.")
    city       = forms.TextField('City', [validators.Required()], description="The city associated with the mailing address.")
    state      = forms.TextField('State', [validators.Required()], description="The state associated with the mailing address.")
    country    = forms.SelectField('Country', [validators.Required()], choices=COUNTRY_CHOICES, description="Choose the country to which this sample will be shipped.")
    postal     = forms.TextField('Postal', [validators.Required()], description="A postal code associated with the entered address.")
    message    = forms.TextField('Write Your Own Note', [validators.Required(), validators.Length(0, 200)], widget=widgets.TextArea(), default=default_note_text,
                                 description="A customized note to be included with your sample when it is sent. You can only enter 200 characters max.")

class CheckoutForm(forms.Form):
    transaction__customer__email                = forms.TextField('E-Mail Address', [validators.Required(), validators.Email('A valid e-mail is important here.')], description="We will send you a receipt of this order here.")
    transaction__customer__phone                = forms.TextField('Phone Number', [validators.Required()], description="If there is a problem printing or shipping your order, this number is used to contact you for details.")
    transaction__billing__country_code_alpha2   = forms.SelectField('Country', [validators.Required()], choices=COUNTRY_CHOICES, description="Choose the country to which this credit card resides.")
    transaction__billing__postal_code           = forms.TextField('Zip Code', [validators.Required(), ValidateUSZip()], description="A 5 digit postal code associated with the entered address.")
    transaction__credit_card__cardholder_name   = forms.TextField('Your Name', [validators.Required()], description="Your name as it appears on your credit card.")
    transaction__credit_card__number            = forms.TextField('Credit card number', [validators.Required()], description="The 15-16 digits on the front of your credit card.")
    expdate                                     = ExpDateField('Expiration Date', [validators.Required()], field_names=('transaction__credit_card__expiration_month', 'transaction__credit_card__expiration_year'), description="The date your credit card expires, located on the front.")
    transaction__credit_card__cvv               = forms.IntegerField('Security Code', [validators.Required()], description="The last 3 digits on the back of your credit card.")
    tr_data                                     = forms.HiddenField()
    #I render these fields manually.
    transaction__billing__locality              = forms.TextField()
    transaction__billing__region                = forms.TextField()
    transaction__options__store_in_vault        = forms.BooleanField('Remember My Information', default=True, description='Allow me to use this card again without filling out this form.')



