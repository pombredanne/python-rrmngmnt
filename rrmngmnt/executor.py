"""
This module was created for easier testing of whole package.
"""
import contextlib
from rrmngmnt.resource import Resource


class Executor(Resource):

    class LoggerAdapter(Resource.LoggerAdapter):
        """
        Makes sure that all logs which are done via this class, has
        appropriate prefix. [user/password]
        """
        def process(self, msg, kwargs):
            return (
                "[%s/%s] %s" % (
                    self.extra['self'].user.name,
                    self.extra['self'].user.password,
                    msg,
                ),
                kwargs,
            )

    class Session(object):
        def __init__(self, executor):
            super(Executor.Session, self).__init__()
            self._executor = executor

        @property
        def logger(self):
            return self._executor.logger

        def __enter__(self):
            self.open()
            return self

        def __exit__(self, type_, value, tb):
            self.close()

        def open(self):
            raise NotImplementedError()

        def close(self):
            pass

        def command(self, cmd):
            return Executor.Command(cmd, self)

        def run_cmd(self, cmd, input_):
            cmd = self.command(cmd)
            return cmd.run(input_)

    class Command(object):
        def __init__(self, cmd, session):
            super(Executor.Command, self).__init__()
            self.cmd = cmd
            self.out = None
            self.err = None
            self._ss = session
            self._rc = None

        @property
        def logger(self):
            return self._ss.logger

        def run(self, input_):
            raise NotImplementedError()

        @contextlib.contextmanager
        def execute(self, bufsize=-1):
            raise NotImplementedError()

        def get_rc(self, wait=False):
            raise NotImplementedError()

        @property
        def rc(self):
            return self.get_rc()
        returncode = rc

    def __init__(self, user):
        """
        :param user: user
        :type user: instance of user
        """
        super(Executor, self).__init__()
        self.user = user

    def session(self):
        return Executor.Session(self)

    def run_cmd(self, cmd, input_=None):
        """
        :param cmd: command
        :type cmd: list
        :param input_: input data
        :type input_: str
        """
        with self.session() as session:
            return session.run_cmd(cmd, input_)
