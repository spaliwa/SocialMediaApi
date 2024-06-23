from django.db import models
from django.contrib.auth.models import User

class Friendship(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outgoing_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incoming_requests')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
