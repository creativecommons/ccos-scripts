# Standard library
import inspect
import logging

SUCCESS = logging.INFO + 1


class IndentFormatter(logging.Formatter):
    """
    Format the given log messages with proper indentation based on the stack
    depth of the code invoking the logger. This removes the need for manual
    indentation using tab characters.
    """

    # https://en.wikipedia.org/wiki/ANSI_escape_code
    color_map = {  # ............. Level     ##    Color    ##
        logging.CRITICAL: 31,  # . CRITICAL  50    red      31
        logging.ERROR: 31,  # .... ERROR     40    red      31
        logging.WARNING: 33,  # .. WARNING   30    yellow   33
        SUCCESS: 32,  # .......... SUCCESS   21    green    32
        logging.INFO: 34,  # ..... INFO      20    blue     34
        logging.DEBUG: 35,  # .... DEBUG     10    magenta  35
    }

    @staticmethod
    def identify_cut(filenames):
        """
        Identify the depth at which the invoking function can be located. The
        invoking function would be the first occurrence of a file just after
        all stack filenames from within Python libs itself.
        @param filenames: the names of all files from which logs were pushed
        @return: the index of the filename from which the logger was called
        """
        lib_string = "lib/python"
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
        fmt = "%(message)s"
        super().__init__(fmt=fmt)

        self.baseline = None
        self.cut = None
        self.manual_push = 0

    def update_format(self, record):
        """
        Update the format string based on the log level of the record.
        @param record: the record based on whose level to update the formatting
        """
        prefix = "\u001b["
        color = f"{prefix}{self.color_map[record.levelno]}m"
        bold = f"{prefix}1m"
        gray = f"{prefix}1m{prefix}30m"
        reset = f"{prefix}0m"
        self._style._fmt = (
            f"%(asctime)s"
            f" {gray}│{reset} {color}%(levelname)-8s{reset} {gray}│{reset} "
        )
        if hasattr(record, "function"):
            self._style._fmt += (
                f"{gray}%(indent)s{reset}"
                f"{bold}%(function)s{reset}{gray}:{reset}"
                " %(message)s"
            )
        else:
            self._style._fmt += "%(indent)s%(message)s"

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
            self.cut = self.identify_cut(filenames)

        # Inject custom information into the record
        record.indent = "." * (depth - self.baseline + self.manual_push)
        if depth > self.cut:
            record.function = stack[self.cut].function

        # Format the record using custom information
        self.update_format(record)
        out = super().format(record)

        # Remove custom information from the record
        del record.indent
        if hasattr(record, "function"):
            del record.function

        return out

    def delta_indent(self, delta=1):
        """
        Change the manual push value by the given number of steps. Increasing
        the value indents the logs and decreasing it de-indents them.
        @param delta: the number of steps by which to indent/de-indent the logs
        """
        self.manual_push += delta

    def reset(self):
        """
        Reset the baseline and cut attributes so that the next call to the
        logger can repopulate them to the new values for the particular file.
        """
        self.baseline = None
        self.cut = None
        self.manual_push = 0


def setup_logger():
    """
    Configure RootLogger. This method must be called only once from the main
    script (not from modules/libraries included by that script).
    """

    def log_success_class(self, message, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            # The 'args' below (instead of '*args') is correct
            self._log(SUCCESS, message, args, **kwargs)

    def log_success_root(message, *args, **kwargs):
        logging.log(SUCCESS, message, *args, **kwargs)

    def change_indent_class(self, delta=1):
        """
        Indent the output of the logger by the given number of steps. If
        positive, the indentation increases and if negative, it decreases.
        @param delta: the number of steps by which to indent/de-indent the logs
        """
        handlers = self.handlers
        if len(handlers) > 0:
            formatter = handlers[-1].formatter
            if isinstance(formatter, IndentFormatter):
                formatter.delta_indent(delta)

    logging.addLevelName(SUCCESS, "SUCCESS")
    setattr(logging.getLoggerClass(), "success", log_success_class)
    setattr(logging, "success", log_success_root)
    setattr(logging.getLoggerClass(), "change_indent", change_indent_class)

    formatter = IndentFormatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.root
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


__all__ = ["setup_logger"]
