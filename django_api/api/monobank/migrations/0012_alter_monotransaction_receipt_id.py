# Generated by Django 4.2.6 on 2024-06-02 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monobank", "0011_rename_originalmcc_jartransaction_original_mcc"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monotransaction",
            name="receipt_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]