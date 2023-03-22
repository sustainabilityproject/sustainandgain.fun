from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    template_name = "about/privacy_policy.html"

class AboutView(TemplateView):
    template_name = "about/about.html"
