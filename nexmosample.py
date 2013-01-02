#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, random, string

from nexmomessage import NexmoMessage

def main(function, args):

    r = "json"
    u = "XXXXXXXX"
    p = "XXXXXXXX"
    f = "4444444444"
    m = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))

    msg = {'reqtype': r, 'password': p, 'from': f, 'to': t, 'username': u}
    req = {'password': p, 'username': u}

    if (function == "balance"):
        # account balance
        req['type'] = 'balance'
        print("request details: %s") % NexmoMessage(req).get_details()
        print NexmoMessage(req).send_request()
    elif (function == "numbers"):
        # my numbers
        req['type'] = 'numbers'
        print("request details: %s") % NexmoMessage(req).get_details()
        print NexmoMessage(req).send_request()
    elif (function == "pricing"):
        # pricing for country 'NL'
        req['type'] = 'pricing'
        req['country'] = args[0]
        print("request details: %s") % NexmoMessage(req).get_details()
        print NexmoMessage(req).send_request()
    elif (function == "search"):
        # searching for numbers for country 'NL'
        req['type'] = 'search'
        req['country'] = args[0]
        print("request details: %s") % NexmoMessage(req).get_details()
        print NexmoMessage(req).send_request()
    elif (function == "buy"):
        # buying number for country
        req['type'] = 'buy'
        req['country'] = args[0]
        req['msisdn'] = args[1]
        print("request details: %s") % NexmoMessage(req).get_details()
        print NexmoMessage(req).send_request()
    elif (function == "message"):
        # text message
        msg['text'] = m
        sms1 = NexmoMessage(msg)
        print("SMS details: %s") % sms1.get_details()
        m += " ktnxbye"
        sms1.set_text_info(m)
        print("SMS details: %s") % sms1.get_details()
        print sms1.send_request()
    elif (function == "binary"):
        # bin message
        sms2 = NexmoMessage(msg)
        sms2.set_bin_info(bb, bu)
        print("SMS details: %s") % sms2.get_details()
        print sms2.send_request()
    elif (function == "wap"):
        # wap message
        msg['title'] = "this is a test"
        msg['url'] = "http://twitter.com/tmarcuz"
        msg['text'] = False
        sms3 = NexmoMessage(msg)
        print("SMS details: %s") % sms3.get_details()
        print sms3.send_request()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "provide function"
        exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
