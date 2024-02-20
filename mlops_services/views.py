from crawler.live_activity import crawl_live_activity
from django.http import JsonResponse


def crawl_liveA(request):
    crawl_live_activity()
    return JsonResponse({'message': 'Live Activity Crawler Completed.'})
