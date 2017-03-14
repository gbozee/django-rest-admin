import json
from mservice_model.api import ServiceApi, FetchHelpers

instance = ServiceApi(FetchHelpers('http://localhost:8000/todos/'))