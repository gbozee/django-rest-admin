class MockRequest:

    def __init__(self, response, **kwargs):
        self.response = response
        self.overwrite = False
        if kwargs.get('overwrite'):
            self.overwrite = True
        self.status_code = kwargs.get('status_code', 200)

    @classmethod
    def raise_for_status(cls):
        pass

    def json(self):
        if self.overwrite:
            return self.response
        return {'data': self.response}


option_response = {
    "actions": {
        "POST": {
            "id": {
                "type": "integer",
                "required": False,
                "read_only": True,
                "label": "ID"
            },
            "title": {
                "type": "string",
                "required": True,
                "read_only": False,
                "label": "Title"
            },
            "completed": {
                "type": "boolean",
                "required": False,
                "read_only": False,
                "label": "Completed"
            },
            "owner": {
                "type": "field",
                "required": False,
                "read_only": False,
                "label": "Owner"
            }
        }
    }
}

get_all_response = {
    "count": 4,
    "next": None,
    "previous": None,
    "last_id": 4,
    "first_id": 1,
    "results": [
        {
            "id": 1,
            "title": "Buckle my shoe",
            "completed": False,
            "owner": None
        },
        {
            "id": 2,
            "title": "Knock at the door",
            "completed": False,
            "owner": None
        },
        {
            "id": 3,
            "title": "Buy the new Ram",
            "completed": True,
            "owner": None
        },
        {
            "id": 4,
            "title": "Implement restful Admin",
            "completed": False,
            "owner": None
        }
    ]
}