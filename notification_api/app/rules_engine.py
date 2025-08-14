
from .models import Event
def evaluate_rules(event,user):
    rules = [
        {"type": "failed_logins", "count": 3, "message": "Multiple failed login attempts"},
        {"type": "purchase_event", "count": 1, "message": "Thanks for your first purchase!"},
        {"type": "click_event", "count": 1, "message": ""},
        {"type": "search_event", "count": 1, "message": ""}
    ]
    if event == "purchase_event":
        return rules[1]
    elif event == "click_event":
        return rules[2]
    elif event == "search_event":
        return rules[3]
    event_count = Event.objects.filter(user=user, event_type='failed_logins')
    if event_count.count() == 3:
        return "Multiple failed login attempts"
    return None
