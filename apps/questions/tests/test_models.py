"""
Unit tests for questions app models.
"""
import pytest

from apps.questions.models import Question, Tag, KompetensiDasar


@pytest.mark.django_db
class TestQuestionModel:
    """Test Question model functionality"""
    
    def test_create_pilgan_question(self, topic, admin_user):
        """Test creating a multiple choice question"""
        question = Question.objects.create(
            topic=topic,
            question_text='Berapa hasil dari 1/2 + 1/4?',
            question_type='pilgan',
            difficulty='mudah',
            options=['1/2', '3/4', '1/4', '1'],
            answer_key='B',
            explanation='1/2 + 1/4 = 2/4 + 1/4 = 3/4',
            points=10,
            estimated_time=60,
            created_by=admin_user
        )
        
        assert question.question_type == 'pilgan'
        assert len(question.options) == 4
        assert question.answer_key == 'B'
        assert question.points == 10
    
    def test_create_essay_question(self, topic, admin_user):
        """Test creating an essay question"""
        question = Question.objects.create(
            topic=topic,
            question_text='Jelaskan apa itu pecahan',
            question_type='essay',
            difficulty='sedang',
            answer_key='Pecahan adalah bilangan yang menyatakan bagian dari keseluruhan',
            points=20,
            created_by=admin_user
        )
        
        assert question.question_type == 'essay'
        assert question.options is None
        assert question.points == 20
    
    def test_question_str_representation(self, question):
        """Test __str__ method"""
        str_repr = str(question)
        assert 'Pecahan' in str_repr  # topic name
        assert 'Berapa hasil' in str_repr  # question text preview
    
    def test_get_subject_method(self, question):
        """Test get_subject method"""
        subject = question.get_subject()
        assert subject.name == 'Matematika'
    
    def test_question_with_tags(self, question, tag):
        """Test question with tags"""
        question.tags.add(tag)
        
        assert tag in question.tags.all()
        assert question in tag.questions.all()
    
    def test_question_with_kd(self, question, kompetensi_dasar):
        """Test question with Kompetensi Dasar"""
        question.kompetensi_dasar.add(kompetensi_dasar)
        
        assert kompetensi_dasar in question.kompetensi_dasar.all()
        assert question in kompetensi_dasar.questions.all()


@pytest.mark.django_db
class TestTagModel:
    """Test Tag model functionality"""
    
    def test_create_tag(self):
        """Test creating a tag"""
        tag = Tag.objects.create(
            name='operasi-hitung',
            category=Tag.Category.SKILL,
            description='Kemampuan operasi hitung dasar'
        )
        
        assert tag.name == 'operasi-hitung'
        assert tag.category == Tag.Category.SKILL
    
    def test_tag_str_representation(self, tag):
        """Test __str__ method"""
        assert str(tag) == 'operasi-hitung'
    
    def test_tag_unique_name(self):
        """Test tag name must be unique"""
        Tag.objects.create(name='test-tag')
        
        with pytest.raises(Exception):  # IntegrityError
            Tag.objects.create(name='test-tag')
    
    def test_tag_categories(self):
        """Test different tag categories"""
        skill_tag = Tag.objects.create(name='skill-tag', category=Tag.Category.SKILL)
        topic_tag = Tag.objects.create(name='topic-tag', category=Tag.Category.TOPIC)
        diff_tag = Tag.objects.create(name='diff-tag', category=Tag.Category.DIFFICULTY)
        
        assert skill_tag.category == Tag.Category.SKILL
        assert topic_tag.category == Tag.Category.TOPIC
        assert diff_tag.category == Tag.Category.DIFFICULTY


@pytest.mark.django_db
class TestKompetensiDasarModel:
    """Test KompetensiDasar model functionality"""
    
    def test_create_kd(self, subject):
        """Test creating a Kompetensi Dasar"""
        kd = KompetensiDasar.objects.create(
            code='3.1',
            description='Memahami pecahan sederhana',
            grade=4,
            subject=subject
        )
        
        assert kd.code == '3.1'
        assert kd.grade == 4
        assert kd.subject == subject
    
    def test_kd_str_representation(self, kompetensi_dasar):
        """Test __str__ method"""
        str_repr = str(kompetensi_dasar)
        assert '3.1' in str_repr
        assert 'Memahami pecahan' in str_repr
    
    def test_kd_ordering(self, subject):
        """Test KD ordering by grade, subject, code"""
        kd1 = KompetensiDasar.objects.create(
            code='4.1', description='Test', grade=4, subject=subject
        )
        kd2 = KompetensiDasar.objects.create(
            code='3.1', description='Test', grade=4, subject=subject
        )
        
        kds = list(KompetensiDasar.objects.filter(subject=subject))
        assert kds[0] == kd2  # 3.1 comes before 4.1
        assert kds[1] == kd1
