# Generated migration to change id field to UUIDField

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('assistance', '0002_alter_todo_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todo',
            name='id',
        ),
        migrations.AddField(
            model_name='todo',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
