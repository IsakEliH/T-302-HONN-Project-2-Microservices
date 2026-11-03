import os
from dotenv import find_dotenv, load_dotenv

# Load .env file from the current directory or parent directories if present
load_dotenv(find_dotenv())

class Config:
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_SENDER_EMAIL: str = os.getenv("RESEND_SENDER_EMAIL", "onboarding@resend.dev")
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    # Queues to listen for order and payment events
    QUEUES: list[str] = os.getenv("RABBITMQ_QUEUES", "orders,payments,email_events").split(",")

config = Config()
