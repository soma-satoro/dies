from evennia import Command
from world.wod20th.utils.damage import apply_damage_or_healing, format_damage, format_status

class CmdHurt(Command):
    """
    Apply damage to yourself or another character.
    
    Usage:
        +hurt <amount><type>
        +hurt <name>=<amount><type>
    
    Example:
        +hurt 3l
        +hurt Bob=2b
    """
    key = "+hurt"
    locks = "cmd:all()"
    
    def parse(self):
        args = self.args.strip().split("=")
        if len(args) == 2:
            self.target_name, self.damage_input = args
        else:
            self.target_name, self.damage_input = None, args[0]
        self.target_name = self.target_name.strip() if self.target_name else None
        self.damage_input = self.damage_input.strip()

    def func(self):
        if not self.damage_input:
            self.caller.msg("Usage: +hurt <amount><type> or +hurt <name>=<amount><type>")
            return

        if self.target_name:
            if not self.caller.locks.check_lockstring(self.caller, "perm(Builder)"):
                self.caller.msg("You don't have permission to hurt others.")
                return
            target = self.caller.search(self.target_name)
            if not target:
                return
        else:
            target = self.caller

        try:
            damage = int(self.damage_input[:-1])
            damage_type = self.damage_input[-1].lower()
            if damage_type not in ['b', 'l', 'a']:
                raise ValueError
            if damage <= 0:
                raise ValueError
        except ValueError:
            self.caller.msg("Invalid damage input. Use a positive number followed by b, l, or a (e.g., 3l, 2b, 4a).")
            return

        damage_type_full = {'b': 'bashing', 'l': 'lethal', 'a': 'aggravated'}[damage_type]
        health = target.get_stat('other', 'other', 'Health') or 7
        if health == 0 and damage_type != 'a':
            self.caller.msg(f"{target.name} is already dead and cannot take more bashing or lethal damage.")
            return

        apply_damage_or_healing(target, damage, damage_type_full)
        # if the character's character.db.agg is greater than 
        if target.get_stat('Other', 'Splat', 'Splat') == 'Vampire':
            health = health + 2
        else:
            health = health + 1

        if target.db.agg > health:
            target.db.agg = health

        # Get the green gradient_name of th target
        target_gradient = target.db.gradient_name or target.key

        msg = f"|rHURT> |n{target_gradient} takes |r{damage}|n |y{damage_type_full}|n.\n"
        msg += f"|rHURT> |n{format_damage(target)} Status: {format_status(target)}"
        
        # Send messages and emit to room
        self.caller.location.msg_contents(msg, from_obj=self.caller)
