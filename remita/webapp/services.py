import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.http import HttpRequest


def get_ip_address(request: HttpRequest):
    user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    if user_ip_address:
        ip = user_ip_address.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_error_mail(resp_json):
    sender = 'mupumamgtsdev@gmail.com'
    receivers = 'seriterk@gmail.com'
    message = MIMEMultipart("alternative")
    message["Subject"] = "MUPUMA INFRATEL INTEGRATION API ERROR"
    message["From"] = sender
    message["To"] = receivers
    html = f"""\
                    <html>
                    <body>
                        <p>
                        Dear Team <br>
                        The following errorlist was returned while posting of an AP Payments Transaction <br>
                        {resp_json['errorList']['TEKESBERROR']} thus not allowing fullfilment of post requests to service "BNK9900", Kindly troubleshoot.<br>
                        Kind regards.
                        </p>
                    </body>
                    </html>
                    """
    msg = MIMEText(html, "html")
    password = "nnbhieknirlbtvcx"
    message.attach(msg)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(
            sender, receivers, message.as_string())


Login_Key = ""
Generate_otp_key = ""
Validate_otp_key = ""
