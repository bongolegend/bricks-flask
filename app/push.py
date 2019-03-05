from firebase_admin import messaging
import firebase_admin

firebase_admin.initialize_app()


def task_created(user, friends, task_description):
    """make push notification that says a task was created.
    path to credentials is set in .env"""

    title = f"{user.username}'s task"
    body = f"{task_description}"

    for user in friends:
        if user.firebase_token is not None:
            notify_user(user.firebase_token, title, body)


def notify_user(firebase_token, title, body):
    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=firebase_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
