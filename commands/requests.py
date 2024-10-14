# in mygame/commands/request_commands.py

from evennia.utils.utils import crop
from world.requests.models import Request, Comment
from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import crop
from world.wod20th.utils.ansi_utils import wrap_ansi
from world.wod20th.utils.formatting import header, footer, divider
from evennia.utils.ansi import ANSIString

class CmdRequests(MuxCommand):
    """
    View and manage requests

    Usage:
      request
      request <#>
      request/create <category>/<title>=<text>
      request/comment <#>=<text>
      request/cancel <#>
      request/addplayer <#>=<player>

    Staff-only commands:
      request/assign <#>=<staff>
      request/close <#>

    Switches:
      create - Create a new request
      comment - Add a comment to a request
      cancel - Cancel one of your requests (player-only)
      addplayer - Add another player to your request (player-only)
      assign - Assign a request to a staff member (staff-only)
      close - Close a request (staff-only)
    """
    key = "+request"
    aliases = ["+requests", "+myjob", "+myjobs"]
    help_category = "General"

    def func(self):
        if not self.args and not self.switches:
            self.list_requests()
        elif self.args and not self.switches:
            self.view_request()
        elif "create" in self.switches:
            self.create_request()
        elif "comment" in self.switches:
            self.add_comment()
        elif "cancel" in self.switches:
            self.cancel_request()
        elif "addplayer" in self.switches:
            self.add_player()
        elif "assign" in self.switches:
            self.assign_request()
        elif "close" in self.switches:
            self.close_request()
        else:
            self.caller.msg("Invalid switch. See help +request for usage.")

    def list_requests(self):
        if self.caller.check_permstring("Admin"):
            requests = Request.objects.all().order_by('-date_created')
        else:
            requests = Request.objects.filter(requester=self.caller.account)

        if not requests:
            self.caller.msg("You have no open requests.")
            return

        output = header("Dies Irae Jobs", width=78, fillchar="|r-|n") + "\n"
        
        # Create the header row
        header_row = "|cReq #  Category   Request Title              Started  Handler           Status|n"
        output += header_row + "\n"
        output += ANSIString("|r" + "-" * 78 + "|n") + "\n"

        # Add each request as a row
        for req in requests:
            handler = req.handler.username if req.handler else "-----"
            row = (
                f"{req.id:<6}"
                f"{req.category:<11}"
                f"{crop(req.title, width=25):<25}"
                f"{req.date_created.strftime('%m/%d/%y'):<9}"
                f"{handler:<18}"
                f"{req.status}"
            )
            output += row + "\n"

        output += ANSIString("|r" + "-" * 78 + "|n") + "\n"
        output += divider("End Requests", width=78, fillchar="-", color="|r")
        self.caller.msg(output)

    def view_request(self):
        try:
            req_id = int(self.args)
            if self.caller.check_permstring("Admin"):
                request = Request.objects.get(id=req_id)
            else:
                request = Request.objects.get(id=req_id, requester=self.caller.account)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        output = header(f"Job {request.id}", width=78, fillchar="|r-|n") + "\n"
        output += f"|cJob Title:|n {request.title}\n"
        output += f"|cCategory:|n {request.category:<15} |cStatus:|n {request.status}\n"
        output += f"|cCreated:|n {request.date_created.strftime('%a %b %d %H:%M:%S %Y'):<30} |cHandler:|n {request.handler.username if request.handler else '-----'}\n"
        output += f"|cAdditional Players:|n\n"
        output += divider("Request", width=78, fillchar="-", color="|r", text_color="|c") + "\n"
        output += wrap_ansi(request.text, width=76, left_padding=2) + "\n\n"

        comments = request.comments.all().order_by('date_posted')
        if comments:
            output += divider("Comments", width=78, fillchar="-", color="|r", text_color="|c") + "\n"
            for comment in comments:
                output += f"{comment.author.username} [{comment.date_posted.strftime('%m/%d/%Y %H:%M')}]:\n"
                output += wrap_ansi(comment.text, width=76, left_padding=2) + "\n"

        output += footer(width=78, fillchar="|r-|n")
        self.caller.msg(output)

    def create_request(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +request/create <category>/<title>=<text>")
            return

        category_title, text = self.args.split("=", 1)
        category, title = category_title.split("/", 1)

        category = category.upper().strip()
        title = title.strip()
        text = text.strip()

        if category not in dict(Request.CATEGORIES):
            self.caller.msg(f"Invalid category. Choose from: {', '.join(dict(Request.CATEGORIES).keys())}")
            return

        new_request = Request.objects.create(
            category=category,
            title=title,
            text=text,
            requester=self.caller.account,
            status='NEW'
        )

        self.caller.msg(f"Request #{new_request.id} created successfully.")

    def add_comment(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +request/comment <#>=<text>")
            return

        req_id, comment_text = self.args.split("=", 1)
        
        try:
            req_id = int(req_id)
            request = Request.objects.get(id=req_id, requester=self.caller.account)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        Comment.objects.create(
            request=request,
            author=self.caller.account,
            text=comment_text.strip()
        )

        self.caller.msg(f"Comment added to request #{req_id}.")

    def cancel_request(self):
        try:
            req_id = int(self.args)
            request = Request.objects.get(id=req_id, requester=self.caller.account)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        request.status = 'CLOSED'
        request.save()
        self.caller.msg(f"Request #{req_id} has been cancelled.")

    def add_player(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +request/addplayer <#>=<player>")
            return

        req_id, player_name = self.args.split("=", 1)
        
        try:
            req_id = int(req_id)
            request = Request.objects.get(id=req_id, requester=self.caller.account)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        player = self.caller.search(player_name)
        if not player:
            return

        # Here you might want to add logic to associate the player with the request
        # For simplicity, we'll just add a comment
        Comment.objects.create(
            request=request,
            author=self.caller.account,
            text=f"Added player {player.name} to the request."
        )

        self.caller.msg(f"Player {player.name} added to request #{req_id}.")

    def assign_request(self):
        if not self.caller.check_permstring("Admin"):
            self.caller.msg("You don't have permission to assign requests.")
            return

        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +request/assign <#>=<staff>")
            return

        req_id, staff_name = self.args.split("=", 1)
        
        try:
            req_id = int(req_id)
            request = Request.objects.get(id=req_id)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        staff = self.caller.search(staff_name)
        if not staff:
            return

        request.handler = staff.account
        request.status = 'OPEN'
        request.save()

        Comment.objects.create(
            request=request,
            author=self.caller.account,
            text=f"Assigned to {staff.name}."
        )

        self.caller.msg(f"Request #{req_id} assigned to {staff.name}.")

    def close_request(self):
        if not self.caller.check_permstring("Admin"):
            self.caller.msg("You don't have permission to close requests.")
            return

        try:
            req_id = int(self.args)
            request = Request.objects.get(id=req_id)
        except (ValueError, Request.DoesNotExist):
            self.caller.msg("Request not found.")
            return

        request.status = 'CLOSED'
        request.save()

        Comment.objects.create(
            request=request,
            author=self.caller.account,
            text="Request closed."
        )

        self.caller.msg(f"Request #{req_id} has been closed.")