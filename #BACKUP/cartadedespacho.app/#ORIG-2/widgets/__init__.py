# coding: utf-8
"""
widgets/main.py — Public facade for the widgets package.

All external code imports from here:
    from widgets import CardWidget, CustomMessageBox, ...

Nothing outside this package needs to know the internal module structure.
"""

from .base        import NoNewlineLineEdit
from .messagebox  import CustomMessageBox
from .tree        import AutoTreeWidget
from .cards       import CardWidget, InsuredGroupCard, EndorsementPolicyCard, GuaranteesCard, GuaranteesTableCard
from .dialog      import CustomDialog
from .endorsement import EndorsementTableCard

__all__ = [
    'NoNewlineLineEdit',
    'CustomMessageBox',
    'AutoTreeWidget',
    'CardWidget',
    'InsuredGroupCard',
    'EndorsementPolicyCard',
    'CustomDialog',
    'EndorsementTableCard',
]
