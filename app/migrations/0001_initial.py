# Generated by Django 2.0.4 on 2018-04-09 16:56

import app.models
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.fields.related


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('userid', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='userid')),
                ('username', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='username')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True, verbose_name='email address')),
                ('usertype', models.SmallIntegerField()),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('mobile', models.CharField(blank=True, max_length=20, null=True, verbose_name='mobile')),
                ('firstname', models.CharField(max_length=100, verbose_name='firstname')),
                ('lastname', models.CharField(max_length=100, verbose_name='lastname')),
                ('picture', models.ImageField(blank=True, max_length=67200, null=True, upload_to=app.models.user_dir_path)),
                ('returnbooknotontime', models.IntegerField(blank=True, null=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BlackListUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.fields.related.ForeignKey, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=200)),
                ('isbn', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=200)),
                ('publisher', models.CharField(max_length=200)),
                ('edition', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('picture', models.ImageField(blank=True, max_length=21376, null=True, upload_to=app.models.book_dir_path)),
                ('barcode', models.CharField(max_length=200, unique=True)),
                ('status', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Borrow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
