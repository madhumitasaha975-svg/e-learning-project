from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_courserating'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='course_thumbnails/'),
        ),
    ]