# Copyright (c) 2011, Jeffrey Bester
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.


import smtpd
import asyncore
import re

class Matcher:
    """ Regex matcher """

    def __init__( self ):
        self.patterns = []

    def register( self, pattern, callback ):
        """ Register a pattern and callback """
        self.patterns.append((pattern, callback))

    def match( self, text, *args, **kw ):
        longest = -1
        longest_match = None
        longest_callback = None

        for (pattern, callback) in self.patterns:
            match = re.match( pattern, text )
            if match:
                (start,end) = match.span()
                length = end - start

                # match longer matches
                if length > longest:
                    longest = length
                    longest_match = match
                    longest_callback = callback

        # if a match found call it
        if longest_match != None:
            params = longest_match.groups()
            # call callback
            apply( longest_callback, args + params, **kw)

class SMTPDispatcher(smtpd.SMTPServer):
    """A dispatching SMTP host


    """

    def __init__(*args, **kwargs):
        """  See params for smtpd.SMTPServer constructor
        """
        smtpd.SMTPServer.__init__(*args, **kwargs)
        __filter_chain = []
        __matcher = Matcher()

    def filter( self, fn ):
        """ Add a filter

        All filters must return true for it to be dispatched
        """
        __filter_chain.append( fn )
    
    def route( self, regex, callback ):
        """ Setup a route

        regex - regular expression
        callback - callback to call if regex is longest match

        """
        __matcher.register( regex, callback )

    def process_message(self, peer, mailfrom, mailtos, data):
        if all( (fltr( peer, mailfrom, mailtos, data) for fltr in __filter_chain) ):
            for to in mailtos:
                __matcher.match( to, peer, mailfrom, mailtos, data )


