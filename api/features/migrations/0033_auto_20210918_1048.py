# Generated by Django 2.2.24 on 2021-09-18 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("features", "0032_update_feature_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicalfeature",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]
