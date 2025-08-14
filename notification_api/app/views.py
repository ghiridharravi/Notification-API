from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, NotificationLog, UserPreference
from .serializers import EventSerializer, NotificationLogSerializer, UserRegisterSerializer
from .rules_engine import evaluate_rules
from .tasks import send_notification_task
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Max

@api_view(['POST'])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.filter(username=serializer.data['username'])[0]
        UserPreference.objects.create(user=user, preferred_channels="email", mail=user.email)
        return Response({"message": "User registered successfully"})
    return Response(serializer.errors)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    log_user = User.objects.filter(username=username)
    if len(log_user) == 0:
        return Response({'message': "User does not exists"})
    try:
        user = None
        latest_attempt = NotificationLog.objects.filter(user=log_user[0]).aggregate(Max('sent_at'))['sent_at__max']
        last_attempt = NotificationLog.objects.filter(user=log_user[0], sent_at=latest_attempt)[0].sent_at
        expiration = (last_attempt + timedelta(hours=24)).replace(tzinfo=None)
        if datetime.now() > expiration:
            user = authenticate(username=username, password=password)
    except:
        user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': "Login successful"
        })
    else:
        try:
            latest_attempt = NotificationLog.objects.filter(user=log_user[0]).aggregate(Max('sent_at'))['sent_at__max']
            last_attempt = NotificationLog.objects.filter(user=log_user[0], sent_at=latest_attempt, message="Multiple failed login attempts")[0].sent_at
            expiration = (last_attempt + timedelta(hours=24)).replace(tzinfo=None)
            if datetime.now() > expiration:
                NotificationLog.objects.filter(user=log_user[0], sent_at=latest_attempt, message="Multiple failed login attempts")[0].delete()
                for eve in Event.objects.filter(user=log_user[0], event_type="failed_logins"):
                    eve.delete()
                event = [{'user': log_user[0].id, 'event_type': 'failed_logins'}]
                serializer = EventSerializer(data=event, many=isinstance(event, list))
                serializer.is_valid(raise_exception=True)
                events = serializer.save()    
                msg = evaluate_rules(events, log_user[0].id)
                if msg:
                    notif = NotificationLog.objects.create(user=log_user[0], message=msg, channel="email")
                    send_notification_task(notif.id, log_user[0])
                    return Response({'message': "Three Failed attempts"})  
            else:
                return Response({'message': "Reached maximum allowed login attempts, wait for 24 hours before trying again"})            
        except Exception as e: 
            event = [{'user': log_user[0].id, 'event_type': 'failed_logins'}]
            serializer = EventSerializer(data=event, many=isinstance(event, list))
            serializer.is_valid(raise_exception=True)
            serializer.save()    
            msg = evaluate_rules(event, log_user[0].id)
            if msg:
                notif = NotificationLog.objects.create(user=log_user[0], message=msg, channel="email")
                send_notification_task(notif.id, log_user[0])
                return Response({'message': "Three Failed attempts"})
    return Response({'message': 'Invalid credentials'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_data(request):
    serializer = EventSerializer(data=request.data, many=isinstance(request.data, list))
    serializer.is_valid(raise_exception=True)
    events = serializer.save()
    for event in events if isinstance(events, list) else [events]:
        msg = evaluate_rules(event, event.user)
        if msg:
            notif = NotificationLog.objects.create(
                user=event.user, message=msg, channel="email"
            )
            send_notification_task.delay(notif.id, event.user)
    return Response({"status": "events processed"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def click_events(request):
    serializer = EventSerializer(data=request.data, many=isinstance(request.data, list))
    serializer.is_valid(raise_exception=True)
    serializer.save()
    event = serializer.data['event_type']
    msg = evaluate_rules(event,request.user)
    if msg['type'] == "purchase_event":
        notif = NotificationLog.objects.create(
            user=request.user, message=msg['message'], channel="email"
        )
        send_notification_task(notif.id, request.user)
        return Response({'message': "Thank you for shopping with us"})
    return Response({"status": "events processed"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_logs(request):
    if request.user.is_superuser:
        logs = NotificationLog.objects.all()
        return Response(NotificationLogSerializer(logs, many=True).data)
    else:
        return Response({"message": "Not Authorised"})
