#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.4

import datetime
from uuid import uuid1
import pytz
from icalendar import Calendar, Event

import sys
sys.path.append('..')

import config
from spider import bycourse

__all__ = ['gen_ics_file']

CLASS_PERIOD_BEGIN_TIME = [(0, 0), (8, 0), (8, 50), \
                           (9, 50), (10, 40), (11, 30), \
                           (14, 00), (14, 50), (15, 50), \
                           (16, 40), (17, 30), (19, 0), \
                           (19, 50), (20, 40), (21, 30)]

def gen_ics_file(courses, classbreak, filename):
    ''' generate iCalendar file '''
    cal = Calendar()
    cal.add('prodid', '-//barriery Inc//BUAA Class Schedule//CN')
    cal.add('version', '2.0')
    for course in courses:
        events = get_events_by_course(course, classbreak)
        for event in events:
            cal.add_component(event)
    with open(filename, 'wb') as file:
        file.write(cal.to_ical())

def get_events_by_course(course, classbreak):
    ''' get events by course '''
    if not course['weekday']:
        # 某些课程（例如英语免修）没有上课周次
        return []

    # zero week is 2019/8/26 00:00:00
    begin_date = datetime.datetime(2019, 8, 26, 0, 0, 0, tzinfo=pytz.timezone("Asia/Shanghai"))
    current_day = begin_date + datetime.timedelta(days = 7 * int(course['week_begin']) \
                                                       + int(course['weekday']) - 1)
    events = []
    if classbreak:
        for class_period in range(int(course['class_begin']), int(course['class_end'])+1):
            hour, minute = CLASS_PERIOD_BEGIN_TIME[class_period]
            current_date = current_day \
                         + datetime.timedelta(hours=hour) \
                         + datetime.timedelta(minutes=minute)
            event = Event()
            event.add('uid', str(uuid1()) + '@barriery')
            event.add('summary', course['name'])
            event.add('dtstart', current_date)
            event.add('dtend', current_date + datetime.timedelta(minutes=45))
            event.add('dtstamp', datetime.datetime.now())
            event.add('location', course['place'])
            event.add('description', 'teacher(%s), credit(%s), id(%s)' \
                    % (course['teacher'], course['credit'], course['course_id']))
            event.add('rrule', {
                'freq': 'weekly',
                'interval': 1,
                'count': int(course['week_end']) - int(course['week_begin']) + 1})
            events.append(event)
    else:
        hour, minute = CLASS_PERIOD_BEGIN_TIME[int(course['class_begin'])]
        current_begin_date = current_day \
                + datetime.timedelta(hours=hour) \
                + datetime.timedelta(minutes=minute)
        hour, minute = CLASS_PERIOD_BEGIN_TIME[int(course['class_end'])]
        current_end_date = current_day \
                + datetime.timedelta(hours=hour) \
                + datetime.timedelta(minutes=minute+45)
        event = Event()
        event.add('uid', str(uuid1()) + '@barriery')
        event.add('summary', course['name'])
        event.add('dtstart', current_begin_date)
        event.add('dtend', current_end_date)
        event.add('dtstamp', datetime.datetime.now())
        event.add('location', course['place'])
        event.add('description', 'teacher(%s), credit(%s), id(%s)' \
                % (course['teacher'], course['credit'], course['course_id']))
        event.add('rrule', {
            'freq': 'weekly',
            'interval': 1,
            'count': int(course['week_end']) - int(course['week_begin']) + 1})
        events.append(event)

    return events

if __name__ == '__main__':
    #  COURSE_LIST = bycourse.query_course_by_xh_in_pre_selection_stage(xh=config.XH,
                                                                     #  username=config.USERNAME,
                                                                     #  password=config.PASSWORD,
                                                                     #  debug=False)
    COURSE_LIST = bycourse.query_course_by_xh_in_adjustment_stage(xh=config.XH,
                                                                  username=config.USERNAME,
                                                                  password=config.PASSWORD,
                                                                  debug=False)
    if COURSE_LIST:
        gen_ics_file(courses=COURSE_LIST,
                     classbreak=config.CLASSBREAK,
                     filename='class_schedule.ics')
        bycourse.check_request_credit(student_type=config.STUDENT_TYPE,
                                    total_request_credit_dict=config.REQUEST_CREDIT,
                                    course_list=COURSE_LIST)
