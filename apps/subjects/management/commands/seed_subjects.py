from django.core.management.base import BaseCommand
from apps.subjects.models import Subject, Topic

class Command(BaseCommand):
    help = "Seed initial subjects and topics for SD (Grade 1-6)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding subjects and topics...")

        subjects_data = [
            {"name": "Matematika", "icon": "calculator", "color": "blue"},
            {"name": "Bahasa Indonesia", "icon": "book", "color": "red"},
            {"name": "IPA", "icon": "beaker", "color": "green"},
            {"name": "IPS", "icon": "globe", "color": "yellow"},
            {"name": "PPKn", "icon": "users", "color": "orange"},
        ]

        # Common topics per subject (simplified for seeding)
        topics_map = {
            "Matematika": [
                "Bilangan Cacah", "Penjumlahan dan Pengurangan", "Perkalian dan Pembagian", 
                "Pecahan", "Bangun Datar", "Bangun Ruang", "Statistika"
            ],
            "Bahasa Indonesia": [
                "Membaca Pemahaman", "Menulis", "Puisi", "Dongeng", "Tata Bahasa"
            ],
            "IPA": [
                "Makhluk Hidup", "Energi", "Lingkungan", "Tata Surya", "Gaya dan Gerak"
            ],
            "IPS": [
                "Lingkungan Alam", "Sejarah", "Kegiatan Ekonomi", "Koperasi", "Peta"
            ],
            "PPKn": [
                "Pancasila", "Hak dan Kewajiban", "Gotong Royong", "Keberagaman", "Persatuan"
            ]
        }

        created_subjects = 0
        created_topics = 0

        for grade in range(1, 7):
            for subj in subjects_data:
                # Create Subject for each grade
                # Note: Subject model has 'grade' field, so we create distinct Subject entries for each grade?
                # Let's check model definition. Yes: field 'grade'.
                
                subject_obj, created = Subject.objects.get_or_create(
                    name=subj["name"],
                    grade=grade,
                    defaults={
                        "icon": subj["icon"],
                        "color": subj["color"],
                        "order": 1
                    }
                )
                
                if created:
                    created_subjects += 1
                
                # Create dummy topics for this subject
                # We just take 2-3 topics from the list randomly or sequentially
                key = subj["name"]
                relevant_topics = topics_map.get(key, [])
                
                # Just add all of them for now
                for i, topic_name in enumerate(relevant_topics):
                     Topic.objects.get_or_create(
                        subject=subject_obj,
                        name=topic_name,
                        defaults={
                            "description": f"Materi {topic_name} untuk kelas {grade}",
                            "order": i + 1
                        }
                    )
                     created_topics += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_subjects} subjects and {created_topics} topics."))
