# typeclasses/characters.py
from evennia import DefaultCharacter

class Character(DefaultCharacter):
    
    def get_stat(self, stat_name):
        if not hasattr(self.db, "stats"):
            return None
        return self.db.stats.get(stat_name, None)
    
    def set_stat(self, stat_name, value):
        if not hasattr(self.db, "stats"):
            self.db.stats = {}
        self.db.stats[stat_name] = value
    
    def check_stat_value(self, stat_name, value):
        from world.wod20th.models import Stat  # Import here to avoid circular reference
        stat = Stat.objects.filter(name=stat_name).first()
        if stat and (value in stat.values):
            return True
        return False

