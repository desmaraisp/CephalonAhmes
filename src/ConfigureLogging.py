import logging, json
from typing import Optional


class FormatterJSON(logging.Formatter):
    AWS_Request_ID: Optional[str]
    
    def __init__(self, time_format: str = "%Y-%m-%dT%H:%M:%S", msec_format: str = "%s.%03dZ", AWS_Request_ID: Optional[str] = None):
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None
        self.AWS_Request_ID = AWS_Request_ID

    
    def format(self, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, self.datefmt)
        j = {
            'Level': record.levelname,
            'Timestamp': '%(asctime)s.%(msecs)dZ' % dict(asctime=record.asctime, msecs=record.msecs),
            'Message': record.getMessage(),
            'Module': record.module
        }
        if self.AWS_Request_ID:
            j['AWS Request ID'] = self.AWS_Request_ID
        
        if record.__dict__.get('data'):
            j['Extra Data'] = record.__dict__['data']
        
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            j["Exc Info"] = record.exc_text

        if record.stack_info:
            j["Stacktrace"] = self.formatStack(record.stack_info)

        return json.dumps(j)
    


def ConfigureLogging(AWS_Request_ID: Optional[str] = None) -> None:
    logging.getLogger().handlers.clear()

    formatter = FormatterJSON(AWS_Request_ID=AWS_Request_ID)
    JSONHandler = logging.StreamHandler()
    JSONHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    logger.addHandler(JSONHandler)

    logger2 = logging.getLogger("CephalonAhmes")
    logger2.setLevel(logging.INFO)
    
    
if __name__ == "__main__":
    ConfigureLogging()
    logging.getLogger().info("DoNotShow")
    logging.getLogger().error("DoShow")
    logging.getLogger("CephalonAhmes").info("DoShow")
    logging.getLogger().error(Exception("test"))
    logging.getLogger().error("test", extra={"data":["test", "test-data"]})
    try:
        raise ValueError("test err")
    except Exception as e:
        logging.getLogger().exception(e, stack_info=True)
