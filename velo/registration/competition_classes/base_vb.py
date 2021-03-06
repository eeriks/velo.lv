
import datetime
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from sitetree.utils import item
from io import BytesIO
from velo.core.models import Log
from velo.marketing.utils import send_sms_to_participant, send_number_email
from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Number, Participant, PreNumberAssign, Application
from velo.registration.tables import ParticipantTable, ParticipantTableWithLastYearPlace
from velo.results.models import ChipScan, Result, DistanceAdmin, TeamResultStandings
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable
from velo.results.tasks import create_result_sms
from velo.team.models import Team, MemberApplication
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from velo.core.pdf import fill_page_with_image, _baseFontName, _baseFontNameB
from django.conf import settings
from django.db import connection
import os.path
from django.utils.translation import ugettext_lazy as _, activate


class VBCompetitionBase(CompetitionScriptBase):

    def build_manager_menu(self):
        return item(str(self.competition), 'manager:competition %i' % self.competition.id, in_menu=self.competition.is_in_menu, access_loggedin=True)



    def build_menu(self, lang):
        activate(lang)
        current_date = datetime.date.today()
        child_items = [
            item(_("Teams"), 'competition:team %i' % self.competition.id, children=[
                item('{{ object }}', 'competition:team %i object.id' % self.competition.id, in_menu=False),
            ]),
            item(_("Start List"), 'competition:participant_list %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items, lang)
        if self.competition.map_set.count():
            child_items.append(item(_("Maps"), 'competition:maps %i' % self.competition.id))

        if self.competition.competition_date <= current_date + datetime.timedelta(days=1):
            child_items.append(item(_("Results"), 'competition:result_distance_list %i' % self.competition.id))
            child_items.append(item(_("Team Results"), 'competition:result_team_by_name %i' % self.competition.id))
            if self.competition_id == 35:
                child_items.append(item(_("Team Results betw. distances"), 'competition:result_team_by_name_btw_distances %i' % self.competition.id))

        return item(str(self.competition), 'competition:competition %i' % self.competition.id, url_as_pattern=True, children=child_items, in_menu=self.competition.is_in_menu)


    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: [{'start': 1, 'end': 250, 'group': ''}, ],
            self.MTB_DISTANCE_ID: [{'start': 401, 'end': 1200, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 6200, 'group': ''}, ],
            self.RETRO_DISTANCE_ID: [{'start': 9001, 'end': 9450, 'group': ''}, ],
        }


    def passages(self):
        return {
            self.SOSEJAS_DISTANCE_ID: [(1, 1, 250, 0), ],
            self.MTB_DISTANCE_ID: [
                                    (1, 401, 600, 20),
                                    (2, 601, 800, 20),
                                    (3, 801, 1000, 10),
                                    (4, 1001, 1200, 0)
                                    ],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 20),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 20),
                                    (4, 2601, 2800, 15),
                                    (5, 2801, 3000, 15),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3400, 5),
                                    (8, 3401, 3600, 5),
                                    (9, 3601, 3800, 5),
                                    (10, 3801, 4000, 5),
                                    (11, 4001, 4200, 0),
                                    (12, 4201, 4400, 0),
                                    (13, 4401, 4600, 0),
                                    (14, 4601, 4800, 0),
                                    (15, 4801, 5000, 0),
                                    (16, 5001, 5200, 0),
                                    (17, 5201, 5400, 0),
                                    (18, 5401, 5600, 0),
                                    (19, 5601, 5800, 0),
                                    (20, 5801, 6000, 0),
                                    (21, 6001, 6200, 0),
                                    ],
            self.RETRO_DISTANCE_ID: [(1, 9001, 9450, 0), ],
        }


    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultRMDistanceTable

    def get_startlist_table_class(self, distance=None):
        if distance.id in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            are_numbers_assigned = Participant.objects.filter(is_participating=True, distance=distance).exclude(primary_number=None).count()
            if not are_numbers_assigned:
                return ParticipantTableWithLastYearPlace
            else:
                return ParticipantTable
        else:
            return ParticipantTable


    def assign_numbers_continuously(self):

        application_ids = []
        participant_ids = []

        for distance_id in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            last_number = self.competition.number_set.filter(distance_id=distance_id).exclude(participant_slug='').order_by('-number')

            participants = Participant.objects.filter(distance_id=distance_id, is_participating=True, primary_number=None).order_by('registration_dt')

            for participant in participants:
                next_number = Number.objects.filter(distance_id=distance_id, participant_slug='')

                if last_number:
                    next_number = next_number.filter(number__gt=last_number[0].number)

                next_number = next_number[0]

                next_number.participant_slug = participant.slug
                next_number.save()
                participant.primary_number = next_number
                participant.save()

                if participant.application and participant.application_id not in application_ids:
                    application_ids.append(participant.application_id)

                participant_ids.append(participant.id)

        applications = Application.objects.filter(id__in=application_ids)
        for application in applications:
            send_number_email(self.competition, application=application) # SEND EMAIL

        participants = Participant.objects.filter(id__in=participant_ids)
        for participant in participants:
            send_sms_to_participant(participant)  # SEND SMS
            if participant.application:
                if participant.application.participant_set.filter(is_participating=True).count() == 1:
                    continue
                if participant.email == participant.application.email:
                    continue

            if participant.email:
                send_number_email(self.competition, participants=[participant, ]) # SEND EMAIL



    def assign_numbers(self, reassign=False, assign_special=False):
        # TODO: There is not "group_together" made.
        total_count = {}
        if reassign:
            Number.objects.filter(competition=self.competition).update(participant_slug='', number_text='')
            Participant.objects.filter(competition=self.competition, is_participating=True).update(primary_number=None)

        if assign_special:
            # first assign special numbers
            numbers = PreNumberAssign.objects.filter(competition=self.competition).exclude(number=None)
            for pre in numbers:
                number = Number.objects.get(number=pre.number, competition=self.competition)
                print("%s - %s" % (number, pre.participant_slug))
                number.participant_slug = pre.participant_slug
                number.save()

                participant = Participant.objects.filter(slug=number.participant_slug, competition=self.competition, distance=number.distance, is_participating=True)
                if participant:
                    participant = participant[0]
                    participant.primary_number = number
                    participant.save()

            if hasattr(self, "assign_numbers_special_additional"):
                total_count = self.assign_numbers_special_additional()

        for distance_id in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.RETRO_DISTANCE_ID):

            for passage_nr, passage_start, passage_end, passage_extra in self.passages().get(distance_id):
                special_in_passage = PreNumberAssign.objects.filter(competition=self.competition, number__gte=passage_start, number__lte=passage_end).count()
                additional_places_used = total_count.get(passage_nr, 0)

                places = passage_end - passage_start - passage_extra + 1 - special_in_passage - additional_places_used

                final_slugs_in_passage = []
                participants_in_passage = PreNumberAssign.objects.filter(competition=self.competition, segment=passage_nr, distance_id=distance_id)
                for pre in participants_in_passage:
                    if not Participant.objects.filter(competition=self.competition, is_participating=True, distance_id=distance_id, slug=pre.participant_slug).exclude(primary_number=None):
                        final_slugs_in_passage.append(pre.participant_slug)


                participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, primary_number=None).order_by('helperresults__calculated_total', 'registration_dt')[:places]
                participant_slugs = [obj.slug for obj in participants]

                extra_count = 0
                slugs_in_passage = final_slugs_in_passage[:]
                for slug in slugs_in_passage:
                    if slug in participant_slugs:
                        print('FOUND %s' % slug)
                        final_slugs_in_passage.remove(slug)
                    else:
                        print('not in')
                        extra_count += 1


                final_slugs = [obj.slug for obj in participants[:places-extra_count]] + final_slugs_in_passage

                final_numbers = [nr for nr in range(passage_start, passage_end+1) if Number.objects.filter(number=nr, competition=self.competition, participant_slug='')]


                for nr, slug in zip(final_numbers, final_slugs):
                    print('%i - %s' % (nr, slug))
                    number = Number.objects.get(number=nr, competition=self.competition, participant_slug='')
                    number.participant_slug = slug
                    number.save()
                    participant = Participant.objects.filter(slug=slug, competition=self.competition, distance=number.distance, is_participating=True)
                    if participant:
                        participant = participant[0]
                        participant.primary_number = number
                        participant.save()

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
            return ''

    def recalculate_team_results(self):
        raise NotImplementedError
        """
        Function to recalculate all team results for current competition.
        """
        teams = Team.objects.filter(member__memberapplication__competition=self.competition, member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT).order_by('id').distinct('id')
        for team in teams:
            print(team.id)
            self.recalculate_team_result(team=team)

    def recalculate_team_result(self, team_id=None, team=None):
        raise NotImplementedError
        """
        Function to recalculate team's result for current competition.
        After current competition point recalculation, standing total points are recalculated as well.
        """
        if not team and not team_id:
            raise Exception('Team or Team Id must be set')
        if not team:
            team = Team.objects.get(id=team_id)
        else:
            team_id = team.id

        team_member_results = Team.objects.filter(
            id=team_id,
            member__memberapplication__competition=self.competition,
            member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT,
            member__memberapplication__participant__result__competition=self.competition).order_by('-member__memberapplication__participant__result__points_distance').values_list('member__memberapplication__participant__result__points_distance')[:4]
        standing, created = TeamResultStandings.objects.get_or_create(team_id=team_id)

        # Set current competition points to best 4 riders sum
        setattr(standing, 'points%i' % self.competition_index, sum([val[0] for val in team_member_results if val[0]]))

        # Recalculate total sum.
        point_list = [standing.points1, standing.points2, standing.points3, standing.points4, standing.points5, standing.points6, standing.points7]
        if team.distance_id == self.SPORTA_DISTANCE_ID:
            point_list.pop(3)  # 4.stage is not taken because it is UCI category

        point_list = filter(None, point_list)  # remove None from list
        setattr(standing, 'points_total', sum(point_list))

        standing.save()

        # Log information about calculated values
        # Log.objects.create(content_object=team, action="Recalculated team standing", params={
        #     'points_total': standing.points_total,
        #     'points%i' % self.competition_index: getattr(standing, 'points%i' % self.competition_index)
        # })

    def _participant_standings_points(self, standing, distance=False):
        raise NotImplementedError
        """
        This is private function that calculates points for participant based on distance.
        """
        stages = range(1, self.STAGES_COUNT+1)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            stages.remove(4)  # 4.stage is not taken because it is UCI category
        if distance:
            points = sorted((getattr(standing, 'distance_points%i' % stage) for stage in stages), reverse=True)
        else:
            points = sorted((getattr(standing, 'group_points%i' % stage) for stage in stages), reverse=True)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            return sum(points[0:4])
        elif standing.distance_id == self.TAUTAS_DISTANCE_ID:
            return sum(points[0:5])
        elif standing.distance_id == self.BERNU_DISTANCE_ID:
            return sum(points[0:5])

    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)


        zero_minus_10secs = (datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.timedelta(seconds=10)).time()
        if chip.time < zero_minus_10secs:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip scanned before start")
            return False

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        if chip.is_blocked:  # If blocked, then remove result, recalculate standings, recalculate team results
            raise NotImplementedError
            results = Result.objects.filter(competition=chip.competition, number=chip.nr, time=result_time)
            if results:
                result = results[0]
                participant = result.participant
                if result.standings_object:
                    standing = result.standings_object
                    result.delete()
                    self.recalculate_standing(standing)  # Recalculate standings for this participant
                    standing.save()
                    if participant.team:  # If blocked participant was in a team, then recalculate team results.
                        self.recalculate_team_result(team=participant.team)
                Log.objects.create(content_object=chip, action="Chip process", message="Processed blocked chip")
            return None
        elif chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        results = Result.objects.filter(competition=chip.competition, number=chip.nr)
        if results:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip ignored. Already have result")
        else:
            participant = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)

            if participant:
                result = Result.objects.create(competition=chip.competition, participant=participant[0], number=chip.nr, time=result_time, )
                result.set_avg_speed()
                result.save()

                self.assign_standing_places()

                if sendsms and participant[0].is_competing and self.competition.competition_date == datetime.date.today():
                    create_result_sms.apply_async(args=[result.id, ], countdown=120)

                chip.is_processed = True
                chip.save()

            else:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")

        print(chip)

    def recalculate_all_points(self):
        self.assign_result_place()

    def assign_result_place(self):
        """
        Assign result place based on result time. Optimized to use raw SQL.
        """
        cursor = connection.cursor()

        # First assign distance place
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = res2.distance_row_nr,
    result_group = res2.group_row_nr
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing,
row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
WHERE p.is_competing is true and res.time IS NOT NULL
) res2
WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
AND r.id = res2.id
""", [self.competition_id, ])
        # Then unset places to others
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = NULL,
    result_group = NULL
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
) res2
WHERE res2.competition_id = %s and (res2.time IS NULL or res2.is_competing is false)
AND r.id = res2.id
""", [self.competition_id, ])


    def recalculate_standing_for_result(self, result):
        pass  # TODO: recalculate if group is changed.

    def assign_standing_places(self):
        self.assign_result_place()
        self.reset_cache_results()

    def reset_cache(self):
        cache.clear()  # This cleans all cache.
        return True
        # Reset team results.
        self.reset_cache_results()

        super(VBCompetitionBase, self).reset_cache()


    def reset_cache_results(self):
        for lang_key, lang_name in settings.LANGUAGES:
            for distance in self.competition.get_distances():
                cache_key = make_template_fragment_key('results_team_by_teamname', [lang_key, self.competition, distance])
                cache.delete(cache_key)
        for distance in self.competition.get_distances():
            cache.delete('team_results_by_name_%i_%i' % (self.competition.id, distance.id))


    def process_unprocessed_chips(self, send_sms=False, recalc=False):
        for chip in self.competition.chipscan_set.filter(is_processed=False).order_by('time'):
            self.process_chip_result(chip.id, send_sms, recalc)

    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 35)
        c.drawCentredString(c._pagesize[0] / 2, 16.3*cm, result.participant.full_name)
        c.setFont(_baseFontName, 25)
        c.drawCentredString(c._pagesize[0] / 2, 15*cm, "%i.vieta" % result.result_distance)
        c.setFont(_baseFontName, 18)
        c.drawCentredString(c._pagesize[0] / 2, 14*cm, "Laiks: %s" % result.time.replace(microsecond=0))
        c.drawCentredString(c._pagesize[0] / 2, 13*cm, "Vidējais ātrums: %s km/h" % result.avg_speed)

        # if result.zero_time:
        #     zero_time = datetime.datetime.combine(datetime.date.today(), result.zero_time)
        #     delta = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0)) - zero_time
        #     zero_time = (datetime.datetime.combine(datetime.date.today(), result.time) + delta).time().replace(microsecond=0)
        #     c.drawCentredString(c._pagesize[0] / 2, 12*cm, "Čipa laiks: %s" % zero_time)

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def recalculate_all_standings(self):
        # Here are no standings.
        pass
