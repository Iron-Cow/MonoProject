# Generated by Django 4.2 on 2023-10-01 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "monobank",
            "0009_rename_cashbackamount_jartransaction_cashback_mount_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="jartransaction",
            old_name="cashback_mount",
            new_name="cashback_amount",
        ),
    ]
