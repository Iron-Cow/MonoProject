# Generated by Django 4.2 on 2023-10-01 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monobank", "0005_remove_monocard_comment_monotransaction_comment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="monojar",
            name="goal",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]