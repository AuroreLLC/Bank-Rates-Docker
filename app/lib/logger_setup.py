import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
import json
import gzip
import shutil
from typing import Optional, Dict, Any


class ColoredFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)


class CompressedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_dir = Path(self.baseFilename).parent / "archived"
        self.archive_dir.mkdir(exist_ok=True)
    
    def doRollover(self):
        super().doRollover()
        if self.backupCount > 0:
            for i in range(self.backupCount, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                if os.path.exists(sfn) and not sfn.endswith('.gz'):
                    base_name = Path(sfn).name
                    archived_path = self.archive_dir / f"{base_name}.gz"
                    with open(sfn, 'rb') as f_in:
                        with gzip.open(archived_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(sfn)


class LoggerConfig:
    
    def __init__(self, 
                 app_name: str = "MyApp",
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 console_output: bool = True,
                 json_format: bool = False,
                 max_file_size: int = 50 * 1024 * 1024,
                 backup_count: int = 30,
                 compression: bool = True):
        
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.console_output = console_output
        self.json_format = json_format
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.compression = compression
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        (self.log_dir / "archived").mkdir(exist_ok=True)
        self._setup_logger()
    
    def _setup_logger(self):
        
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.handlers.clear()
        
        if self.json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        main_log_file = self.log_dir / f"{self.app_name}.log"
        if self.compression:
            file_handler = CompressedTimedRotatingFileHandler(
                filename=main_log_file,
                when='midnight',
                interval=1,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        else:
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=main_log_file,
                when='midnight',
                interval=1,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        error_log_file = self.log_dir / f"{self.app_name}_errors.log"
        if self.compression:
            error_handler = CompressedTimedRotatingFileHandler(
                filename=error_log_file,
                when='midnight',
                interval=1,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        else:
            error_handler = logging.handlers.TimedRotatingFileHandler(
                filename=error_log_file,
                when='midnight',
                interval=1,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        if self.log_level == logging.DEBUG:
            debug_log_file = self.log_dir / f"{self.app_name}_debug.log"
            if self.compression:
                debug_handler = CompressedTimedRotatingFileHandler(
                    filename=debug_log_file,
                    when='midnight',
                    interval=1,
                    backupCount=7,
                    encoding='utf-8'
                )
            else:
                debug_handler = logging.handlers.TimedRotatingFileHandler(
                    filename=debug_log_file,
                    when='midnight',
                    interval=1,
                    backupCount=7,
                    encoding='utf-8'
                )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(file_formatter)
            root_logger.addHandler(debug_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        return logging.getLogger(name or self.app_name)
    
    def log_system_info(self):
        logger = self.get_logger()
        logger.info("="*60)
        logger.info(f"Starting application: {self.app_name}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Log directory: {self.log_dir.absolute()}")
        logger.info(f"Logging level: {logging.getLevelName(self.log_level)}")
        logger.info("="*60)


def setup_logging(app_name: str = "MyApp", 
                 log_level: str = "INFO",
                 log_dir: str = "logs",
                 console_output: bool = True,
                 json_format: bool = False) -> LoggerConfig:
    
    config = LoggerConfig(
        app_name=app_name,
        log_level=log_level,
        log_dir=log_dir,
        console_output=console_output,
        json_format=json_format
    )
    
    config.log_system_info()
    return config


if __name__ == "__main__":
    log_config = setup_logging(
        app_name="MyApplication",
        log_level="DEBUG",
        log_dir="logs",
        console_output=True,
        json_format=False
    )
    
    logger = log_config.get_logger("main")
    
    logger.debug("Debug message - detailed information")
    logger.info("Application started successfully")
    logger.warning("Warning: using default configuration")
    logger.error("Simulated error for testing")
    
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Zero division error caught")
    
    extra_logger = log_config.get_logger("database")
    extra_logger.info("Query executed", extra={'query_time': 0.045, 'rows': 150})
    
    logger.info("Logging example completed")