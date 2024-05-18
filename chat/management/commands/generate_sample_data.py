import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chat.models import Thread, Message
from django.db.models import Q


class Command(BaseCommand):
    help = 'Generate sample data for the chat application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample data...')

        # Create users
        users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(username=f'user{i}', defaults={'email': f'user{i}@example.com'})
            if created:
                user.set_password('password')
                user.save()
            users.append(user)

        # Create threads
        threads = []
        for i in range(0, 4):
            participants = [users[i], users[i+1]]
            thread = Thread.objects.create()
            thread.participants.add(*participants)
            thread.save()
            threads.append(thread)

        # Create messages
        for thread in threads:
            for i in range(1, 6):
                sender = random.choice(thread.participants.all())
                Message.objects.create(
                    sender=sender,
                    text=f'Sample message {i} in thread {thread.id}',
                    thread=thread
                )

        self.stdout.write(self.style.SUCCESS('Sample data generated successfully!'))
