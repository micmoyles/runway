def sendEmail( body, subject ):

  import smtplib
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText

  fromAddress = 'micmoyles@gmail.com'
  toAddress = 'micmoyles@gmail.com'
  ccAddress = 'mattgolden@erovaenergy.ie'

  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject
  msg['From'] = fromAddress
  msg['To'] = toAddress

  #  Record the MIME types of both parts - text/plain and text/html.

  part2 = MIMEText(body,'html')

  msg.attach(part2)
  mail = smtplib.SMTP('smtp.gmail.com:587')

  mail.ehlo()

  mail.starttls()

  mail.ehlo()
  #mail.login('mattgolden@erovaenergy.ie', 'EEmattyg11EE')
  mail.login('micmoyles@gmail.com', 'Pi27hliL')
  mail.sendmail( fromAddress , [ toAddress ], msg.as_string())
  mail.quit()
