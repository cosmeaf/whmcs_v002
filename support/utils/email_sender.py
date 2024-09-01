# support/utils/email_sender.py

from support.tasks import send_email_task

class EmailSender:
    def __init__(self, subject, to, template_name=None, context=None):
        self.subject = subject
        self.to = to
        self.template_name = template_name
        self.context = context

    def send_email(self):
        send_email_task.delay(self.subject, self.to, self.template_name, self.context)
    
    def send_test_email(self):
        self.subject = "Test Email"
        self.to = self.email_settings.email_host_user
        self.template_name = None
        self.context = None
        self.send_email()
