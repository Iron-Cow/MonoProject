# pyright: reportArgumentType = false
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AITool(models.Model):
    """Represents a tool (function) available to an AI agent."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Tool description")


class AIAgent(models.Model):
    """Represents a tool-using AI agent with a specific prompt and config."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    prompt = models.TextField(help_text="System prompt or behavior instruction")
    model_name = models.CharField(max_length=100, default="models/gemini-2.0-flash")
    temperature = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    tools = models.ManyToManyField(AITool, related_name="agents")


class AIConversation(models.Model):
    """Stores a conversation session between user and agent."""

    agent = models.ForeignKey(AIAgent, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)


class AIMessage(models.Model):
    """Represents a single user or agent message."""

    conversation = models.ForeignKey(
        AIConversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(
        max_length=10, choices=[("user", "User"), ("agent", "Agent")]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
