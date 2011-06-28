import datetime
import wtforms as forms
from wtforms import validators, widgets, fields


class ShowPasswordInput(widgets.PasswordInput):
    def __call__(self, field, **kwargs):
        return widgets.HTMLString(u''.join([
            super(ShowPasswordInput, self).__call__(field, **kwargs),
            '<br/>',
            '<label class="show_pass"><input type="checkbox" id="_%s" /> Show Password</label>' % field.id
        ]))


class ExpDateWidget(widgets.Input):
    def __init__(self):
        super(ExpDateWidget, self).__init__()

    def render_select(self, fid, name, choices, **kwargs):
        html = [u'<select %s>' % widgets.html_params(name=name, id=fid, **kwargs)]
        for val, label, selected in choices:
            html.append(widgets.Select.render_option(val, label, selected))
        html.append(u'</select>')
        return widgets.HTMLString(u''.join(html))

    def get_choices(self, current, choices):
        return [(v, k, v==current) for v, k in choices]

    def __call__(self, field, **kwargs):
        return widgets.HTMLString(u''.join([
            self.render_select(field.field_names[0][0],
                               field.field_names[0][1],
                               self.get_choices(field.data and field.data[0] or None, field.months)),
            field.separator,
            self.render_select(field.field_names[1][0],
                               field.field_names[1][1],
                               self.get_choices(field.data and field.data[1] or None, field.years))
        ]))


class ExpDateField(fields.Field):
    widget = ExpDateWidget()
    
    def __init__(self, label='', validators=None, months=(), years=(), separator=' / ', field_names=None, **kwargs):
        super(ExpDateField, self).__init__(label, validators, **kwargs)
        self.months = months or [('%02d' % i, '%02d (%s)' % (i, datetime.datetime(2011, i, 1).strftime('%B'))) for i in range(1,13)]
        self.years = years or [(i, i) for i in range(datetime.datetime.now().year, datetime.datetime.now().year+5)]
        self.separator = separator
        if field_names is not None:
            self.field_names = [(i, i) for i in field_names]
        else:
            self.field_names = [(i % self.id, i % self.name) for i in ('%s_month', '%s_year')]

    def process(self, formdata, data=fields._unset_value):
        """
        Naming the expmonth and expyear field the same name would give both 
        without overriding this method. However, I could not rely on the 
        order they are given to me.
        """
        self.process_errors = []
        if data is fields._unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
        try:
            self.process_data(data)
        except ValueError, e:
            self.process_errors.append(e.args[0])

        if formdata:
            try:
                #CHANGED THIS BLOCK
                data = []
                for i in self.field_names:
                    if '%s' in i[0]:
                        data.append(formdata[i[0] % self.name])
                    else:
                        data.append(formdata[i[0]])
                self.process_formdata(data)
            except ValueError, e:
                self.process_errors.append(e.args[0])

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError, e:
                self.process_errors.append(e.args[0])

    def process_formdata(self, valuelist):
        self.data = valuelist

    #def process_data(self, value):
    #    self.data = valuelist


def ValidateUSZip():
    message = 'Zip must be a valid US Postal Code'

    def _uszip(form, field):
        import application
        zipcode = application.get_zip('US', field.data)
        if zipcode is None:
            raise validators.ValidationError(message)

    return _uszip



