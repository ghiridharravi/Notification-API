******Register Parameters******
{
    "username": "username",
    "password": "password"
}

******Login Parameters******
{
    "username": "username",
    "password": "password"
}

******clicks parameters******

******Do this after login with bearer token authentication******

******event_type can be anything like click_event, search_event, purchase_event ******

******click_event and search_event does not send any notification to the user******
{
    "user": 1,
    "event_type": "purchase_event",
    "metadata": {
        "product": "iphone 14 pro",
        "add_to_cart": "True"
    }
}

{
    "user": 1,
    "event_type": "click_event",
    "metadata": {
        "product": "iphone 14 pro",
        "add_to_cart": "True"
    }
}

{
    "user": 1,
    "event_type": "search_event",
    "metadata": {
        "product": "iphone 14 pro",
        "add_to_cart": "True"
    }
}

******bulk data upload via API(JSON)******
[
    {"user": 1, "event_type": "failed_logins", "metadata": {}},
    {"user": 1, "event_type": "purchase_event", "metadata": {}},
    {"user": 1, "event_type": "search_event", "metadata": {}},
    {"user": 1, "event_type": "click_event", "metadata": {}}
]
