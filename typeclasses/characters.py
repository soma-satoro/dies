# typeclasses/characters.py
from evennia import DefaultCharacter
from world.wod20th.models import Stat

class Character(DefaultCharacter):
    
    def get_stat(self, stat_name):
        return self.db.stats.get(stat_name, None)
    
    def set_stat(self, stat_name, value):
        if not hasattr(self.db, "stats"):
            self.db.stats = {}
        self.db.stats[stat_name] = value
    
    def check_stat_value(self, stat_name, value):
        stat = Stat.objects.filter(name=stat_name).first()
        if stat and (value in stat.values):
            return True
        return False
