from django import forms
from .models import Question, Tag, KompetensiDasar

class QuestionForm(forms.ModelForm):
    # Virtual fields for options (handling simple Multiple Choice scenario)
    option_a = forms.CharField(required=False, label="Option A", widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}))
    option_b = forms.CharField(required=False, label="Option B", widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}))
    option_c = forms.CharField(required=False, label="Option C", widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}))
    option_d = forms.CharField(required=False, label="Option D", widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}))
    option_e = forms.CharField(required=False, label="Option E", widget=forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}))

    class Meta:
        model = Question
        fields = [
            "topic",
            "question_text",
            "question_type",
            "difficulty",
            "answer_key",
            "explanation",
            "image",
            "has_math",
            "estimated_time",
            "points",
            "tags",
            "kompetensi_dasar",
        ]
        widgets = {
             "question_text": forms.Textarea(attrs={'rows': 4, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "explanation": forms.Textarea(attrs={'rows': 3, 'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "topic": forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "question_type": forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "difficulty": forms.Select(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "answer_key": forms.TextInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "estimated_time": forms.NumberInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "points": forms.NumberInput(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "tags": forms.SelectMultiple(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
             "kompetensi_dasar": forms.SelectMultiple(attrs={'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.options:
            options = self.instance.options
            if isinstance(options, list):
                if len(options) > 0: self.fields['option_a'].initial = options[0]
                if len(options) > 1: self.fields['option_b'].initial = options[1]
                if len(options) > 2: self.fields['option_c'].initial = options[2]
                if len(options) > 3: self.fields['option_d'].initial = options[3]
                if len(options) > 4: self.fields['option_e'].initial = options[4]

    def clean(self):
        cleaned_data = super().clean()
        q_type = cleaned_data.get("question_type")
        
        if q_type == "pilgan":
            opts = []
            if cleaned_data.get("option_a"): opts.append(cleaned_data.get("option_a"))
            if cleaned_data.get("option_b"): opts.append(cleaned_data.get("option_b"))
            if cleaned_data.get("option_c"): opts.append(cleaned_data.get("option_c"))
            if cleaned_data.get("option_d"): opts.append(cleaned_data.get("option_d"))
            if cleaned_data.get("option_e"): opts.append(cleaned_data.get("option_e"))
            
            if len(opts) < 2:
                raise forms.ValidationError("Pilihan Ganda minimal harus punya 2 opsi.")
            
            cleaned_data["options"] = opts
            self.instance.options = opts 
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('question_type') == 'pilgan' and 'options' in self.cleaned_data:
             instance.options = self.cleaned_data['options']
        
        if commit:
            instance.save()
            self.save_m2m() 
        return instance


class QuestionImportForm(forms.Form):
    file = forms.FileField(
        label="JSON File", 
        help_text="Upload .json file containing list of questions.",
        widget=forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'})
    )
