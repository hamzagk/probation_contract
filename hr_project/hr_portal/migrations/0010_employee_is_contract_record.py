from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hr_portal", "0009_populate_contract_dates"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="is_contract_record",
            field=models.BooleanField(
                default=False,
                help_text="Tracks employees managed through the contract renewal module",
            ),
        ),
    ]
