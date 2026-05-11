from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='todo',
            table='todos',
        ),
    ]
