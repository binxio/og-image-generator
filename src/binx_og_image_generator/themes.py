from dataclasses import dataclass
from os import path
import typing


"""Directory with images"""
IMAGES_DIR = path.join(path.dirname(__file__), "images")

"""Directory with fonts"""
FONTS_DIR = path.join(path.dirname(__file__), "fonts")

_RGBColorType: typing.TypeAlias = typing.Tuple[int, int, int]


@dataclass(kw_only=True)
class Theme:
    """OG banner theme definition"""

    """RGB notation of text color"""
    text_color: _RGBColorType

    """RGB notation of background color"""
    background_color: _RGBColorType

    """RGB notation of section deviders """
    border_color: _RGBColorType

    """Xebia logo file"""
    logo: str

    """Regular weight font file"""
    normal_font: str

    """Bold weight font file"""
    bold_font: str

    """Banner image mask file"""
    banner_mask: str = "banner-mask.png"

    """Author profile image mask"""
    profile_mask: str = "profile-mask.png"

    def __post_init__(self):
        """ """

        self.profile_mask = self.normalise_path(self.profile_mask, IMAGES_DIR)
        self.banner_mask = self.normalise_path(self.banner_mask, IMAGES_DIR)
        self.logo = self.normalise_path(self.logo, IMAGES_DIR)

        self.normal_font = self.normalise_path(self.normal_font, FONTS_DIR)
        self.bold_font = self.normalise_path(self.bold_font, FONTS_DIR)

    def normalise_path(self, p: str, prefix: str) -> str:
        """Normalises file path by prepending it with `prefix` if needed."""

        if path.isabs(p):
            raise ValueError(f"Expected a relative path, got absolute path: {p!r}")

        candidate = path.abspath(path.join(prefix, p))
        abs_prefix = path.abspath(prefix)

        if path.commonpath([candidate, abs_prefix]) != abs_prefix:
            raise ValueError(f"Path {p!r} resolves outside of {prefix!r}")

        return candidate


_XebiaDark = Theme(
    text_color=(255, 255, 255),
    background_color=(21, 0, 39),
    border_color=(82, 67, 96),
    logo="xebia-logo-white.png",
    normal_font="Suisse/SuisseIntl-Regular.ttf",
    bold_font="Suisse/SuisseIntl-Medium.ttf",
)
_XebiaLight = Theme(
    text_color=(0, 0, 0),
    background_color=(255, 255, 255),
    border_color=(0, 0, 0),
    logo="xebia-logo-black.png",
    normal_font="Suisse/SuisseIntl-Regular.ttf",
    bold_font="Suisse/SuisseIntl-Medium.ttf",
)

THEMES = {"xebia-dark": _XebiaDark, "xebia-light": _XebiaLight}
