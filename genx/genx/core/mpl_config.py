from __future__ import annotations

from typing import Optional

import matplotlib as mpl

# rcParams definitions for use in light/dark themes respectively.
# Applied my own preferred styling to plots. Maybe remove this if
# it looks bad inside GUI - Kibbi 12/03/2026

# Common style for both light and dark themes
_COMMON_RC = {
    "figure.subplot.wspace": 0,
    "axes.labelsize": 13,
    "xtick.labelsize": 12,
    "xtick.direction": "in",
    "xtick.minor.visible": True,
    "ytick.labelsize": 12,
    "ytick.direction": "in",
    "ytick.minor.visible": True,
    "axes.linewidth": 1.5,
    "axes.grid": True,
    "grid.linestyle": '--',
}

# Additional colours for dark theme
_DARK_RC = {
    "figure.facecolor": "#1e1e1e",
    "axes.facecolor": "black",
    "axes.edgecolor": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "text.color": "white",
    "grid.color": "gray",
}

# Explicit light-theme colours (so switching back from dark resets properly)
_LIGHT_RC = {
    "figure.facecolor": "#e7e7e7",
    "axes.facecolor": "#F4F1F1",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "text.color": "black",
    "grid.color": "lightgray",
}


def _detect_dark_mode() -> bool:
    """Best-effort detection of OS dark mode via wx.

    Returns False if wx is unavailable or detection fails.
    """

    try:
        import wx  # type: ignore
    except Exception:
        return False

    # wx >= 4.1 has GetAppearance with IsDark()
    try:
        appearance = wx.SystemSettings.GetAppearance()
        if hasattr(appearance, "IsDark"):
            return bool(appearance.IsDark())
    except Exception:
        pass

    # Fallback: infer from system window colour luminance
    try:
        col = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        r, g, b = col.Get()
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128
    except Exception:
        return False


def apply_genx_mpl_style(is_dark: Optional[bool] = None) -> None:
    """Apply GenX-wide matplotlib rcParams.

    If *is_dark* is None, try to auto-detect via wx; otherwise honour
    the explicit flag. This function is safe to call multiple times.
    """

    if is_dark is None:
        is_dark = _detect_dark_mode()

    rc = dict(_COMMON_RC)
    if is_dark:
        rc.update(_DARK_RC)
    else:
        rc.update(_LIGHT_RC)

    mpl.rcParams.update(rc)
