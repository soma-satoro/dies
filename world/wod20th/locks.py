# world/wod20th/locks.py
from evennia.locks.lockfuncs import _TRUE, _FALSE

def is_splat(character, splat_name):
    """
    Checks if the character belongs to a specific splat.
    """
    return character.db.splat == splat_name

def has_stat_value(character, stat_name, value):
    """
    Checks if the character's stat is at least a specific value.
    """
    stat_value = character.get_stat(stat_name)
    if stat_value is None:
        return _FALSE
    return stat_value >= value

# Register these functions in Evennia
from evennia.locks.lockhandler import LOCK_FUNC_MODULES
LOCK_FUNC_MODULES.append("world.wod20th.locks")
