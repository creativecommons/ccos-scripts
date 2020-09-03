import inspect
import logging


class IndentFormatter(logging.Formatter):
    """
    Format the given log messages with proper indentation based on the stack
    depth of the code invoking the logger. This removes the need for manual
    indentation using ``'\t'`` characters.
    """

    @staticmethod
    def identify_cut(filenames):
        """
        Identify the depth at which the invoking function can be located. The
        invoking function would be the first occurrence of a file just after
        all stack filenames from within Python libs itself.
        @param filenames: the names of all files from which logs were pushed
        @return: the index of the filename from which the logger was called
        """

        lib_string = 'lib/python'
        lib_started = False
        for index, filename in enumerate(filenames):
            if not lib_started and lib_string in filename:
                lib_started = True
            if lib_started and lib_string not in filename:
                return index

    def __init__(self):
        """
        Initialise the formatter with the fixed log format. The format is
        intentionally minimal to get clean and readable logs.
        """

        fmt = "%(asctime)s │ %(levelname)-8s │ %(indent)s%(function)s: %(message)s"
        logging.Formatter.__init__(self, fmt=fmt)

        self.baseline = None
        self.cut = None
        self.manual_push = 0

    def format(self, record):
        """
        Format the log message with additional data extracted from the stack.
        @param record: the log record to format with this formatter
        @return: the formatted log record
        """

        stack = inspect.stack(context=0)
        depth = len(stack)
        if self.baseline is None:
            self.baseline = depth
        if self.cut is None:
            filenames = map(lambda x: x.filename, stack)
            self.cut = IndentFormatter.identify_cut(filenames)

        # Inject custom information into the record
        record.indent = '    ' * (depth - self.baseline + self.manual_push)
        record.function = stack[self.cut].function
        # Format the record using custom information
        out = logging.Formatter.format(self, record)
        # Remove custom information from the record
        del record.indent
        del record.function

        return out

    def delta_indent(self, delta=1):
        """
        Change the manual push value by the given number of steps. Increasing
        the value indents the logs and decreasing it de-indents them.
        @param delta: the number of steps by which to indent/de-indent the logs
        @return:
        """

        self.manual_push += delta
        if self.manual_push < 0:
            self.manual_push = 0

    def reset(self):
        """
        Reset the baseline and cut attributes so that the next call to the
        logger can repopulate them to the new values for the particular file.
        """

        self.baseline = None
        self.cut = None
        self.manual_push = 0


def set_up_logging():
    """
    Configure logging with some first-run configuration. This method must be
    called only once from the main process.
    """

    formatter = IndentFormatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=(handler,))


def reset_handler():
    """
    Reset the formatter on the handler on the root logger. This causes the next
    call to the logger can repopulate them based on the new stack in a new file.
    """

    formatter = logging.root.handlers[-1].formatter
    if isinstance(formatter, IndentFormatter):
        formatter.reset()


def change_indent(delta=1):
    """
    Indent the output of the logger by the given number of steps. If positive,
    the indentation increases and if negative, it decreases.
    @param delta: the number of steps by which to indent/de-indent the logs
    """

    formatter = logging.root.handlers[-1].formatter
    if isinstance(formatter, IndentFormatter):
        formatter.delta_indent(delta)
