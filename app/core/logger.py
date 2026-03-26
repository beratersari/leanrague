"""
Logger - Configurable logging utility for n-layered architecture.
Provides different log levels and configurable output options.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Any
from pathlib import Path

# Log level constants
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

# Default log levels mapping
LEVEL_NAMES = {
    DEBUG: 'DEBUG',
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR',
    CRITICAL: 'CRITICAL',
}

# Reverse mapping
LEVEL_VALUES = {v: k for k, v in LEVEL_NAMES.items()}


class LoggerConfig:
    """
    Configuration class for the Logger.
    Can be customized via Django settings or direct instantiation.
    """
    
    def __init__(
        self,
        level: int = INFO,
        log_file: Optional[str] = None,
        log_format: Optional[str] = None,
        date_format: Optional[str] = None,
        console_output: bool = True,
        file_output: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
    ):
        """
        Initialize logger configuration.
        
        Args:
            level: Minimum log level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
            log_file: Path to log file (if file_output is True)
            log_format: Format string for log messages
            date_format: Format string for timestamps
            console_output: Whether to output to console
            file_output: Whether to output to file
            max_file_size: Maximum size of log file before rotation (bytes)
            backup_count: Number of backup files to keep
        """
        self.level = level
        self.log_file = log_file or 'app.log'
        self.log_format = log_format or '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        self.date_format = date_format or '%Y-%m-%d %H:%M:%S'
        self.console_output = console_output
        self.file_output = file_output
        self.max_file_size = max_file_size
        self.backup_count = backup_count
    
    @classmethod
    def from_django_settings(cls) -> 'LoggerConfig':
        """Create config from Django settings if available."""
        try:
            from django.conf import settings
            
            level_str = getattr(settings, 'LOG_LEVEL', 'INFO')
            level = LEVEL_VALUES.get(level_str.upper(), INFO)
            
            return cls(
                level=level,
                log_file=getattr(settings, 'LOG_FILE', 'app.log'),
                log_format=getattr(settings, 'LOG_FORMAT', None),
                date_format=getattr(settings, 'LOG_DATE_FORMAT', None),
                console_output=getattr(settings, 'LOG_CONSOLE_OUTPUT', True),
                file_output=getattr(settings, 'LOG_FILE_OUTPUT', False),
                max_file_size=getattr(settings, 'LOG_MAX_FILE_SIZE', 10 * 1024 * 1024),
                backup_count=getattr(settings, 'LOG_BACKUP_COUNT', 5),
            )
        except Exception:
            # Fall back to defaults if Django not configured
            return cls()


class Logger:
    """
    Custom Logger class with configurable levels and outputs.
    Provides a simple interface for logging across the application.
    """
    
    _instances = {}  # Singleton pattern per logger name
    
    def __new__(cls, name: str = 'lang_learn', config: Optional[LoggerConfig] = None):
        """Ensure singleton per logger name."""
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(self, name: str = 'lang_learn', config: Optional[LoggerConfig] = None):
        """
        Initialize the logger.
        
        Args:
            name: Name of the logger (typically module name)
            config: LoggerConfig instance (if None, uses Django settings or defaults)
        """
        if self._initialized:
            return
        
        self.name = name
        self.config = config or LoggerConfig.from_django_settings()
        
        # Create Python logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self.config.level)
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=self.config.log_format,
            datefmt=self.config.date_format
        )
        
        # Console handler
        if self.config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.file_output:
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.config.log_file,
                    maxBytes=self.config.max_file_size,
                    backupCount=self.config.backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(self.config.level)
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
            except Exception as e:
                # If file logging fails, continue with console only
                self._logger.warning(f"Could not set up file logging: {e}")
        
        self._initialized = True
    
    @property
    def level(self) -> int:
        """Get current log level."""
        return self._logger.level
    
    @level.setter
    def level(self, value: int):
        """Set log level."""
        self._logger.setLevel(value)
        for handler in self._logger.handlers:
            handler.setLevel(value)
    
    def set_level(self, level: int):
        """Set the minimum log level."""
        self.level = level
    
    def get_level_name(self) -> str:
        """Get the current log level name."""
        return LEVEL_NAMES.get(self.level, 'UNKNOWN')
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """Internal logging method."""
        if args:
            try:
                message = message % args
            except Exception:
                pass  # Fall back to raw message if formatting fails
        
        extra = kwargs.get('extra', {})
        exc_info = kwargs.get('exc_info', False)
        
        self._logger.log(level, message, exc_info=exc_info, extra=extra)
    
    def debug(self, message: str, *args, **kwargs):
        """Log a debug message."""
        self._log(DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log an info message."""
        self._log(INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log a warning message."""
        self._log(WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log an error message."""
        self._log(ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log a critical message."""
        self._log(CRITICAL, message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log an exception with traceback."""
        kwargs['exc_info'] = True
        self._log(ERROR, message, *args, **kwargs)
    
    def log_function_entry(self, func_name: str, **kwargs):
        """Log function entry with parameters."""
        params = ', '.join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else "no args"
        self.debug(f"Entering {func_name}({params})")
    
    def log_function_exit(self, func_name: str, result: Any = None, success: bool = True):
        """Log function exit with result."""
        if success:
            self.debug(f"Exiting {func_name} - Success")
        else:
            self.warning(f"Exiting {func_name} - Failed: {result}")
    
    def log_exception(self, func_name: str, error: Exception):
        """Log an exception that occurred in a function."""
        self.exception(f"Exception in {func_name}: {type(error).__name__}: {error}")


# Convenience function to get a logger instance
def get_logger(name: str = 'lang_learn') -> Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Name of the logger (typically __name__ or module name)
    
    Returns:
        Logger instance
    """
    return Logger(name)


# Default logger instance for the application
default_logger = get_logger('lang_learn')
