# utils/email_notifier.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import Config
import logging

class EmailNotifier:
    def __init__(self):
        self.enabled = Config.EMAIL_ENABLED
        self.smtp_host = Config.EMAIL_HOST
        self.smtp_port = Config.EMAIL_PORT
        self.email_user = Config.EMAIL_USER
        self.email_pass = Config.EMAIL_PASS
    
    def send_email(self, subject, body, to_email):
        """Send email notification"""
        if not self.enabled:
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_pass)
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            logging.info(f"📧 Email sent: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error sending email: {str(e)}")
            return False
    
    def send_trade_alert(self, trade_info, to_email):
        """Send trade alert email"""
        subject = f"🚨 Trade Alert: {trade_info.get('type', 'UNKNOWN')} {trade_info.get('symbol', '')}"
        body = f"""
Trade Alert Details:
====================
Type: {trade_info.get('type', 'N/A')}
Symbol: {trade_info.get('symbol', 'N/A')}
Entry Price: {trade_info.get('entry_price', 'N/A')}
Strategy: {trade_info.get('strategy', 'N/A')}
Time: {trade_info.get('time', 'N/A')}

Risk Management:
================
Position Size: {trade_info.get('position_size', 'N/A')}
Stop Loss: {trade_info.get('sl', 'N/A')}
Take Profit: {trade_info.get('tp', 'N/A')}
        """
        
        return self.send_email(subject, body, to_email)