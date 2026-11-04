from functools import wraps
from hmac import compare_digest
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import F, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ClubForm, ContactForm, FixtureForm, JoinForm, PhotoForm, PlayerForm, ResultForm
from .models import POSITIONS, ClubInfo, Fixture, Photo, Player, Registration


def coach_required(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not request.session.get('coach'):
            return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")
        return view(request, *args, **kwargs)
    return inner


def safe_next(request, default):
    target = request.POST.get('next') or request.GET.get('next') or ''
    ok = url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()})
    return target if ok else default


def ranked(key, limit=10):
    top = list(Player.objects.filter(**{key + '__gt': 0}).order_by('-' + key, 'name')[:limit])
    best = getattr(top[0], key) if top else 1
    rows = []
    for p in top:
        value = getattr(p, key)
        rank = 1 + next(i for i, q in enumerate(top) if getattr(q, key) == value)
        rows.append((rank, p, value, round(value / best * 100)))
    return rows


def home(request):
    totals = Player.objects.aggregate(g=Sum('goals'), a=Sum('assists'), apps=Sum('appearances'))
    played = Fixture.objects.filter(our_score__isnull=False, their_score__isnull=False)
    goals_scored = Fixture.objects.filter(our_score__isnull=False).aggregate(total=Sum('our_score'))['total'] or 0
    wins = Fixture.objects.filter(our_score__isnull=False).filter(our_score__gt=F('their_score')).count()
    recent = played.order_by('-date')[:3]
    club = ClubInfo.get()
    if request.method == 'POST' and not request.session.get('coach'):
        form = JoinForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for your interest. The coach will review your registration.')
            return redirect('home')
    else:
        form = None
    return render(request, 'home.html', {
        'players': Player.objects.count(),
        'goals': totals['g'] or 0,
        'assists': totals['a'] or 0,
        'matches_played': played.count(),
        'matches_won': wins,
        'goals_scored': goals_scored,
        'upcoming_matches': Fixture.objects.filter(our_score__isnull=True).count(),
        'next': Fixture.objects.filter(our_score__isnull=True).first(),
        'club': club,
        'scorer': (ranked('goals', 1) or [None])[0],
        'assister': (ranked('assists', 1) or [None])[0],
        'recent_results': recent,
        'photos': Photo.objects.all()[:3],
        'values': [v.strip() for v in (club.values or 'Teamwork, Discipline, Respect, Commitment, Sportsmanship, Excellence').split(',') if v.strip()],
        'join_form': form,
    })


def about(request):
    club = ClubInfo.get()
    return render(request, 'about.html', {
        'club': club,
        'values': [v.strip() for v in (club.values or 'Teamwork, Discipline, Respect, Commitment, Sportsmanship, Excellence').split(',') if v.strip()],
    })


def results(request):
    return render(request, 'results.html', {
        'results': Fixture.objects.filter(our_score__isnull=False, their_score__isnull=False).order_by('-date'),
    })


def join(request):
    form = JoinForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your club registration has been sent successfully. The coach will be in touch soon.')
        return redirect('home')
    return render(request, 'join.html', {'form': form})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        messages.success(request, 'Thanks for your message. The coach will get back to you soon.')
        return redirect('home')
    return render(request, 'contact.html', {'form': form, 'club': ClubInfo.get()})


def squad(request):
    players = Player.objects.all()
    pos = request.GET.get('pos', '')
    q = request.GET.get('q', '').strip()
    if pos in dict(POSITIONS):
        players = players.filter(position=pos)
    if q:
        cond = Q(name__icontains=q)
        if q.isdigit():
            cond |= Q(number=int(q))
        players = players.filter(cond)
    return render(request, 'squad.html', {
        'players': players, 'positions': [p for p, _ in POSITIONS], 'pos': pos, 'q': q,
        'total': Player.objects.count(),
    })


def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, 'player_detail.html', {'player': player})


def leaders(request):
    return render(request, 'leaders.html', {'scorers': ranked('goals'), 'assisters': ranked('assists')})


def fixtures(request):
    return render(request, 'fixtures.html', {
        'upcoming': Fixture.objects.filter(our_score__isnull=True),
        'played': Fixture.objects.filter(our_score__isnull=False).order_by('-date'),
    })


def gallery(request):
    return render(request, 'gallery.html', {'photos': Photo.objects.all()})


def login(request):
    key = 'login-fails:' + request.META.get('REMOTE_ADDR', '?')
    error = ''
    if request.method == 'POST':
        if cache.get(key, 0) >= 5:
            error = 'Too many wrong attempts. Try again in 10 minutes.'
        elif compare_digest(request.POST.get('password', '').strip().encode(), settings.COACH_PASSWORD.encode()):
            cache.delete(key)
            request.session.cycle_key()
            request.session['coach'] = True
            return redirect(safe_next(request, reverse('dashboard')))
        else:
            cache.set(key, cache.get(key, 0) + 1, 600)
            error = 'That password is not correct. Try again.'
    return render(request, 'login.html', {'error': error, 'next': request.GET.get('next', '')})


@coach_required
def dashboard(request):
    registrations = Registration.objects.filter(status='new')
    return render(request, 'coach_dashboard.html', {
        'players': Player.objects.count(),
        'matches': Fixture.objects.count(),
        'goals': Player.objects.aggregate(total=Sum('goals'))['total'] or 0,
        'upcoming': Fixture.objects.filter(our_score__isnull=True).count(),
        'recent_results': Fixture.objects.filter(our_score__isnull=False).count(),
        'registrations': registrations.count(),
        'registrations_list': registrations[:5],
    })


@coach_required
def registrations(request):
    reg_list = Registration.objects.all()
    return render(request, 'admin_registrations.html', {'registrations': reg_list})


@coach_required
@require_POST
def registration_action(request, pk, status):
    if status not in {'accepted', 'rejected'}:
        raise Http404
    reg = get_object_or_404(Registration, pk=pk)
    reg.status = status
    reg.save(update_fields=['status'])
    messages.success(request, f'Registration marked as {status}.')
    return redirect('registrations')


@coach_required
def admin_players(request):
    return render(request, 'admin_players.html', {'players': Player.objects.all()})


@coach_required
def admin_fixtures(request):
    return render(request, 'admin_fixtures.html', {
        'fixtures': Fixture.objects.all().order_by('-date'),
        'upcoming': Fixture.objects.filter(our_score__isnull=True),
        'played': Fixture.objects.filter(our_score__isnull=False).order_by('-date'),
    })


@coach_required
def admin_photos(request):
    return render(request, 'admin_photos.html', {'photos': Photo.objects.all()})


@require_POST
def logout(request):
    request.session.flush()
    return redirect('home')


KINDS = {
    'player': (PlayerForm, 'Add a player', 'squad'),
    'fixture': (FixtureForm, 'Add a game', 'fixtures'),
    'photo': (PhotoForm, 'Add match photos', 'gallery'),
    'photos': (PhotoForm, 'Add match photos', 'gallery'),
    'club': (ClubForm, 'Edit club info', 'home'),
}
MODELS = {
    'player': (Player, 'squad'),
    'fixture': (Fixture, 'fixtures'),
    'photo': (Photo, 'gallery'),
    'photos': (Photo, 'gallery'),
}


@coach_required
def add(request, kind):
    if kind not in KINDS:
        raise Http404
    form_class, title, back = KINDS[kind]
    extra = {'instance': ClubInfo.get()} if kind == 'club' else {}
    form = form_class(request.POST or None, request.FILES or None, **extra)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Saved. Everyone can see it now.')
        return redirect(back)
    return render(request, 'form.html', {'form': form, 'title': title, 'back': back})


@coach_required
@require_POST
def delete(request, kind, pk):
    if kind not in MODELS:
        raise Http404
    model, back = MODELS[kind]
    get_object_or_404(model, pk=pk).delete()
    messages.success(request, 'Removed.')
    return redirect(back)


@coach_required
@require_POST
def bump(request, pk, field, step):
    if field not in ('goals', 'assists') or step not in ('up', 'down'):
        raise Http404
    player = get_object_or_404(Player, pk=pk)
    setattr(player, field, max(0, getattr(player, field) + (1 if step == 'up' else -1)))
    player.save(update_fields=[field])
    return redirect(safe_next(request, reverse('squad')))


@coach_required
@require_POST
def result(request, pk):
    fixture = get_object_or_404(Fixture, pk=pk)
    form = ResultForm(request.POST, instance=fixture)
    if form.is_valid() and form.cleaned_data['our_score'] is not None and form.cleaned_data['their_score'] is not None:
        form.save()
        messages.success(request, 'Result saved.')
    else:
        messages.error(request, 'Enter both scores to save the result.')
    return redirect('fixtures')
