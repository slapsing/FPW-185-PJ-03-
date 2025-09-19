def unread_notifications_count(request):
    if request.user.is_authenticated:
        return {"unread_notifications": request.user.notifications.filter(read=False).count()}
    return {"unread_notifications": 0}
