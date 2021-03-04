from django.db import models

# Create your models here.
class Tgenre(models.Model):
    genreid = models.IntegerField(primary_key=True)
    genrename = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tgenre'


class Travel(models.Model):
    tourid = models.IntegerField(db_column='tourId', primary_key=True)  # Field name made lowercase.
    city = models.CharField(max_length=10, blank=True, null=True)
    town = models.CharField(max_length=20, blank=True, null=True)
    tourname = models.CharField(max_length=40, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    score = models.CharField(max_length=20, blank=True, null=True)
    tscore = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey(Tgenre, models.DO_NOTHING, db_column='genre', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travel'


class Treview(models.Model):
    treviewno = models.IntegerField(primary_key=True)
    treviewid = models.ForeignKey('Tuser', models.DO_NOTHING, db_column='treviewId', blank=True, null=True)  # Field name made lowercase.
    tourid = models.ForeignKey(Travel, models.DO_NOTHING, db_column='tourId', blank=True, null=True)  # Field name made lowercase.
    rating = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'treview'


class Tuser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=20)
    user_name = models.CharField(max_length=10, blank=True, null=True)
    user_pwd = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tuser'  