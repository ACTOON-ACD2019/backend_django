# Generated by Django 2.2.5 on 2019-11-25 06:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('type', models.CharField(choices=[('SC', 'Scene'), ('BU', 'Bubble'), ('TX', 'Text'), ('UD', 'Undefined')], default='UD', max_length=2)),
                ('sequence', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Effect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('required_parameters', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameters', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cut', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actoon.Cut')),
                ('effect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actoon.Effect')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actoon.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('TO', 'Cartoon'), ('AU', 'Audio'), ('MO', 'Movie'), ('UD', 'Undefined')], default='UD', max_length=2)),
                ('file', models.FileField(upload_to='')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actoon.Project')),
            ],
        ),
        migrations.AddField(
            model_name='cut',
            name='media',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='actoon.Media'),
        ),
    ]
