# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
import requests
import unicodedata
import urllib
import uuid
from velo.core.models import Competition
from velo.marketing.models import SMS, MailgunEmail
from velo.registration.models import Participant, Application
from premailer import transform
import logging

logger = logging.getLogger('marketing')


# TODO: Rebuild this all

def send_number_email(competition, participants=None, application=None):
    if application:
        email = application.email
        participants = application.participant_set.filter(is_participating=True)
    else:
        email = participants[0].email

    if not participants:
        return False
    if not email:
        return False

    context = {
        'participants': participants,
        'domain': settings.MY_DEFAULT_DOMAIN,
        'competition': competition,
        'application': True,
    }
    template = transform(render_to_string('registration/email/%s/number_email.html' % competition.skin, context))
    template_txt = render_to_string('registration/email/%s/number_email.txt' % competition.skin, context)

    if len(participants) == 1:
        subject = u'Reģistrācijas apliecinājums - %s - %s' % (competition.get_full_name, participants[0].full_name)
    else:
        subject = u'Reģistrācijas apliecinājums - %s' % competition.get_full_name

    email_data = {
        'em_to': email,
        'subject': subject,
        'html': template,
        'text': template_txt,
        'content_object': application or participants[0],
    }
    MailgunEmail.objects.create(**email_data)

    return True

def send_sms_to_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print('Not sending to %s' % number)
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print('TOO SHORT NUMBER')
        return False

    print('Sending to %s' % number)

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')

    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=u"{0}, Jusu starta numurs ir {1} Vienibas brauciena. Iznemiet to EXPO centra 04.-05.09 ELKOR PLAZA Brivibas 201 uzradot so SMS".format(full_name, unicode(participant.primary_number)))

    Participant.objects.filter(id=participant.id).update(is_sent_number_sms=True)

    return True

def send_sms_to_family_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print('Not sending to %s' % number)
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print('TOO SHORT NUMBER')
        return False

    print('Sending to %s' % number)

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')
    sms_txt = u"Sveiki, {0}! Jums ir pieskirts starta numurs AMWAY Gimenes brauciena. Iznemiet to EXPO centra 29.-30.05 ELKOR PLAZA Brivibas 201 uzradot so SMS".format(full_name)[:160]
    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=sms_txt)

    Participant.objects.filter(id=participant.id).update(is_sent_number_sms=True)



def initial_send_numbers_to_all_participants():
    # TODO: Filter. If participant is only one in application, then send only one email.
    competition = Competition.objects.get(id=48)
    applications = Application.objects.filter(competition_id=48).filter(participant__is_participating=True).order_by('id')
    applications = applications.distinct()

    for application in applications:
            send_number_email(competition, application=application)

    participants = Participant.objects.filter(competition_id=48, is_participating=True, is_sent_number_email=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        if participant.application:
            if participant.application.participant_set.filter(is_participating=True).count() == 1:
                continue
            if participant.email == participant.application.email:
                continue

        if participant.email:
            send_number_email(competition, [participant, ])


def send_numbers_to_all_participants_sms():
    participants = Participant.objects.filter(competition_id=48, is_participating=True, is_sent_number_sms=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        send_sms_to_participant(participant)

    # participants = Participant.objects.filter(competition_id=34, is_participating=True, is_sent_number_sms=False, distance_id=30).order_by('created')
    # for participant in participants:
    #     send_sms_to_family_participant(participant)


def send_test():
    sms_obj = {
        'page': 'message/send',
        'username': settings.SMS_USERNAME,
        'password': settings.SMS_PASSWORD,
        'destinationAddress': '37126461101',
        'text': str(uuid.uuid4()),
    }
    resp = requests.get('%s/?%s' % (settings.SMS_GATEWAY, urllib.urlencode(sms_obj)))

def send_smses():
    smses = SMS.objects.filter(is_processed=False)[:100]
    for sms in smses:
        # text = unicodedata.normalize('NFKD', sms.text).encode('ascii', 'ignore').decode('ascii')
        # print(text)
        sms_obj = {
            'page': 'message/send',
            'username': settings.SMS_USERNAME,
            'password': settings.SMS_PASSWORD,
            'destinationAddress': sms.phone_number,
            'text': sms.text,
        }
        if settings.DEBUG:
            logger.info('Sent SMS %s to %s' % (sms.text, sms.phone_number))
        else:
            resp = requests.get('%s/?%s' % (settings.SMS_GATEWAY, urllib.urlencode(sms_obj)))
            sms.response = resp.content
        sms.is_processed = True
        sms.save()