from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, UserSerializer
from django.contrib.auth.models import User


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        participants = request.data.get('participants')

        if not participants or len(participants) != 1:
            return Response({"error": "A thread must have exactly one other participant."},
                            status=status.HTTP_400_BAD_REQUEST)

        other_participant_id = participants[0]
        try:
            other_participant = User.objects.get(id=other_participant_id)
        except User.DoesNotExist:
            return Response({"error": "The specified participant does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the thread already exists
        existing_thread = Thread.objects.filter(participants=request.user).filter(participants=other_participant).first()
        if existing_thread:
            return Response({"thread": ThreadSerializer(existing_thread).data})

        thread = Thread.objects.create()
        thread.participants.add(request.user, other_participant)
        thread.save()

        return Response({"thread": ThreadSerializer(thread).data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        try:
            thread = Thread.objects.get(pk=pk)
        except (Thread.DoesNotExist, ValidationError):
            return Response({"error": "Thread does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Validate query parameters
        limit = request.query_params.get('limit', None)
        if limit and not limit.isdigit():
            return Response({"error": "Limit must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        offset = request.query_params.get('offset', None)
        if offset and not offset.isdigit():
            return Response({"error": "Offset must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        messages = thread.messages.all()
        if limit:
            limit = int(limit)
            messages = messages[:limit]
        if offset:
            offset = int(offset)
            messages = messages[offset:]

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # retrieving the list of threads for any user;
    # I did not understand this part, so the list of threads are made for request.user with no user_id given,
    # but also it can be received with this method for any user given as query param.
    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
            threads = Thread.objects.filter(participants=user)
        else:
            threads = Thread.objects.filter(participants=request.user)
        page = self.paginate_queryset(threads)
        if page is not None:
            serializer = ThreadSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ThreadSerializer(threads, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Was not in documentation, but added filtered messages, from all threads users are in.
    def list(self, request, *args, **kwargs):
        messages = Message.objects.filter(thread__participants=request.user)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({"status": "Message marked as read"})

    # Not explained logic, but usually unread_count would be used to show unread messages that are forwarded
    # not from user
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        user = request.user
        # Adding filter for sender not from request.user.
        # To get all the messages unread - exclude filter should be removed
        unread_count = Message.objects.filter(thread__participants=user, is_read=False).exclude(sender=user).count()
        return Response({"unread_count": unread_count})

    def create(self, request, *args, **kwargs):
        thread_id = request.data.get('thread')
        text = request.data.get('text')

        if not thread_id or not text:
            return Response({"error": "Thread ID and text are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            return Response({"error": "Thread does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user not in thread.participants.all():
            return Response({"error": "You are not a participant in this thread."}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(sender=request.user, text=text, thread=thread)
        serializer = MessageSerializer(message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
