import inspect
import logging


class VerboseFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        result = super().format(record)
        if record.exc_info:
            extra = self._get_stack_info()
            if extra:
                result = f"{result}\nLocal variables: {extra}"
        return result

    def _get_stack_info(self) -> str | None:
        """Collect local variables from the innermost exception frame."""
        frame = None
        try:
            trace = inspect.trace()
            frame = trace[-1][0] if trace else None
            if frame is None:
                return None
            local_vars = {k: v for k, v in frame.f_locals.items() if not k.startswith("__") and not callable(v)}
            if not local_vars:
                return None
            return ", ".join(f"{k}={v!r}" for k, v in local_vars.items())
        except (AttributeError, TypeError):
            return None
        finally:
            del frame
            del trace
