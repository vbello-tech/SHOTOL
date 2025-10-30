import geoip2.database
from django.conf import settings
import os


def get_client_ip(self, request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def track_click():
    pass


class GeoLocationService:
    """Service to get geolocation data from IP addresses."""

    def __init__(self):
        self.city_reader = None
        self.country_reader = None

        try:
            city_db_path = os.path.join(settings.GEOIP_PATH, settings.GEOIP_CITY)
            country_db_path = os.path.join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY)

            if os.path.exists(city_db_path):
                self.city_reader = geoip2.database.Reader(city_db_path)

            if os.path.exists(country_db_path):
                self.country_reader = geoip2.database.Reader(country_db_path)
        except Exception as e:
            print(f"GeoIP database initialization error: {e}")

    def get_location(self, ip_address):
        """
        Get location data from IP address.

        Args:
            ip_address (str): IP address to lookup

        Returns:
            dict: Location data including country, city, region
        """
        location_data = {
            'country': '',
            'country_code': '',
            'city': '',
            'region': '',
        }

        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            return location_data

        try:
            # Try city database first (includes all data)
            if self.city_reader:
                response = self.city_reader.city(ip_address)
                location_data['country'] = response.country.name or ''
                location_data['country_code'] = response.country.iso_code or ''
                location_data['city'] = response.city.name or ''
                location_data['region'] = response.subdivisions.most_specific.name or ''

            # Fallback to country database
            elif self.country_reader:
                response = self.country_reader.country(ip_address)
                location_data['country'] = response.country.name or ''
                location_data['country_code'] = response.country.iso_code or ''

        except geoip2.errors.AddressNotFoundError:
            # IP not found in database
            pass
        except Exception as e:
            print(f"GeoIP lookup error for {ip_address}: {e}")

        return location_data

    def __del__(self):
        """Clean up database connections."""
        if self.city_reader:
            self.city_reader.close()
        if self.country_reader:
            self.country_reader.close()


geo_service = GeoLocationService()
