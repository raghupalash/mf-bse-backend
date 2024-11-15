# Generated by Django 5.0.6 on 2024-07-29 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0012_kycdetail_client_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_code",
            field=models.CharField(
                choices=[("NEW", "NEW"), ("CANCELLATION", "CANCELLATION")],
                default="NEW",
                max_length=15,
            ),
        ),
    ]
