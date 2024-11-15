# Generated by Django 5.0.6 on 2024-07-24 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0009_alter_mutualfundlist_additional_purchase_amount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mutualfundlist",
            name="additional_purchase_amount",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="face_value",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="maximum_purchase_amount",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="maximum_redemption_qty",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="minimum_purchase_amount",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="minimum_redemption_qty",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="purchase_amount_multiplier",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="redemption_amount_maximum",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="redemption_amount_minimum",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="redemption_amount_multiple",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name="mutualfundlist",
            name="redemption_qty_multiplier",
            field=models.DecimalField(decimal_places=10, max_digits=25, null=True),
        ),
    ]
