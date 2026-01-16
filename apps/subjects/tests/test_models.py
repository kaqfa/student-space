"""
Unit tests for subjects app models.
"""
import pytest

from apps.subjects.models import Subject, Topic


@pytest.mark.django_db
class TestSubjectModel:
    """Test Subject model functionality"""
    
    def test_create_subject(self):
        """Test creating a subject"""
        subject = Subject.objects.create(
            name='Matematika',
            grade=4,
            order=1,
            color='#3B82F6'
        )
        
        assert subject.name == 'Matematika'
        assert subject.grade == 4
        assert subject.order == 1
        assert subject.color == '#3B82F6'
    
    def test_subject_str_representation(self, subject):
        """Test __str__ method"""
        assert 'Matematika' in str(subject)
        assert 'Kelas 4' in str(subject)
    
    def test_subject_ordering(self):
        """Test subjects are ordered by grade, order, name"""
        s1 = Subject.objects.create(name='IPA', grade=4, order=2)
        s2 = Subject.objects.create(name='Matematika', grade=4, order=1)
        s3 = Subject.objects.create(name='Bahasa', grade=3, order=1)
        
        subjects = list(Subject.objects.all())
        # Should be ordered by grade, then order
        assert subjects[0] == s3  # Grade 3
        assert subjects[1] == s2  # Grade 4, order 1
        assert subjects[2] == s1  # Grade 4, order 2
    
    def test_subject_unique_together(self):
        """Test unique constraint on name and grade"""
        Subject.objects.create(name='Matematika', grade=4)
        
        with pytest.raises(Exception):  # IntegrityError
            Subject.objects.create(name='Matematika', grade=4)


@pytest.mark.django_db
class TestTopicModel:
    """Test Topic model functionality"""
    
    def test_create_topic(self, subject):
        """Test creating a topic"""
        topic = Topic.objects.create(
            subject=subject,
            name='Pecahan',
            description='Belajar tentang pecahan',
            order=1
        )
        
        assert topic.subject == subject
        assert topic.name == 'Pecahan'
        assert topic.description == 'Belajar tentang pecahan'
        assert topic.order == 1
    
    def test_topic_str_representation(self, topic):
        """Test __str__ method"""
        str_repr = str(topic)
        assert 'Matematika' in str_repr
        assert 'Pecahan' in str_repr
    
    def test_topic_ordering(self, subject):
        """Test topics are ordered by subject, order, name"""
        t1 = Topic.objects.create(subject=subject, name='Geometri', order=2)
        t2 = Topic.objects.create(subject=subject, name='Pecahan', order=1)
        
        topics = list(Topic.objects.filter(subject=subject))
        assert topics[0] == t2  # order 1
        assert topics[1] == t1  # order 2
    
    def test_topic_subject_relationship(self, topic):
        """Test topic-subject relationship"""
        assert topic.subject.name == 'Matematika'
        assert topic in topic.subject.topics.all()
