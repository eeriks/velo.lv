# coding=utf-8
from __future__ import unicode_literals
from io import StringIO
from difflib import get_close_matches
from velo.marketing.utils import send_sms_to_participant, send_number_email, send_smses, send_sms_to_family_participant
from velo.registration.competition_classes.base import RMCompetitionBase
from velo.registration.models import Number, Participant, ChangedName
from velo.results.models import Result, HelperResults

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from velo.core.pdf import get_image, getSampleStyleSheet, base_table_style, fill_page_with_image, _baseFontName, _baseFontNameB
import os.path
from velo.team.models import Member, Team


class RM2016(RMCompetitionBase):
    SPORTA_DISTANCE_ID = 53
    TAUTAS_DISTANCE_ID = 54
    TAUTAS1_DISTANCE_ID = 55
    GIMENU_DISTANCE_ID = 56

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'W-18', 'M Elite', 'W', 'M-35', 'M-40', 'M-45', 'M-50', 'M-55', ),
            self.TAUTAS_DISTANCE_ID: ('T M-16', 'T W-16', 'T M', 'T W', ),
            self.TAUTAS1_DISTANCE_ID: ('T1 M', 'T1 W',)
        }

    def _update_year(self, year):
        return year + 2

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M Elite'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'M-35'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'M-40'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'M-45'
                elif self._update_year(1964) >= year >= self._update_year(1960):
                    return 'M-50'
                elif year <= self._update_year(1959):
                    return 'M-55'
            else:
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'W-18'
                elif year <= self._update_year(1995):
                    return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T M-16'
                elif year <= self._update_year(1997):
                    return 'T M'
            else:
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T W-16'
                elif year <= self._update_year(1997):
                    return 'T W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T1 M'
            else:
                return 'T1 W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        output = StringIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("media/competition/vestule/RVm_2015_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5*cm, 20*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(5*cm, 18*cm, str(participant.distance))


        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 18.5*cm, str(participant.primary_number))
        elif participant.distance_id == self.GIMENU_DISTANCE_ID:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15*cm, 18.5*cm, "Amway")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15*cm, 18.5*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output


    def generate_diploma(self, result):
        output = StringIO()
        path = 'results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            return Exception

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 35)
        c.drawCentredString(c._pagesize[0] / 2, 16.3*cm, result.participant.full_name)

        if result.participant.distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            c.setFont(_baseFontName, 25)
            c.drawCentredString(c._pagesize[0] / 2, 15*cm, "%i.vieta" % result.result_distance)
            c.setFont(_baseFontName, 18)
            c.drawCentredString(c._pagesize[0] / 2, 14*cm, "Laiks: %s" % result.time.replace(microsecond=0))
            c.drawCentredString(c._pagesize[0] / 2, 13*cm, "Vidējais ātrums: %s km/h" % result.avg_speed)

        c.showPage()
        c.save()
        output.seek(0)
        return output


    def create_helper_results(self, participants):
        prev_competition = self.competition.get_previous_sibling()

        prev_slugs_sport = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='S').select_related('participant')]
        prev_slugs_tauta = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='T').select_related('participant')]

        for participant in participants:
            results = Result.objects.filter(competition=prev_competition, participant__slug=participant.slug, participant__distance__kind=participant.distance.kind).order_by('time')

            if not results:
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    results = Result.objects.filter(competition=prev_competition, participant__slug=changed.slug, participant__distance__kind=participant.distance.kind).order_by('time')
                except:
                    pass


            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

            if participant.distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            if results:
                result = results[0]
                helper.calculated_total = result.result_distance
                helper.result_used = result
            else:
                helper.calculated_total = None
                matches = get_close_matches(participant.slug, prev_slugs_sport if participant.distance_id == self.SPORTA_DISTANCE_ID else prev_slugs_tauta, 1, 0.8)
                if matches:
                    helper.matches_slug = matches[0]

            helper.save()

    def pre_competition_run(self):
        t = Team.objects.filter(distance__competition=self.competition)
        members = Member.objects.filter(team__in=t)
        for member in members:
            try:
                p = Participant.objects.get(slug=member.slug, is_participating=True, distance=member.team.distance)
                if p.team_name != member.team.title:
                    print("%i %s %s %s" % (p.id, p.slug, p.team_name, member.team.title))
                    p.team_name = member.team.title
                    p.save()
            except:
                print('Not %s' % member.slug)