# Generated by Django 5.0.6 on 2024-07-11 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0005_kycdetail_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bankdetail",
            name="ifsc_code",
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name="user",
            name="middle_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]