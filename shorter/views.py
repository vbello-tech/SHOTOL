import random
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404, HttpResponse
from django.views import View
from django.utils import timezone
from .models import URL, UrlHistory
from user_agents import parse
from django.contrib import messages
from datetime import timedelta
from .utils import geo_service, track_click
from .cache import URLCacheService
# Create your views here.


def generate_slug():
    characters = string.ascii_lowercase + string.digits
    slug = ''.join(random.choice(characters) for _ in range(5))
    return slug


class HomeView(View):
    """Display the home page with URL shortener form."""

    def get(self, request):
        return render(request, 'home.html')

    def post(self, request):
        original_url = request.POST.get('url', '').strip()
        expiry_date = request.POST.get('expiry_date')

        if not original_url:
            messages.error(request, 'Please enter a URL')
            return render(request, 'home.html')

        # Validate URL format
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'https://' + original_url

        # Check if URL already exists
        existing = URL.objects.filter(url=original_url, is_active=True, owner=request.user).first()
        if existing:
            messages.info(request, 'This URL was already shortened by you!')
            return render(request, 'home.html')
        else:
            sh_url = URL.objects.create(
                owner=request.user,
                url=original_url,
                slug=generate_slug(),
                expires_at=expiry_date or None,
            )
            messages.success(request, 'URL shortened successfully!')

        short_url = request.build_absolute_uri(f'/{sh_url.slug}/')

        context = {
            'short_url': short_url,
            'slug': sh_url.slug,
            'original_url': original_url
        }

        return render(request, 'home.html', context)


class RedirectView(View):
    """Redirect to original URL and track analytics."""

    def get(self, request, slug):
        cached_data = URLCacheService.get_url(slug)
        if cached_data:
            url = cached_data['url']
            is_active = cached_data['is_active']
            expires_at = cached_data['expires_at']

            if expires_at and expires_at < timezone.now():
                return HttpResponse("This link has expired")

            return redirect(url)
        else:
            shortened_url = get_object_or_404(URL, slug=slug, is_active=True)

            # Check if expired
            if shortened_url.expires_at and shortened_url.expires_at < timezone.now():
                return HttpResponse("This link has expired")

            # cache data
            cached_data = {
                'url': shortened_url.url,
                'is_active': shortened_url.is_active,
                'expires_at': shortened_url.expires_at
            }

            URLCacheService.set_url(slug, cached_data)
            # Increment basic counter
            shortened_url.increment_click()

            # Track the click
            """Track detailed analytics for this click."""

            # Get IP address
            ip_address = self.get_client_ip(request)

            # Get country and city
            location = geo_service.get_location(ip_address)

            # Parse user agent
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_string)

            # Determine device type
            if user_agent.is_mobile:
                device_type = 'mobile'
            elif user_agent.is_tablet:
                device_type = 'tablet'
            else:
                device_type = 'desktop'

            # Create click record
            UrlHistory.objects.create(
                url=shortened_url,
                ip_address=ip_address,
                user_agent=user_agent_string,
                device_type=device_type,
                browser=user_agent.browser.family,
                operating_system=user_agent.os.family,
                country=location['country'],
                city=location['city'],
            )

            # Redirect to original URL
            return redirect(shortened_url.url)

    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AnalyticsView(View):
    """View analytics for a shortened URL."""

    def get(self, request, slug):
        shortened_url = get_object_or_404(URL, slug=slug)

        # Get all clicks
        clicks = shortened_url.clicks.all()

        # Clicks by device
        device_stats = {}
        for click in clicks:
            device = click.device_type or 'unknown'
            device_stats[device] = device_stats.get(device, 0) + 1

        # Clicks over time (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_clicks = clicks.filter(clicked_at__gte=seven_days_ago)

        context = {
            'shortened_url': shortened_url,
            'device_stats': device_stats,
            'clicks_last_7_days': recent_clicks.count(),
            'recent_clicks': clicks[:20]  # Last 20 clicks
        }

        return render(request, 'analytics.html', context)
