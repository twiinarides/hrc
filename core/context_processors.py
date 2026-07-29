from .models import SiteSetting, CustomTextSnippet

def site_settings(request):
    settings_obj = SiteSetting.objects.first()
    if not settings_obj:
        settings_obj = SiteSetting.objects.create()

    # Retrieve all custom text snippets into a dictionary
    snippets = {snippet.key: snippet.content for snippet in CustomTextSnippet.objects.all()}

    return {
        'site': settings_obj,
        'snippets': snippets,
    }
