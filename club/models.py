from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator
from django.db import models
from PIL import Image, ImageOps

POSITIONS = [(p, p) for p in ('Goalkeeper', 'Defender', 'Midfielder', 'Forward')]
PHOTO_CATEGORIES = [
    ('match-day', 'Match Days'),
    ('training', 'Training Sessions'),
    ('team', 'Team Photos'),
    ('celebrations', 'Celebrations'),
    ('tournaments', 'Tournaments'),
    ('awards', 'Awards and Achievements'),
]
REGISTRATION_STATUS = [
    ('new', 'New'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]


def shrink(field, px, square=False):
    if not field or field._committed:
        return
    img = ImageOps.exif_transpose(Image.open(field)).convert('RGB')
    if square:
        img = ImageOps.fit(img, (px, px))
    else:
        img.thumbnail((px, px))
    buf = BytesIO()
    img.save(buf, 'JPEG', quality=82)
    field.save(Path(field.name).stem + '.jpg', ContentFile(buf.getvalue()), save=False)


class Player(models.Model):
    name = models.CharField(max_length=60)
    number = models.PositiveSmallIntegerField('shirt number', null=True, blank=True, validators=[MaxValueValidator(99)])
    position = models.CharField(max_length=12, choices=POSITIONS)
    photo = models.ImageField(upload_to='players/', blank=True)
    bio = models.TextField(blank=True)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    appearances = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return ''.join(w[0] for w in self.name.split()[:2]).upper()

    def save(self, *args, **kwargs):
        shrink(self.photo, 400, square=True)
        super().save(*args, **kwargs)


class Fixture(models.Model):
    opponent = models.CharField(max_length=60)
    date = models.DateField()
    time = models.TimeField('kick-off time', null=True, blank=True)
    venue = models.CharField(max_length=80, blank=True)
    competition = models.CharField(max_length=80, blank=True)
    summary = models.TextField(blank=True)
    is_home = models.BooleanField('home game', default=True)
    our_score = models.PositiveSmallIntegerField(null=True, blank=True)
    their_score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f'Three Feathers v {self.opponent}'

    @property
    def played(self):
        return self.our_score is not None and self.their_score is not None

    @property
    def outcome(self):
        if not self.played:
            return None
        if self.our_score > self.their_score:
            return ('w', 'Win')
        if self.our_score < self.their_score:
            return ('l', 'Loss')
        return ('d', 'Draw')


class Photo(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=20, choices=PHOTO_CATEGORIES, default='match-day')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created', '-id']

    def save(self, *args, **kwargs):
        shrink(self.image, 1400)
        super().save(*args, **kwargs)


class ClubInfo(models.Model):
    about = models.TextField(blank=True)
    history = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    values = models.TextField(blank=True)
    training = models.CharField('training days and times', max_length=80, blank=True)
    pitch = models.CharField('home pitch', max_length=80, blank=True)
    contact = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    club_email = models.EmailField(blank=True)

    @classmethod
    def get(cls):
        return cls.objects.get_or_create(pk=1)[0]


class Registration(models.Model):
    full_name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    experience = models.TextField(blank=True)
    position = models.CharField(max_length=20, choices=POSITIONS, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REGISTRATION_STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.full_name
