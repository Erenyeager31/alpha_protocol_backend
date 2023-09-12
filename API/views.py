import random, string, smtplib
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.shortcuts import render
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from AlphaProtocol import config
from . models import *
from validate_email_address import validate_email
from API.models import LeaderBoard,user_list
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

stories=[1,2,3]
current=0

@api_view(['GET'])
def getRoutes(request):
    routes=[
        'GET/ap/regusr',
        'POST/ap/genotp/',
        'POST/ap/verotp/',
        'GET/ap/getotp',
        'GET/ap/delotp',
        'POST/ap/addscr',
        'GET/ap/ldrbrd'
    ]
    return Response(routes)

@api_view(['GET'])
def regUser(request):
    # if cache.get('otp'):
    #     return Response(status=status.HTTP_208_ALREADY_REPORTED)
    return render(request,'API/genotp.html')

@api_view(['POST'])
def genOtp(request):
    global stories,current
    mail = request.POST.get('mail', False)
    username = request.POST.get('username', False)

    print(mail)
    print(username)



    if validate_email(mail):
        pass
    else:
        return render(request, 'API/email.html')

    your_email = config.EMAIL
    your_password = config.PASSWORD

    #!Logic to check if the email previously existed or not
    email_count = LeaderBoard.objects.values("email").count()
    # print(email_count)
    otp = "000000"
    index_list = [0,3,6]
    # print(index_list[random.randint(0, 2)])
    #!rechecking the logic here
    if email_count == 0:
        # user = LeaderBoard.objects.get(email=mail)
        otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        val = str(index_list[random.randint(0, 2)])
        otp = otp + val
        user = LeaderBoard(id=otp,name=username,email=mail,story=val)
        user.save()

    elif email_count == 1:
        user = LeaderBoard.objects.values().get(email=mail)
        print(user)
        index_list.remove(int(user["story"]))
        otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        val = str(index_list[random.randint(0, 1)])
        otp = otp + val
        user = LeaderBoard(id=otp,name=username,email=mail,story=val)
        user.save()

    elif email_count == 2:
        user = LeaderBoard.objects.values()
        print(user.get)
        for i in user:
            if mail == i.get("email"):
                # print(user.get("story"))
                index_list.remove(int(i.get("story")))
        otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        otp = otp + str(index_list[0])
        user = LeaderBoard(id=otp,name=username,email=mail,story=str(index_list[0]))
        user.save()
    else:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        val = str(index_list[random.randint(0, 2)])
        otp = otp + val
        user = LeaderBoard(id=otp,name=username,email=mail,story=val)
        user.save()

    # otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    print(otp)
    cache.set('otp', otp, None)
    
    message = MIMEMultipart()
    message['Subject'] = 'OTP for ALPHA PROTOCOL'
    message['From'] = your_email
    message['To'] = mail

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    body = f'''<b>OTP for alpha protocol</b>
<p>Thank you for registering for treasure hunt.</p>
<p>Your one time password to get started is <b style="color:green">{otp}</b>.
We hope you keep it confidential. Vamos!! </p>
'''
     
    html = f'''<html>
    <head>
    <title>OTP for <B>ALPHA PROTOCOL</B></title>
    </head>
    <body>
    {body}
    </body>
    </html>'''

    part1 = MIMEText(body, 'plain')
    part2 = MIMEText(html, 'html')

    # message.attach(part1)
    message.attach(part2)

    server.login(your_email, your_password)
    server.sendmail(your_email, mail, message.as_string())
    server.close()
    # LeaderBoard.objects.create(id=otp,name=username,email=mail)
    # if(email_count == 0):
    #     print("hi")
    #     user = LeaderBoard.objects.get(email=mail)
    #     user.story = val
    #     user.save()
    return render(request, 'API/success.html')

@api_view(['POST'])
def verOtp(request):
    print(request.data)
    code=request.data[0]['code']
    print(code)
    otp=cache.get('otp')
    if otp==code:
        cache.delete('otp')
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def addScore(request):
    print(request.data)
    otp=request.data[0]['otp']
    level=request.data[0]['level']
    time=request.data[0]['time']
    time =timeConversion(time)
    grp=LeaderBoard.objects.get(id=otp)
    grp.level=level
    grp.completion=time
    grp.save()
    print(request.data)
    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
def getOtp(request):
    data=[
        {
            "code":cache.get('otp')
        }
    ]
    return Response(data)

def leaderBoard(request):
   
    data=LeaderBoard.objects.all().exclude(level__isnull=True).order_by('-level','completion')[:10]
    context={
        "data":data
    }
    return render(request,'API/leaderboard.html',context)

@api_view(['GET'])
def delOtp(request):
    if cache.get('otp'):
        cache.delete('otp')
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_204_NO_CONTENT)

def timeConversion(time):
    time_remaining_seconds = float(time) * 60
    total_time_seconds = 30 * 60
    result_seconds = total_time_seconds - time_remaining_seconds
    result_minutes = result_seconds // 60
    result_seconds %= 60
    time = "{:02d}.{:02d}".format(int(result_minutes), int(result_seconds))
    return time