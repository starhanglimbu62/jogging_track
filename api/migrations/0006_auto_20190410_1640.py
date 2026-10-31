from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_auto_20190410_1620'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='userId',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='userId',
            new_name='user',
        ),
    ]
