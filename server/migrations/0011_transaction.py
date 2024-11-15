# Generated by Django 5.0.6 on 2024-07-29 09:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0010_alter_mutualfundlist_additional_purchase_amount_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_code",
                    models.CharField(
                        choices=[("N", "NEW"), ("C", "CANCELLATION")],
                        default="N",
                        max_length=1,
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("P", "Purchase"),
                            ("R", "Redemption"),
                            ("A", "Additional Purchase"),
                        ],
                        default="P",
                        max_length=1,
                    ),
                ),
                (
                    "order_type",
                    models.CharField(
                        choices=[("1", "Lumpsum"), ("2", "SIP")],
                        default="1",
                        max_length=1,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("0", "Requested internally"),
                            (
                                "1",
                                "Cancelled/Failed- refer to status_comment for reason",
                            ),
                            ("2", "Order successfully placed at BSE"),
                            ("4", "Redirected after payment"),
                            ("5", "Payment provisionally made"),
                            ("6", "Order sucessfully completed at BSE"),
                            ("7", "Reversed"),
                            ("8", "Concluded"),
                        ],
                        default="0",
                        max_length=1,
                    ),
                ),
                ("status_comment", models.CharField(blank=True, max_length=1000)),
                (
                    "amount",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1000000),
                        ],
                    ),
                ),
                ("all_redeem", models.BooleanField(blank=True, null=True)),
                (
                    "sip_num_inst",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(120),
                        ],
                    ),
                ),
                ("sip_start_date", models.DateField(blank=True, null=True)),
                (
                    "sip_num_inst_done",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(120),
                        ],
                    ),
                ),
                ("sip_dates", models.CharField(blank=True, max_length=255)),
                ("sip_order_ids", models.CharField(blank=True, max_length=255)),
                ("datetime_at_mf", models.DateTimeField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("bse_trans_no", models.CharField(blank=True, max_length=20)),
                ("folio_number", models.CharField(blank=True, max_length=25)),
                ("return_till_date", models.FloatField(blank=True, null=True)),
                ("return_date", models.DateField(blank=True, null=True)),
                ("return_grade", models.CharField(blank=True, max_length=200)),
                (
                    "scheme_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        related_query_name="transaction",
                        to="server.mutualfundlist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        related_query_name="transaction",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
