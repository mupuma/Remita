from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_remitaauth'),
    ]

    operations = [
        # Drop uniqueness on invoiceid by altering the field
        migrations.AlterField(
            model_name='processeddeposits',
            name='invoiceid',
            field=models.CharField(max_length=255),
        ),
        # Ensure unique together for (project, invoiceid)
        migrations.AlterUniqueTogether(
            name='processeddeposits',
            unique_together={('project', 'invoiceid')},
        ),
    ]
