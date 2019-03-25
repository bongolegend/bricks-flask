from firebase_admin import messaging, credentials
import firebase_admin
from settings import APP_ROOT
import os


cred = credentials.Certificate(os.path.join(APP_ROOT, os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")))
firebase_admin.initialize_app(cred)


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
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound="default"
                )
            )
        ),
        token=firebase_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
