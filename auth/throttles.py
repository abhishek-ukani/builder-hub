from rest_framework.throttling import SimpleRateThrottle


class LoginFailRateThrottle(SimpleRateThrottle):
    scope = "login_fail"

    def get_cache_key(self, request, view):
        # Throttle based on the username being attempted or IP
        ident = request.data.get("username", self.get_ident(request))
        return self.cache_format % {"scope": self.scope, "ident": ident}
