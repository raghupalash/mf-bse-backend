# Generated by Django 5.0.6 on 2024-07-30 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0018_rename_created_transaction_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_code",
            field=models.CharField(
                choices=[("NEW", "NEW"), ("CXL", "CANCELLATION")],
                default="NEW",
                max_length=15,
            ),
        ),
    ]