def sendEmail( body ):
  import smtplib
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
  msg = MIMEMultipart('alternative')
  msg['Subject'] = "Test email"
  msg['From'] = 'micmoyles@gmail.com' 
  msg['To'] = 'micmoyles@gmail.com'

  #  Record the MIME types of both parts - text/plain and text/html.
  part2 = MIMEText(body,'html')

  msg.attach(part2)
  mail = smtplib.SMTP('smtp.gmail.com:587')

  mail.ehlo()

  mail.starttls()

  mail.ehlo()
  #mail.login('mattgolden@erovaenergy.ie', 'EEmattyg11EE')
  mail.login('micmoyles@gmail.com', 'Pi27hliL')
  mail.sendmail('micmoyles@gmail.com', ['micmoyles@gmail.com','mattgolden@erovaenergy.ie'], msg.as_string())
  mail.quit()
