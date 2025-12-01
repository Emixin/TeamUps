from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib import messages 
from django.shortcuts import redirect




def push_notification(username, message):
    """
    This method pushes a real-time notification to a specific user via django channels.
    "async_to_sync" wraps an async function so it can be called synchronously,
    returning the async function's result.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'notifications_{username}',
                                            {'type': 'send_notification', 'message': message})



def handle_invitation(request, invitation, result):
    """
    This method handles user's invitation process.
    result can be either "accept" or "reject".
    """
    if invitation.status != "PENDING":
        messages.error(request, "Invitation is already answered!")
        return None

    if result == "accept":
            invitation.accept()
            messages.success(request, "Accepted!")

    if result == "reject":
            invitation.decline()
            messages.success(request, "Rejected!")

    return invitation




def handle_form(request, form, success_message, extra_kwargs=None, redirect_url='dashboard'):
    """
    This function handles a form submission and redirects back with a success message.
    extra_kwargs is a dictionary of additional fields to set before saving
    """
    
    if form.is_valid():
        obj = form.save(commit=False)

        if extra_kwargs:
            for key, value in extra_kwargs.items():
                setattr(obj, key, value)

        obj.save()
        messages.success(request, success_message)
        return redirect(redirect_url)
    return form


def avatar_upload_path_generator(instance, filename):
     """
     This function generates a file path for each file uploaded by a user,
     to avoid filename conflicts.
     """
     return f"avatars/{instance.username}/{filename}"