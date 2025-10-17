import emails
import os
from dotenv import dotenv_values
import traceback

config = dotenv_values(".env")

default_mail_template = """
   <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; color: #333; }}
                .container {{ background-color: #ffffff; padding: 0 20px 20px 20px; margin: auto; max-width: 600px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                .logo {{ display: block; width: 120px; }}
                .content {{ margin: 20px; font-size: 16px; line-height: 1.5; text-align: center; min-height: 300px; display: flex; flex-direction: column; gap: 20px; align-items: center; justify-content: center; }}
                .footer {{ margin-top: 20px; font-size: 12px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://dashboard.predictops.fr/predictops/logo_predictops_black.svg" alt="Logo" class="logo">
                <div class="content">
                    {message}
                </div>
                <div class="footer">
                    © SAD Marketing - Tous droits réservés
                </div>
            </div>
        </body>
        </html>
"""

guideline_mail_template = """
    <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; color: #333; }}
                .container {{ background-color: #ffffff; padding: 0 20px 20px 20px; margin: auto; max-width: 600px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                .logo {{ display: block; width: 120px; }}
                .content {{ margin: 20px; font-size: 16px; line-height: 1.5; text-align: center; min-height: 200px; display: flex; flex-direction: column; gap: 20px; align-items: center; justify-content: center; }}
                .guideline-theme {{ font-weight: 700; color: #c92a2a; text-align: end }}
                .guideline-time {{ font-style: italic; margin-top: 20px; text-align: end }}
                .guideline-author {{ margin-top: 20px; text-align: end }}
                .footer {{ margin-top: 20px; font-size: 12px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://dashboard.predictops.fr/predictops/logo_predictops_black.svg" alt="Logo" class="logo">
                <div class="guideline-theme">{theme}</div>
                <div class="guideline-time">{start_date} - {end_date}</div>
                <div class="guideline-author">Par : {author}</div>
                <div class="content">
                    {guideline}
                </div>
                <div class="footer">
                    © SAD Marketing - Tous droits réservés
                </div>
            </div>
        </body>
        </html>
"""

def send_email(receiver, subject, message, smtp=config['MAIL_SERVER'], port=config['MAIL_PORT'], sender=config['MAIL_DEFAULT_SENDER'], password=config['MAIL_PASSWORD']):
    try:
        
        # Create and configure the email message
        msg = emails.html(
            html=message,
            subject=subject,
            mail_from=sender
        )

        # Define SMTP options
        smtp_options = {
            "host": smtp,
            "port": int(port),
            "user": sender,
            "password": password,
            "tls": True
        }

        # Send the email
        response = msg.send(to=receiver, smtp=smtp_options)
        if response.status_code == 250:
            return 200  
        else:
            return 500  
    except Exception as e:
        print(traceback.format_exc())
        return 500
