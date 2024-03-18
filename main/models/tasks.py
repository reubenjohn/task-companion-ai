from dataclasses import dataclass
import sqlite3
from django.db import models

@dataclass
class NewTaskData:
    title: str
    priority: int

class Task(models.Model):
    class State(models.TextChoices):
        pending='pending', 'pending'
        completed='completed', 'completed'

    class Priority(models.IntegerChoices):
        unknown = 0, "unknown"
        critical = 1, "critical"
        high = 2, "high"
        medium = 3, "medium"
        low = 4, "low"
        obsolete = 99, "obsolete"

    title = models.CharField(max_length=200)
    state = models.CharField(max_length=20, choices=State.choices, default=State.pending)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.unknown)

    # def open_status(self):
    #     now = sqlite3.func.current_time()
    #     return now > self.opens_at and now < self.closes_at