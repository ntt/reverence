import __builtin__
__builtin__.MILLISECOND = 10000L
__builtin__.SECOND = 10000000L
__builtin__.MINUTE = 60L*SECOND
__builtin__.HOUR   = 60L*MINUTE
__builtin__.DAY    = 24L*HOUR

__all__ = [
	"blue", "util", "config", "cache", "embedfs",
	"dbutil", "const", "objectCaching", "exceptions", "strings",
	"carbon", "eve",
]
