# Generated by Django 4.2.5 on 2023-09-09 23:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CombinedItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('barcode', models.CharField(max_length=50)),
                ('calories', models.IntegerField()),
                ('protein', models.IntegerField()),
                ('carbs', models.IntegerField()),
                ('fats', models.IntegerField()),
                ('unit', models.CharField(max_length=50)),
                ('servingSize', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Mineral',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Supplement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('barcode', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('userName', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('joinedOn', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vitamin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SupplementVitamin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('supplementId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.supplement')),
                ('vitaminId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.vitamin')),
            ],
        ),
        migrations.CreateModel(
            name='SupplementMineral',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('mineralId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.mineral')),
                ('supplementId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.supplement')),
            ],
        ),
        migrations.CreateModel(
            name='SupplementIngredient',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('unit', models.CharField(max_length=50)),
                ('foodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
                ('supplementId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.supplement')),
            ],
        ),
        migrations.CreateModel(
            name='FoodVitamin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('foodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
                ('vitaminId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.vitamin')),
            ],
        ),
        migrations.CreateModel(
            name='FoodMineral',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('foodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
                ('mineralId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.mineral')),
            ],
        ),
        migrations.CreateModel(
            name='Consumed',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('consumedAt', models.DateTimeField(auto_now_add=True)),
                ('portion', models.IntegerField()),
                ('combinedItemId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.combineditem')),
                ('foodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
                ('supplementId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.supplement')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.users')),
            ],
        ),
        migrations.AddField(
            model_name='combineditem',
            name='userId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.users'),
        ),
        migrations.CreateModel(
            name='CombinedFoodElement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('servingSize', models.IntegerField()),
                ('combinedFoodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.combineditem')),
                ('foodId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nutrition.fooditem')),
            ],
        ),
    ]
