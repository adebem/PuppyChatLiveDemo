# Generated by Django 3.2.7 on 2021-10-03 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DictionaryEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=30)),
                ('word_type', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Dog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('temperament', models.CharField(max_length=50)),
                ('height', models.CharField(max_length=80)),
                ('weight', models.CharField(max_length=80)),
                ('lifespan', models.CharField(max_length=50)),
                ('group', models.CharField(max_length=50)),
                ('description_short', models.TextField()),
                ('description_long', models.TextField()),
                ('nicknames', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GrammarRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.CharField(max_length=30)),
                ('addends', models.CharField(max_length=30)),
            ],
        ),
    ]