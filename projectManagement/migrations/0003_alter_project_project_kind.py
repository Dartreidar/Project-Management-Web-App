# Generated by Django 4.2.1 on 2023-07-10 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectManagement', '0002_alter_notification_notification_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_kind',
            field=models.CharField(choices=[('Web', 'Web'), ('Software', 'Software'), ('Hardware', 'Hardware')], max_length=50),
        ),
    ]
