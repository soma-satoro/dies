from evennia.commands.default.muxcommand import MuxCommand
from evennia import search_object
from evennia.utils.utils import inherits_from

class AdminCommand(MuxCommand):
    """
    Base class for admin commands.
    Update with any additional definitions that may be useful to admin, then call the class by using 'CmdName(AdminCommand)', which
    will apply the following functions.
    """

    #search for a character by name match or dbref.
    def search_for_character(self, search_string):
        # First, try to find by exact name match
        results = search_object(search_string, typeclass="typeclasses.characters.Character")
        if results:
            return results[0]
        
        # If not found, try to find by dbref
        if search_string.startswith("#") and search_string[1:].isdigit():
            results = search_object(search_string, typeclass="typeclasses.characters.Character")
            if results:
                return results[0]
        
        # If still not found, return None
        return None

class CmdOOC(MuxCommand):
    """
    Speak or pose out-of-character in your current location.

    Usage:
      ooc <message>
      ooc :<pose>

    Examples:
      ooc Hello everyone!
      ooc :waves to the group.
    """
    key = "ooc"
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        if not self.args:
            self.caller.msg("Say or pose what?")
            return

        location = self.caller.location
        if not location:
            self.caller.msg("You are not in any location.")
            return

        # Strip leading and trailing whitespace from the message
        ooc_message = self.args.strip()

        # Check if it's a pose (starts with ':')
        if ooc_message.startswith(':'):
            pose = ooc_message[1:].strip()  # Remove the ':' and any following space
            message = f"|r<|n|yOOC|n|r>|n {self.caller.name} {pose}"
            self_message = f"|r<|n|yOOC|n|r>|n {self.caller.name} {pose}"
        else:
            message = f"|r<|n|yOOC|n|r>|n {self.caller.name} says, \"{ooc_message}\""
            self_message = f"|r<|n|yOOC|n|r>|n You say, \"{ooc_message}\""

        location.msg_contents(message, exclude=self.caller)
        self.caller.msg(self_message)

class CmdPlusIc(MuxCommand):
    """
    Return to the IC area from OOC.

    Usage:
      +ic

    This command moves you back to your previous IC location if available,
    or to the default IC starting room if not. You must be approved to use this command.
    """

    key = "+ic"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller

        # Check if the character is approved
        if not caller.tags.has("approved", category="approval"):
            caller.msg("You must be approved to enter IC areas.")
            return

        # Get the stored pre_ooc_location, or use the default room #30
        target_location = caller.db.pre_ooc_location or search_object("#30")[0]

        if not target_location:
            caller.msg("Error: Unable to find a valid IC location.")
            return

        # Move the caller to the target location
        caller.move_to(target_location, quiet=True)
        caller.msg(f"You return to the IC area ({target_location.name}).")
        target_location.msg_contents(f"{caller.name} has returned to the IC area.", exclude=caller)

        # Clear the pre_ooc_location attribute
        caller.attributes.remove("pre_ooc_location")

class CmdPlusOoc(MuxCommand):
    """
    Move to the OOC area (Limbo).

    Usage:
      +ooc

    This command moves you to the OOC area (Limbo) and stores your
    previous location so you can return later.
    """

    key = "+ooc"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current_location = caller.location

        # Store the current location as an attribute
        caller.db.pre_ooc_location = current_location

        # Find Limbo (object #2)
        limbo = search_object("#2")[0]

        if not limbo:
            caller.msg("Error: Limbo not found.")
            return

        # Move the caller to Limbo
        caller.move_to(limbo, quiet=True)
        caller.msg(f"You move to the OOC area ({limbo.name}).")
        limbo.msg_contents(f"{caller.name} has entered the OOC area.", exclude=caller)

class CmdMeet(MuxCommand):
    """
    Send a meet request to another player or respond to one.

    Usage:
      +meet <player>
      +meet/accept
      +meet/reject

    Sends a meet request to another player. If accepted, they'll be
    teleported to your location.
    """

    key = "+meet"
    locks = "cmd:all()"
    help_category = "General"

    def search_for_character(self, search_string):
        # First, try to find by exact name match
        results = search_object(search_string, typeclass="typeclasses.characters.Character")
        if results:
            return results[0]
        
        # If not found, try to find by dbref
        if search_string.startswith("#") and search_string[1:].isdigit():
            results = search_object(search_string, typeclass="typeclasses.characters.Character")
            if results:
                return results[0]
        
        # If still not found, return None
        return None

    def func(self):
        caller = self.caller

        if not self.args and not self.switches:
            caller.msg("Usage: +meet <player> or +meet/accept or +meet/reject")
            return

        if "accept" in self.switches:
            if not caller.ndb.meet_request:
                caller.msg("You have no pending meet requests.")
                return
            requester = caller.ndb.meet_request
            old_location = caller.location
            caller.move_to(requester.location, quiet=True)
            caller.msg(f"You accept the meet request from {requester.name} and join them.")
            requester.msg(f"{caller.name} has accepted your meet request and joined you.")
            old_location.msg_contents(f"{caller.name} has left to meet {requester.name}.", exclude=caller)
            requester.location.msg_contents(f"{caller.name} appears, joining {requester.name}.", exclude=[caller, requester])
            caller.ndb.meet_request = None
            return

        if "reject" in self.switches:
            if not caller.ndb.meet_request:
                caller.msg("You have no pending meet requests.")
                return
            requester = caller.ndb.meet_request
            caller.msg(f"You reject the meet request from {requester.name}.")
            requester.msg(f"{caller.name} has rejected your meet request.")
            caller.ndb.meet_request = None
            return

        target = self.search_for_character(self.args)
        if not target:
            caller.msg(f"Could not find character '{self.args}'.")
            return

        if target == caller:
            caller.msg("You can't send a meet request to yourself.")
            return

        if target.ndb.meet_request:
            caller.msg(f"{target.name} already has a pending meet request.")
            return

        target.ndb.meet_request = caller
        caller.msg(f"You sent a meet request to {target.name}.")
        target.msg(f"{caller.name} has sent you a meet request. Use +meet/accept to accept or +meet/reject to decline.")

class CmdSummon(AdminCommand):
    """
    Summon a player to your location.

    Usage:
      +summon <player>

    Teleports the specified player to your location.
    """

    key = "+summon"
    locks = "cmd:perm(admin)"
    help_category = "Admin"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +summon <player>")
            return

        target = self.search_for_character(self.args)
        if not target:
            caller.msg(f"Could not find character '{self.args}'.")
            return

        if not inherits_from(target, "typeclasses.characters.Character"):
            caller.msg("You can only summon characters.")
            return

        old_location = target.location
        target.move_to(caller.location, quiet=True)
        caller.msg(f"You have summoned {target.name} to your location.")
        target.msg(f"{caller.name} has summoned you.")
        old_location.msg_contents(f"{target.name} has been summoned by {caller.name}.", exclude=target)
        caller.location.msg_contents(f"{target.name} appears, summoned by {caller.name}.", exclude=[caller, target])

class CmdJoin(AdminCommand):
    """
    Join a player at their location.

    Usage:
      +join <player>

    Teleports you to the specified player's location.
    """

    key = "+join"
    locks = "cmd:perm(admin)"
    help_category = "Admin"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +join <player>")
            return

        target = self.search_for_character(self.args)
        if not target:
            caller.msg(f"Could not find character '{self.args}'.")
            return

        if not inherits_from(target, "typeclasses.characters.Character"):
            caller.msg("You can only join characters.")
            return

        caller.move_to(target.location, quiet=True)
        caller.msg(f"You have joined {target.name} at their location.")
        target.location.msg_contents(f"{caller.name} appears in the room.", exclude=caller)