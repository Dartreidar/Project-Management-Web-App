# Generated by Django 4.2.1 on 2023-06-29 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectManagement', '0005_alter_project_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('detail', models.TextField()),
                ('notification_type', models.CharField(choices=[('deadline', 'Deadline Reminder'), ('invitation', 'Project Invitation')], max_length=20)),
                ('status', models.CharField(choices=[('unread', 'Unread'), ('read', 'Read')], default='unread', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projectManagement.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
