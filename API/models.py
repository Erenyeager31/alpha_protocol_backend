from django.db import models

class LeaderBoard(models.Model):
    id=models.CharField(max_length=4, primary_key=True)
    name=models.CharField(max_length=50, null=True)
    email=models.EmailField()
    level=models.IntegerField(blank=True,null=True)
    completion=models.CharField(max_length=10,null=True)
    story=models.CharField(max_length=3,default="")
    def __str__(self) -> str:
        return self.email

class user_list:
    name=models.CharField(max_length=50, null=True)
    email=models.EmailField()
    story=models.CharField(max_length=3,null=True)
    def __str__(self) -> str:
        return self.email
    