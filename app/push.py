from firebase_admin import messaging


def task_created(user, friends, task_description):
    """make push notification that says a task was created.
    path to credentials is set in .env"""

    title = f"{user.username}'s task"
    body = f"{task_description}"

    for user in friends:
        if user.fir_push_notif_token is not None and user.task_notifs:
            notify_user(user, title, body)


def notify_user(user, title, body):
    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default"
                )
            )
        ),
        token=user.fir_push_notif_token,
    )

    _send(message, user)



def send_message_notif(fir_push_notif_token, badge_number, title=None, body=None):
    """send message notif and update badge icon"""
    message = messaging.Message(
        token=fir_push_notif_token,
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    badge=badge_number
                )
            )
        )
    )

    if title is not None and body is not None:
        message.notification = messaging.Notification(
                title=title,
                body=body,
            )

    _send(message, user)


def _send(message, user):
    """wrap the fcm send method with a try except"""
    # Send a message to the device corresponding to the provided
    # registration token.
    try:
        response = messaging.send(message)
    except messaging.ApiCallError:
        print(f"ApiCallError. the following user's token is invalid: {user.id} - {user.username}")
