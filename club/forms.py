from django import forms

from .models import ClubInfo, Fixture, Photo, Player, Registration


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'number', 'position', 'photo', 'bio', 'goals', 'assists', 'appearances']
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}


class FixtureForm(forms.ModelForm):
    class Meta:
        model = Fixture
        fields = ['opponent', 'date', 'time', 'venue', 'competition', 'is_home', 'summary']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'summary': forms.Textarea(attrs={'rows': 3}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Fixture
        fields = ['our_score', 'their_score', 'summary']
        widgets = {'summary': forms.Textarea(attrs={'rows': 3})}


class ClubForm(forms.ModelForm):
    class Meta:
        model = ClubInfo
        fields = ['about', 'history', 'mission', 'vision', 'values', 'training', 'pitch', 'contact', 'phone', 'email']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
            'history': forms.Textarea(attrs={'rows': 4}),
            'mission': forms.Textarea(attrs={'rows': 3}),
            'vision': forms.Textarea(attrs={'rows': 3}),
            'values': forms.Textarea(attrs={'rows': 4}),
        }


class JoinForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['full_name', 'age', 'phone', 'email', 'experience', 'position', 'message']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 3}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    subject = forms.CharField(max_length=160)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiImageField(forms.ImageField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        files = [f for f in (data if isinstance(data, (list, tuple)) else [data]) if f]
        if not files:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        return [super(MultiImageField, self).clean(f, initial) for f in files]


class PhotoForm(forms.Form):
    images = MultiImageField(label='Photos')
    caption = forms.CharField(max_length=80, required=False, help_text='Optional. Applied to every photo you upload.')
    category = forms.ChoiceField(choices=[('match-day', 'Match Days'), ('training', 'Training Sessions'), ('team', 'Team Photos'), ('celebrations', 'Celebrations'), ('tournaments', 'Tournaments'), ('awards', 'Awards and Achievements')], initial='match-day')

    def save(self):
        return [Photo.objects.create(image=i, caption=self.cleaned_data['caption'], category=self.cleaned_data['category']) for i in self.cleaned_data['images']]
