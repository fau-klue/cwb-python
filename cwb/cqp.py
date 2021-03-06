#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Version 2.0 of "PyCQP" by Joerg Asmussen, DSL (Febr. 2008)
# Some changes by Philipp Heinrich (2021)

"""
Wrapper for CQP.
"""

import sys
import os
import re
import random
import time
import select
import subprocess
import tempfile
import threading


# GLOBAL CONSTANTS OF MODULE:
PROGRESS_CONTROL_CYCLE = 5  # secs between each progress control cycle
MAX_REQUEST_PROC_TIME = 60  # max secs for processing a user request


class ErrCQP:
    """
    Error message class for CQP
    """
    def __init__(self, msg):
        self.msg = msg.rstrip()


class ErrKilled:
    """
    Error message class for Process
    """
    def __init__(self, msg):
        self.msg = msg.rstrip()


class CQP:
    """
    Wrapper for CQP.
    """

    def _progressController(self):
        """
        CREATED: 2008-02
        This method is run as a thread.
        At certain intervals (PROGRESS_CONTROL_CYCLE), it controls how long the
        CQP process of the current user has spent on processing this user's
        latest CQP command. If this time exceeds a certain maximun
        (MAX_REQUEST_PROC_TIME), this method kills the CQP process.
        """
        self.runController = True
        while self.runController:
            time.sleep(PROGRESS_CONTROL_CYCLE)
            if self.execStart is not None:
                if time.time() - self.execStart > \
                        MAX_REQUEST_PROC_TIME * self.maxProcCycles:
                    print(
                        '''WARNING!: PROGRESS CONTROLLER IDENTIFIED BLOCKING CQP PROCESS ID {}'''.format(self.CQP_process.pid),
                        file=sys.stderr
                    )
                    # os.kill(self.CQP_process.pid, SIGKILL) - doesn't work!
                    os.popen("kill -9 " + str(self.CQP_process.pid))  # works!
                    print("=> KILLED!")
                    self.CQPrunning = False
                    break

    def __init__(self, binary='/usr/local/bin/cqp', options='-c', print_version=False):
        """Class constructor."""

        self.CQPrunning = False
        self.runController = None
        self.execStart = time.time()
        self.maxProcCycles = 1.0

        # start CQP as a child process of this wrapper
        if binary is None:
            raise RuntimeError('Path to CQP binaries undefined')
        self.CQP_process = subprocess.Popen(binary + ' ' + options,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            universal_newlines=True,
                                            close_fds=True)
        self.CQPrunning = True

        # init progress controller
        progressthread = threading.Thread(target=self._progressController, args=())
        progressthread.setDaemon(True)
        progressthread.start()

        # "cqp -c" should print version on startup:
        version_string = self.CQP_process.stdout.readline()
        version_string = version_string.rstrip()  # Equivalent to Perl's chomp
        self.CQP_process.stdout.flush()
        if print_version:
            print(version_string)
        version_regexp = re.compile(
            r'^CQP\s+(?:\w+\s+)*([0-9]+)\.([0-9]+)(?:\.b?([0-9]+))?(?:\s+(.*))?$'
        )
        match = version_regexp.match(version_string)
        if not match:
            print("CQP backend startup failed", file=sys.stderr)
            sys.exit(1)
        self.major_version = int(match.group(1))
        self.minor_version = int(match.group(2))
        self.beta_version = int(match.group(3))
        self.compile_date = match.group(4)

        # We need cqp-2.2.b41 or newer (for query lock):
        if not (self.major_version >= 3 or (self.major_version == 2 and self.minor_version == 2 and self.beta_version >= 41)):
            raise RuntimeError('CQP {} version is too old'.format(version_string))

        # Error handling:
        self.error_handler = None
        self.status = 'ok'
        self.error_message = ''  # we store compound error messages as a STRING
        self.errpipe = self.CQP_process.stderr.fileno()

        # Debugging (prints more or less everything on stdout)
        self.debug = False

        # CQP defaults:
        self.Exec('set PrettyPrint off')
        self.execStart = None

    def Terminate(self):
        """
        Terminate controller thread, must be called before deleting CQP
        """
        self.execStart = None
        self.runController = False

    def SetProcCycles(self, procCycles):
        """
        Set process cycles
        """
        print("Setting procCycles to {}".format(procCycles))
        self.maxProcCycles = procCycles
        return int(self.maxProcCycles * MAX_REQUEST_PROC_TIME)

    def __del__(self):
        if self.CQPrunning:
            # print "Deleting CQP with pid", self.CQP_process.pid, "...",
            self.CQPrunning = False
            self.execStart = time.time()
            if self.debug:
                print("Shutting down CQP backend ...", end='')
            self.CQP_process.stdin.write('exit;')  # exits CQP backend
            if self.debug:
                print("Done\nCQP object deleted.")
            self.execStart = None
            # print "Finished"

    def Exec(self, cmd):
        """
        Executes CQP command.
        The method takes as input a command string and sends it
        to the CQP child process
        """
        self.execStart = time.time()
        self.status = 'ok'
        cmd = cmd.rstrip()  # Equivalent to Perl's 'chomp'
        cmd = re.sub(r';\s*$', r'', cmd)
        if self.debug:
            print("CQP <<", cmd + ";")
        try:
            self.CQP_process.stdin.write(cmd + '; .EOL.;\n')
        except IOError:
            return None
        # In CQP.pm lines are appended to a list @result.
        # This implementation prefers a string structure instead
        # because output from this module is meant to be transferred
        # accross a server connection. To enable the development of
        # client modules written in any language, the server only emits
        # strings which then are to be structured by the client module.
        # The server does not emit pickled data according to some
        # language dependent protocol.
        self.CQP_process.stdin.flush()
        result = ''
        while self.CQPrunning:
            ln = self.CQP_process.stdout.readline()
            ln = ln.strip()  # strip off whitespace from start and end of line
            if re.match(r'-::-EOL-::-', ln):
                if self.debug:
                    print("CQP "+"-" * 60)
                break
            if self.debug:
                print("CQP >> "+ln)
            if ln != '':
                result = result + ln + '\n'
        self.Checkerr()
        self.execStart = None
        result = '\n'.join(result)
        result = result.rstrip()  # strip off whitespace from EOL (\n)
        return result

    def Query(self, query):
        """
        Executes query in safe mode (query lock)
        """
        result = []
        key = str(random.randint(1, 1000000))
        errormsg = ''  # collect CQP error messages AS STRING
        ok = True	  # check if any error occurs
        self.Exec('set QueryLock ' + key)  # enter query lock mode
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            ok = False
        result = self.Exec(query)
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            ok = ok and False
        self.Exec('unlock ' + key)  # unlock with random key
        if self.status != 'ok':
            errormsg = errormsg + self.error_message
            ok = ok and False
        # Set error status & error message:
        if ok:
            self.status = 'ok'
        else:
            self.status = 'error'
            self.error_message = errormsg
        return result

    def Dump(self, subcorpus='Last', first=None, last=None):
        """
        Dumps named query result into table of corpus positions
        """
        first = ''
        last = ''

        if first is not None and last is None:
            last = first
        elif last is not None and first is None:
            first = last
        if first is not None:
            first = str(first)
            last = str(last)
            regexp = re.compile(r'^[0-9]+$')
            if (not regexp.match(first)) or (not regexp.match(last)):
                print(
                    "ERROR: Invalid value for first ({}) or last ({}) line in Dump() method".format(first, last),
                    file=sys.stderr
                )
                sys.exit(1)

        matches = []
        result = re.split(r'\n', self.Exec('dump ' + subcorpus +
                                           " " + first + " " + last))
        for line in result:
            matches.append(re.split(r'\t', line))
        return matches

    def Undump(self, subcorpus='Last', table=None):
        """
        Undumps named query result from table of corpus positions
        """
        if not table:
            table = []

        wth = ''               # undump with target and keyword
        n_el = None            # number of anchors for each match
        # (will be determined from first row)
        n_matches = len(table)  # number of matches (= remaining arguments)
        # We have to read undump table from temporary file:
        tf = tempfile.NamedTemporaryFile(prefix='pycqp_undump_')
        filename = tf.name
        tf.write(str(n_matches) + '\n')
        for row in table:
            row_el = len(row)
            if n_el is None:
                n_el = row_el
                if (n_el < 2) or (n_el > 4):
                    print(
                        "ERROR: Row arrays in undump table must have " +
                        "between 2 and 4 elements (first row has " +
                        str(n_el) + " elements)",
                        file=sys.stderr
                    )
                    sys.exit(1)
                if n_el >= 3:
                    wth = 'with target'
                if n_el == 4:
                    wth = wth + ' keyword'
            elif row_el != n_el:
                print(
                    "ERROR: All rows in undump table must have the same " + "length (first row = " + str(n_el) + ", this row = " + str(row_el) + ")",
                    file=sys.stderr
                )
                sys.exit(1)
            tf.write('\t'.join(row) + '\n')
        tf.close()
        # Send undump command with filename of temporary file:
        self.Exec("undump " + subcorpus + " " + wth + " < '" + filename + "'")
        tf.delete()

    def Group(self, subcorpus='Last',
              spec1='match.word', spec2='', cutoff='1'):
        """
        Computes frequency distribution over attribute values
        (single values or pairs) using group command;
        note that the arguments are specified in the logical order,
        in contrast to "group"
        """
        spec2_regexp = re.compile(r'^[0-9]+$')
        if spec2_regexp.match(spec2):
            cutoff = spec2
            spec2 = ''
        spec_regexp = re.compile(
            r'^(match|matchend|target[0-9]?|keyword)\.([A-Za-z0-9_-]+)$')
        match = spec_regexp.match(spec1)
        if not match:
            print(
                "ERROR: Invalid key '" + spec1 + "' in Group() method",
                file=sys.stderr)
            sys.exit(1)
        spec1 = match.group(1) + ' ' + match.group(2)
        if spec2 != '':
            match = spec_regexp(spec2)
            if not match:
                print(
                    "ERROR: Invalid key '" + spec2 + "' in Group() method",
                    file=sys.stderr)
                sys.exit(1)
            spec2 = match.group(1) + ' ' + match.group(2)
            cmd = 'group ' + subcorpus + ' ' + spec2 + ' by ' + spec1 + \
                ' cut ' + cutoff
        else:
            cmd = 'group ' + subcorpus + ' ' + spec1 + ' cut ' + cutoff
        result = self.Exec(cmd)
        rows = []
        for line in result:
            rows.append(re.split(r'\t', line))
        return rows

    def Count(self, subcorpus='Last', sort_clause=None, cutoff=1):
        """
        Computes frequency distribution for match strings,
        based on sort clause
        """
        if sort_clause is None:
            print(
                "ERROR: Parameter 'sort_clause' undefined in Count() method",
                file=sys.stderr)
            sys.exit(1)
        return self.Exec('count ' + subcorpus + ' ' + sort_clause +
                         ' cut ' + str(cutoff))
    # We don't want to return a data structure other than a string in order to
    # send it across a server line without pickling.
    # The work of structuring the data must be done by the client part
    # rows = []
    # for line in result:
    #   size, first, string = re.split(r'\t', line)
    #   rows.append([size, string, first, int(first) + int(size) - 1])
    # return rows

    def Checkerr(self):
        """
        Checks CQP's stderr stream for error messages
        (returns true if there was an error)
        OBS! In CQP.pm the error_message is stored in a list,
        In PyCQP_interface.pm we use a string (which better can be sent
        accross the server line)
        """
        ready = select.select([self.errpipe], [], [], 0)
        if self.errpipe in ready[0]:
            # We've got something on stderr -> an error must have occurred:
            self.status = 'error'
            self.error_message = self.Readerr()
        return not self.Ok()

    def Readerr(self):
        """
        Reads all available lines from CQP's stderr stream
        """
        return os.read(self.errpipe, 16384)

    def Status(self):
        """
        Reads the CQP object's (error) status
        """
        return self.status

    def Ok(self):
        """
        Simplified interface for checking for CQP errors
        """
        if self.CQPrunning:
            return self.Status() == 'ok'

        return False

    def Error_message(self):
        """
        Returns the CQP error message
        """
        if self.CQPrunning:
            return ErrCQP(self.error_message)

        msgKilled = '**** CQP KILLED ***\n' + \
                    'CQP COULD NOT PROCESS YOUR REQUEST\n'

        return ErrKilled(msgKilled + self.error_message)

    def Error(self, msg):
        """
        Processes/outputs error messages
        (optionally run through user-defined error handler)
        """
        if self.error_handler is not None:
            self.error_handler(msg)
        else:
            print(msg, file=sys.stderr)

    def Set_error_handler(self, handler=None):
        """
        Sets user-defined error handler
        """
        self.error_handler = handler

    def Debug(self, on=False):
        """
        Switches debugging output on/off
        """
        prev = self.debug
        self.debug = on
        return prev
