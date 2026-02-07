# Generated manually

from django.db import migrations, models
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='llm_provider',
            field=models.CharField(
                choices=[
                    ('local', 'Local Model'),
                    ('openai', 'OpenAI'),
                    ('comet', 'Comet API'),
                    ('custom', 'Custom Provider')
                ],
                default='local',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='llm_api_key',
            field=encrypted_model_fields.fields.EncryptedCharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='llm_model',
            field=models.CharField(blank=True, default='claude-sonnet-4-5', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='custom_api_base_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='custom_provider_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
