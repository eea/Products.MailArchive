#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is MailArchive 0.5
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#    Cornel Nitu (Finsiel Romania)
#    Dragos Chirila (Finsiel Romania)
#
#Thanks to Noah Spurrier for his code

import string
import re
from os.path import join

import Globals

BLACKWORDS = 'BLACKWORDS'
SPAM = 0
KEEP = 1
UNSURE = 2


class mbox_filters:
    
    def __init__(self):
        file_path = join(Globals.package_home(globals()) ,BLACKWORDS)
        buf = open(file_path).readlines()
        blackword_list = map(string.strip, buf)
        self.blackword_pattern_list = self.compile_pattern_list([i for i in blackword_list if i != ''])

    def compile_pattern_list (self, string_list):
        """This takes a list of strings and returns a list of compiled regexs
        with the IGNORECASE flag set true.
        """
        pattern_list = []
        for x in string_list:
            pattern_list.append (re.compile(x, re.IGNORECASE))
        return pattern_list

    def in_pattern_list (self, pattern_list, s):
        """This returns a match object if the string matches any regex in the pattern_list
           otherwise it returns None.
        """
        for cre in pattern_list:
            match = cre.search(s)
            if match is not None:
                return match
        return None

    def run_rules(self, subject):
        try:
            match = self.in_pattern_list(self.blackword_pattern_list, subject)
            if match:
               return SPAM, "Subject matches %s in BLACKWORDS list" % (match.re.pattern)
            return UNSURE, "Message yields uncertainty"
        except Exception,e:
            response_message = """The rule processor raised an exception.
                Sometimes this is from a bad regular expression.\n"""
            return KEEP, response_message