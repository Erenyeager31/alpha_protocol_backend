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
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    cache.set('otp', otp, None)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    body = f'''OTP for alpha protocol
    Thank you for registering for treasure hunt . Your one time password to get started is  {otp} .
    We hope you keep it confidential. Vamos!!'''
     

    server.login(your_email, your_password)
    server.sendmail(your_email, mail, body)
    server.close()
    LeaderBoard.objects.create(id=otp,name=username,email=mail)
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
    time = 30.00-float(time)
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