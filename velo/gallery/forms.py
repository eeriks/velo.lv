from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from crispy_forms.bootstrap import StrictButton, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div, HTML, Field, ButtonHolder, Submit
import datetime
import re
import zipfile
import os

from velo.core.models import Competition
from velo.core.widgets import SplitDateWidget
from velo.gallery.models import Video, Photo, Album
from velo.gallery.utils import youtube_video_id
from velo.gallery.tasks import sync_album
from velo.velo.mixins.forms import RequestKwargModelFormMixin
import environ
from django.utils import timezone


class AssignNumberForm(RequestKwargModelFormMixin, forms.Form):
    # TODO: Restore field
    # numbers = PhotoNumberChoices(required=False, widget=AutoHeavySelect2MultipleWidget(select2_options={
    #     'ajax': {
    #         'dataType': 'json',
    #         'quietMillis': 100,
    #         'data': '*START*django_select2.runInContextHelper(get_number_params, selector)*END*',
    #         'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
    #     },
    #     "minimumResultsForSearch": 0,
    #     "minimumInputLength": 0,
    #     "closeOnSelect": True
    # }))

    def __init__(self, *args, **kwargs):

        self.object = kwargs.pop('object', None)
        super(AssignNumberForm, self).__init__(*args, **kwargs)

        numbers = self.object.numbers.all()
        val = []
        for number in numbers:
            val.append(number.id)

        self.fields['numbers'].initial = val


class AddVideoForm(RequestKwargModelFormMixin, forms.ModelForm):
    link = forms.URLField(label=_('Link'), help_text=_('Youtube or Vimeo link'), required=True)
    class Meta:
        model = Video
        fields = ['competition', ]

    def __init__(self, *args, **kwargs):
        super(AddVideoForm, self).__init__(*args, **kwargs)
        competitions = Competition.objects.filter(competition_date__year=datetime.datetime.now().year)
        self.fields['competition'].choices = ((obj.id, obj.get_full_name) for obj in competitions)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
                    'competition',
                    'link',
                        StrictButton('Add', css_class="btn-primary search-button-margin", type="submit"),
        )

    def clean_link(self):
        link = self.cleaned_data.get('link')
        if "youtube" not in link and "youtu.be" not in link and "vimeo" not in link:
            raise forms.ValidationError(_("You can add only youtube and vimeo videos."),)

        if "youtube" in link or "youtu.be" in link:
            if not youtube_video_id(link):
                raise forms.ValidationError(_("Incorrect youtube link."),)
        else:
            video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)
            if not video_id:
                raise forms.ValidationError(_("Incorrect vimeo link."),)

        return link


    def save(self, commit=True):
        link = self.cleaned_data.get('link')
        if "youtube" in link or "youtu.be" in link:
            self.instance.kind = 1
            self.instance.video_id = youtube_video_id(link)
        else:
            self.instance.kind = 2
            self.instance.video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)

        if self.request and self.request.user.is_authenticated():
            self.instance.created_by = self.request.user
            self.instance.modified_by = self.request.user

        messages.info(self.request, _('Video successfully added. Video must be approved by agency to be available to public.'))

        return super(AddVideoForm, self).save(commit)



class AddPhotoAlbumForm(RequestKwargModelFormMixin, forms.ModelForm):
    zip_file = forms.FileField(label=_('Zip File'), help_text=_('ZIP File containing photos'), required=True)
    class Meta:
        model = Album
        fields = ['title', 'gallery_date', 'photographer', 'competition', ]
        widgets = {
            'gallery_date': SplitDateWidget,
        }

    def __init__(self, *args, **kwargs):
        super(AddPhotoAlbumForm, self).__init__(*args, **kwargs)
        competitions = Competition.objects.filter(competition_date__year=datetime.datetime.now().year)
        self.fields['competition'].choices = ((obj.id, obj.get_full_name) for obj in competitions)

        self.fields['gallery_date'].label = ""
        self.fields['gallery_date'].initial = timezone.now()

        if self.request.user.is_authenticated():
            self.fields['photographer'].initial = self.request.user.full_name

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
                            Div(
                                Div(
                                    Field(
                                        "title",
                                        css_class="input-field if--50 if--dark js-placeholder-up"
                                    ),
                                    css_class="input-wrap w100 bottom-margin--15"
                                ),
                                css_class="col-xl-8 col-m-12 col-s-24"
                            ),
                            Div(
                                Div(
                                    Field(
                                        "photographer",
                                        css_class="input-field if--50 if--dark js-placeholder-up"
                                    ),
                                    css_class="input-wrap w100 bottom-margin--15"
                                ),
                                css_class="col-xl-8 col-m-12 col-s-24"
                            ),
                            'competition',
                            Div(
                                Div(
                                    HTML('<label for="id_gallery_date" class="js-placeholder ">Gallery date</label>'),
                                    Field(
                                        "gallery_date",
                                        wrapper_class="row"
                                    ),
                                    css_class="row row--gutters-20"
                                ),
                                css_class="w100"
                            ),
                            'zip_file',
        )

    def get_members(self, zip):
        parts = []
        for name in zip.namelist():
            name = name
            if name.startswith('__MACOSX'):
                continue
            if not name.endswith('/'):
                parts.append(name.split('/')[:-1])

        prefix = os.path.commonprefix(parts) or ''
        if prefix:
            prefix = '/'.join(prefix) + '/'
        offset = len(prefix)
        for zipinfo in zip.infolist():
            name = zipinfo.filename

            if name.startswith('__MACOSX'):
                continue

            ext = os.path.splitext(name)[1].lower()
            if len(name) > offset and ext in ('.jpg', '.jpeg'):
                zipinfo.filename = "%s%s" % (slugify(name[offset:-len(ext)]), ext)
                yield zipinfo


    def save(self, commit=True):
        obj = super(AddPhotoAlbumForm, self).save(commit)

        year = obj.gallery_date.year
        gallery_folder = slugify('%s-%s' % (obj.id, obj.title))
        gallery_path = str(environ.Path(settings.MEDIA_ROOT).path('gallery').path(str(year)).path(gallery_folder))
        if not os.path.exists(gallery_path):
            os.makedirs(gallery_path)

        obj.folder = 'velo/media/gallery/%i/%s' % (year, gallery_folder)
        obj.save()

        zip_file = self.cleaned_data.get('zip_file')

        with zipfile.ZipFile(zip_file.temporary_file_path(), "r") as z:
            z.extractall(gallery_path, self.get_members(z))

        sync_album.delay(obj.id)

        return obj





class VideoSearchForm(RequestKwargModelFormMixin, forms.Form):
    competition = forms.ChoiceField(choices=(), required=False, label=_('Competition'))
    show = forms.ChoiceField(choices=(), required=False, label=_('Show'))
    search = forms.CharField(required=False, label=_('Search'))

    sort = forms.CharField(required=False, widget=forms.HiddenInput)

    def append_queryset(self, queryset):
        query_attrs = self.fields


        if query_attrs.get('competition').initial:
            try:
                _id = int(query_attrs.get('competition').initial)
                competition = Competition.objects.get(id=_id)
                ids = competition.get_all_children_ids() + (competition.id, )
                queryset = queryset.filter(competition_id__in=ids)
            except:
                pass


        if query_attrs.get('show').initial:
            queryset = queryset.filter(is_agency_video=query_attrs.get('show').initial)

        if query_attrs.get('search').initial:
            queryset = queryset.filter(title__icontains=query_attrs.get('search').initial)

        if query_attrs.get('sort').initial:
            queryset = queryset.order_by(*query_attrs.get('sort').initial.split(','))

        queryset = queryset.distinct()

        return queryset

    def __init__(self, *args, **kwargs):
        super(VideoSearchForm, self).__init__(*args, **kwargs)


        competitions = Competition.objects.exclude(video=None)
        self.fields['competition'].choices = [('', '------')] + [(obj.id, obj.get_full_name) for obj in competitions]

        self.fields['show'].choices = [('', '------'), (1, _('Show only agency videos')), (0, _('Show only user videos'))]



        self.fields['sort'].initial = self.request.GET.get('sort', '-published_at')

        self.fields['search'].initial = self.request.GET.get('search', '')
        self.fields['competition'].initial = self.request.GET.get('competition', '')
        self.fields['show'].initial = self.request.GET.get('show', '')

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
                Div(
                    'show',
                    css_class='col-sm-2 hidden-xs',
                ),
                Div(
                    'competition',
                    css_class='col-sm-2 hidden-xs',
                ),
                Div(
                    'search',
                    'sort',
                    css_class='col-sm-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span>', css_class="btn-primary search-button-margin", type="submit"),
                        HTML('<a href="%s" class="btn btn-primary search-button-margin"><i class="glyphicon glyphicon-plus"></i></a>' % reverse('gallery:video_add')),
                        css_class="buttons pull-right",
                    ),
                    css_class='col-sm-2',
                ),
        )




class GallerySearchForm(RequestKwargModelFormMixin, forms.Form):
    competition = forms.ChoiceField(choices=(), required=False, label=_('Competition'))
    search = forms.CharField(required=False, label=_('Search'))

    sort = forms.CharField(required=False, widget=forms.HiddenInput)

    def append_queryset(self, queryset):
        query_attrs = self.fields

        if query_attrs.get('competition').initial:
            try:
                _id = int(query_attrs.get('competition').initial)
                competition = Competition.objects.get(id=_id)
                ids = competition.get_all_children_ids() + (competition.id, )
                queryset = queryset.filter(competition_id__in=ids)
            except:
                pass

        if query_attrs.get('search').initial:
            queryset = queryset.filter(Q(title__icontains=query_attrs.get('search').initial) | Q(photographer__icontains=query_attrs.get('search').initial))

        if query_attrs.get('sort').initial:
            queryset = queryset.order_by(*query_attrs.get('sort').initial.split(','))

        queryset = queryset.distinct()

        return queryset

    def __init__(self, *args, **kwargs):
        super(GallerySearchForm, self).__init__(*args, **kwargs)


        competitions = Competition.objects.exclude(album=None)
        self.fields['competition'].choices = [('', '------')] + [(obj.id, obj.get_full_name) for obj in competitions]


        self.fields['sort'].initial = self.request.GET.get('sort', '-id')

        self.fields['search'].initial = self.request.GET.get('search', '')
        self.fields['competition'].initial = self.request.GET.get('competition', '')

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(
                Div(
                    'competition',
                    css_class='col-sm-2 hidden-xs',
                ),
                Div(
                    'search',
                    'sort',
                    css_class='col-sm-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span>', css_class="btn-primary search-button-margin", type="submit"),
                        HTML('<a href="%s" class="btn btn-primary search-button-margin"><i class="glyphicon glyphicon-plus"></i></a>' % reverse('gallery:album_add')),
                        css_class="buttons pull-right",
                    ),
                    css_class='col-sm-2',
                ),
            )
        )


class ChangeAlbumDataUpdateForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = Album
        fields = {'title', 'gallery_date', 'photographer', 'competition', 'gallery_date'}

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        competitions = Competition.objects.filter(competition_date__year=datetime.datetime.now().year)
        self.fields['competition'].choices = ((obj.id, obj.get_full_name) for obj in competitions)

        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.form_method = "POST"
        self.helper.label_class = "control-label col-sm-2"
        self.helper.field_class = "form-control  col-sm-4"
        self.helper.layout = Layout(
            Field(
                "title",
            ),
            Field(
                "photographer",
            ),
            'competition',
            Field(
                "gallery_date",
            ),
            ButtonHolder(
                Submit(
                    'submit',
                    _('Submit'),
                    css_class='btn-sm col-sm-offset-2'
                ),
            )
        )

