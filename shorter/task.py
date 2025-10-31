from celery import shared_task
from user_agents import parse
from .models import UrlHistory, URL
from .utils import geo_service
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def user_agent_str(request):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    return user_agent_string


def user_agent(request):
    return parse(user_agent_str(request))


def device(request):
    agent = user_agent(request)
    # Determine device type
    if agent.is_mobile:
        device_type = 'mobile'
    elif agent.is_tablet:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    return device_type


@shared_task()
def track_click(url_id, ip, u_a_s, d, b, os):
    shortened_url = get_object_or_404(URL, id=url_id, is_active=True)
    # Increment basic counter
    shortened_url.increment_click()

    # Get IP address
    ip_address = ip

    # Get country and city
    location = geo_service.get_location(ip_address)

    # Create click record
    UrlHistory.objects.create(
        url=shortened_url,
        ip_address=ip_address,
        user_agent=u_a_s,
        device_type=d,
        browser=b,
        operating_system=os,
        country=location['country'],
        city=location['city'],
    )

    try:
        logger.info(f"Running click tracking for {shortened_url.slug}....")
    except Exception as e:
        logger.debug(f"Unable to runtask. Message: {e}")
