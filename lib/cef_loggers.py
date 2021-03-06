"""Our app specific CEF loggers."""
from django.conf import settings
from django.http import HttpRequest

from cef import log_cef as _log_cef
metlog = settings.METLOG


class CEFLogger:
    """Abstract base CEF logger.

    Class attributes to set in a concrete class:
    **sig_prefix**
        Prefix to the CEF signature. Example: RECEIPT
    **cs2label**
        cs2label parameter. Example: ReceiptTransaction
    **msg_prefix**
        Prefix to all CEF log messages. Example: Receipt
    **default_severity**
        If set, this should be a 0-10 int.
    """
    sig_prefix = ''
    cs2label = None
    msg_prefix = ''
    default_severity = None

    def log(self, environ, app, msg, longer, severity=None,
            extra_kwargs=None):
        """Log something important using the CEF library.

        Parameters:
        **environ**
            Typically a Django request object. It can also be
            a plain dict.
        **app**
            An app/addon object.
        **msg**
            A short message about the incident.
        **longer**
            A more description message about the incident.
        **severity=None**
            A 0-10 int to override the default severity.
        **extra_kwargs**
            A dict to override anything sent to the CEF library.
        """
        c = {'cef.product': getattr(settings, 'CEF_PRODUCT', 'AMO'),
             'cef.vendor': getattr(settings, 'CEF_VENDOR', 'Mozilla'),
             'cef.version': getattr(settings, 'CEF_VERSION', '0'),
             'cef.device_version': getattr(settings,
                                           'CEF_DEVICE_VERSION',
                                           '0'),
             'cef.file': getattr(settings, 'CEF_FILE', 'syslog'), }
        user = getattr(environ, 'amo_user', None)
        kwargs = {'username': getattr(user, 'name', ''),
                  'suid': str(getattr(user, 'pk', '')),
                  'signature': '%s%s' % (self.sig_prefix, msg.upper()),
                  'msg': longer, 'config': c,
                  'cs2': app, 'cs2Label': self.cs2label}
        if extra_kwargs:
            kwargs.update(extra_kwargs)

        if not severity:
            severity = self.default_severity
        if not severity:
            raise ValueError('CEF severity was not defined')

        if isinstance(environ, HttpRequest):
            environ = environ.META.copy()

        if settings.USE_METLOG_FOR_CEF:
            return metlog.cef('%s %s' % (self.msg_prefix, msg), severity,
                            environ, **kwargs)
        else:
            return _log_cef('%s %s' % (self.msg_prefix, msg),
                     severity, environ, **kwargs)


class ReceiptCEFLogger(CEFLogger):
    sig_prefix = 'RECEIPT'
    cs2label = 'ReceiptTransaction'
    msg_prefix = 'Receipt'
    default_severity = 5


receipt_cef = ReceiptCEFLogger()


class InappCEFLogger(CEFLogger):
    sig_prefix = 'INAPP_PAY'
    cs2label = 'InappPayment'
    msg_prefix = 'InappPayment'
    default_severity = 5


inapp_cef = InappCEFLogger()
