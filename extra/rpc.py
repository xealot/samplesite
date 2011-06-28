from lib.homeplate import HPRPCHandler
from django.conf import settings

rpc = HPRPCHandler(settings.RPC_API_TOKEN, settings.RPC_ENDPOINT)
