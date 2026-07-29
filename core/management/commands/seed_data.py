from django.core.management.base import BaseCommand
from core.models import SiteSetting, Director
from programs.models import Program

class Command(BaseCommand):
    help = "Populate initial data for Hope Reception Centre"

    def handle(self, *args, **options):
        site, created = SiteSetting.objects.get_or_create(id=1)
        site.site_name = "Hope Reception Centre"
        site.tagline = "Giving Hope to Vulnerable Children Since 2003"
        site.established_year = 2003
        site.address = "Kijuguta ward, Northern division, Kabale municipality, Uganda"
        site.phone = "+256 772 123456"
        site.email = "info@hopereceptioncentre.org"
        site.mtn_mobile_money = "+256 772 123456 (Enid Origumusiriza)"
        site.airtel_money = "+256 752 654321 (Rev. Michael Asiimwe)"
        site.bank_details = "Bank: Stanbic Bank Uganda\nAccount Name: Hope Reception Centre\nAccount Number: 9030001234567\nBranch: Kabale Branch"
        site.save()

        directors_data = [
            ("Enid Origumusiriza CM", "Director / Founder", 1),
            ("Rev. Michael Asiimwe", "Executive Director", 2),
            ("Patience Asiimwe", "Director", 3),
            ("Janiffer Agaba", "Treasurer", 4),
            ("Godfrey Dutki", "Director", 5),
        ]

        for name, title, order in directors_data:
            Director.objects.get_or_create(
                name=name,
                defaults={'title': title, 'order': order}
            )

        programs_data = [
            ("Child Reception & Protection", "child-reception", "Temporary reception, shelter, rehabilitation, and safety for vulnerable, abandoned, and orphaned children.", "fa-hands-holding-child"),
            ("Formal Digital & In-Person Counseling", "counseling-services", "Individual and group counseling sessions, trauma healing, and online digital support for youth and families.", "fa-comments-dollar"),
            ("Education & Vocational Support", "education-support", "Providing school fees, books, uniforms, and vocational skills training to empower children for self-reliance.", "fa-graduation-cap"),
        ]

        for title, slug, summary, icon in programs_data:
            Program.objects.get_or_create(
                slug=slug,
                defaults={'title': title, 'summary': summary, 'description': summary, 'icon': icon}
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated seed data for Hope Reception Centre!"))
