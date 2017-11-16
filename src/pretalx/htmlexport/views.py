from bakery.views import BuildableDetailView
from django.conf import settings

from pretalx.agenda.views.schedule import ScheduleView
from pretalx.agenda.views.speaker import SpeakerView
from pretalx.agenda.views.talk import TalkView
from pretalx.person.models import SpeakerProfile
from pretalx.schedule.models import Schedule
from pretalx.submission.models import Submission


class PretalxExportContextMixin():
    def build_object(self, obj):
        self._object = obj
        super().build_object(obj)

    def create_request(self, *args, **kwargs):
        request = super().create_request(*args, **kwargs)
        request.event = self._object.event  # django-bakery/RequestFactory does not support middlewares
        return request

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()  # ScheduleView crashes without this

        ctx = super().get_context_data(*args, **kwargs)
        ctx['is_html_export'] = True
        return ctx

    def get_url(self, obj):
        return obj.urls.public

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(event=settings.EXPORTING_EVENT)
        return qs


# current schedule
class ExportScheduleView(PretalxExportContextMixin, BuildableDetailView, ScheduleView):
    queryset = Schedule.objects.filter(published__isnull=False).order_by('published')

    def get_queryset(self):
        # can't do this in queryset=, because super.get_queryset() needs filter()
        return super().get_queryset()[:1]

    def get_url(self, obj):
        return obj.event.urls.schedule


# all schedule versions
class ExportScheduleVersionsView(PretalxExportContextMixin, BuildableDetailView, ScheduleView):
    queryset = Schedule.objects.filter(version__isnull=False)


class ExportTalkView(PretalxExportContextMixin, BuildableDetailView, TalkView):
    queryset = Submission.objects.filter(slots__schedule__published__isnull=False).distinct()


class ExportSpeakerView(PretalxExportContextMixin, BuildableDetailView, SpeakerView):
    queryset = SpeakerProfile.objects.filter(user__submissions__slots__schedule__published__isnull=False).distinct()
