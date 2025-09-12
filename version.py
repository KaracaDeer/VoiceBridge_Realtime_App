"""
VoiceBridge Version Information
"""
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__build__ = "2024.09.10"
__author__ = "VoiceBridge Team"
__description__ = "Real-time Speech-to-Text API for Hearing-Impaired Individuals"


def get_version():
    """Get the current version string."""
    return __version__


def get_version_info():
    """Get the current version info tuple."""
    return __version_info__


def get_build_info():
    """Get build information."""
    return {"version": __version__, "build_date": __build__, "author": __author__, "description": __description__}
