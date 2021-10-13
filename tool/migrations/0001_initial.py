# Generated by Django 2.2.17 on 2021-10-13 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('assemblyID', models.AutoField(primary_key=True, serialize=False)),
                ('assemblyName', models.CharField(max_length=15, unique=True)),
                ('assemblyQuantity', models.IntegerField()),
                ('assemblySlug', models.SlugField(default='assembly-', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('carID', models.CharField(max_length=8, primary_key=True, serialize=False, unique=True)),
                ('carName', models.CharField(max_length=10)),
                ('carYear', models.IntegerField()),
                ('carSlug', models.SlugField(default='car-', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('partID', models.AutoField(primary_key=True, serialize=False)),
                ('partName', models.CharField(max_length=15)),
                ('makeBuy', models.BooleanField()),
                ('partCost', models.FloatField(null=True)),
                ('partQuantity', models.IntegerField(default=1)),
                ('partCurrency', models.CharField(max_length=3, null=True)),
                ('partComment', models.CharField(max_length=50, null=True)),
                ('partSlug', models.SlugField(default='part-', unique=True)),
                ('assemblyID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tool.Assembly')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('systemID', models.AutoField(primary_key=True, serialize=False)),
                ('systemName', models.CharField(max_length=15)),
                ('costed', models.BooleanField(default=False)),
                ('systemSlug', models.SlugField(default='system-', unique=True)),
                ('carID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tool.Car')),
            ],
        ),
        migrations.CreateModel(
            name='PMFT',
            fields=[
                ('pmftID', models.AutoField(primary_key=True, serialize=False)),
                ('pmftName', models.CharField(max_length=15)),
                ('pmftComment', models.CharField(max_length=50, null=True)),
                ('pmftCost', models.FloatField(default=0)),
                ('pmftCurrency', models.CharField(max_length=3, null=True)),
                ('pmftCostComment', models.CharField(max_length=50, null=True)),
                ('pmftQuantity', models.IntegerField(default=1)),
                ('pmftType', models.CharField(max_length=1)),
                ('pmftSlug', models.SlugField(default='pmft-', unique=True)),
                ('partID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tool.Part')),
            ],
        ),
        migrations.AddField(
            model_name='assembly',
            name='systemID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tool.System'),
        ),
    ]
