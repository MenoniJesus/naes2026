from django.db import migrations


def create_admin_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='admin')


def remove_admin_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('sobraNada', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_group, remove_admin_group),
    ]
