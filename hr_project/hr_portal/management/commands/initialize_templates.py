from django.core.management.base import BaseCommand
from hr_portal.models import DocumentTemplate
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize default document templates'

    def handle(self, *args, **options):
        # Create default probation confirmation template
        confirmation_template_path = os.path.join(settings.BASE_DIR, 'probation_templates', 'probation_confirmation_template.txt')
        if os.path.exists(confirmation_template_path):
            with open(confirmation_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Save the template content to MEDIA_ROOT
            template_dir = os.path.join(settings.MEDIA_ROOT, 'templates')
            os.makedirs(template_dir, exist_ok=True)
            template_file_path = os.path.join(template_dir, 'probation_confirmation_template.txt')
            
            with open(template_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create the template record
            template_path_relative = 'templates/probation_confirmation_template.txt'
            template, created = DocumentTemplate.objects.get_or_create(
                name='Probation Confirmation Template',
                template_type='probation_confirmation_letter',
                defaults={
                    'description': 'Template for generating probation confirmation letters',
                    'template_file': template_path_relative,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Successfully created probation confirmation template')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Probation confirmation template already exists')
                )
        else:
            self.stdout.write(
                self.style.ERROR(f'Confirmation template file does not exist: {confirmation_template_path}')
            )

        # Create default probation extension template
        extension_template_path = os.path.join(settings.BASE_DIR, 'probation_templates', 'probation_extension_template.txt')
        if os.path.exists(extension_template_path):
            with open(extension_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Save the template content to MEDIA_ROOT
            template_file_path = os.path.join(settings.MEDIA_ROOT, 'templates', 'probation_extension_template.txt')
            
            with open(template_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create the template record
            template_path_relative = 'templates/probation_extension_template.txt'
            template, created = DocumentTemplate.objects.get_or_create(
                name='Probation Extension Template',
                template_type='probation_extension_letter',
                defaults={
                    'description': 'Template for generating probation extension letters',
                    'template_file': template_path_relative,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Successfully created probation extension template')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Probation extension template already exists')
                )
        else:
            self.stdout.write(
                self.style.ERROR(f'Extension template file does not exist: {extension_template_path}')
            )