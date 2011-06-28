import braintree

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    "ss37wjw57f8wz9k4",
    "y5jq7rw2c8p52ngf",
    "mgqq3836tjc6sq55"
)
# Allow unsafe SSL, removes dependency on PycURL C-ext.
braintree.Configuration.use_unsafe_ssl = True