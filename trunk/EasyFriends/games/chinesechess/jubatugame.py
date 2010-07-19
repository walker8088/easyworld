#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Chess main module.

This is the only module to which the main program and the communication thread communicates to. 
"""

from jubatu.gameengine import BaseEngine
import newchessgame
import pyxmpp.all
import pyxmpp.expdict
import libxml2
from jubatu import util
import wx
from jubatu import commands
import time
from jubatu import events
from frontend.chess3dgui import Chess3dGui
from backend.chess import Game, Board, Move, Piece, Coord, PIECE_NAMES, WHITE, BLACK, UNDEFINED
from backend.chess import ONGOING, MATE, STALEMATE, QUEEN, ROOK, BISHOP, KNIGHT
import math
import os
import logging
import gettext
import md5

# Load the translations file for the preferred language
lang = gettext.translation('chess', os.path.join(os.path.dirname(__file__), 'i18n'), languages=util.get_preferred_languages(), fallback=True)
# A game module MUST not use the lang.install() function, as it would override the default language for the core
_ = lang.ugettext 
        
DEBUG_MODE = False

COLOUR_NAMES = {WHITE:"white", BLACK:"black", UNDEFINED:None}
BACKEND_PIECES = {"queen":QUEEN, "rook":ROOK, "bishop":BISHOP, "knight":KNIGHT}

class Match:
    """Helper class to act as a cointainer for match-related objects."""
    
    pass

class ChessEngine(BaseEngine):
    """Chess Engine.

    This class implements the chess-specific protocol and manages both the frontend and the backend.
    """
    
    proposedMatches = pyxmpp.expdict.ExpiringDictionary(600)
    activeMatches = {}
    
    def __init__(self):
        logging.getLogger("chessEngine").setLevel(logging.WARNING)   # set the logging verbosity for this module here
        
    def version(self):
        return "0.1.0"
    
    __filehash__ = None
    def id(self):
        """Main identificator for the module.
        
        This number is intented to be used extensively in all the game protocols. By changing it, you are effectively
        making the engine a distinct one, even if no other change is done.
        As this should change every time some change is done to the module, i recommend using a hash of something
        neccesarily changing with every version (as the version name itself). Take care of not hashing strings
        subject to gettext processing ;)
        """
    
        if self.__filehash__:   # We only need to calculate the hash once
            return self.__filehash__
        else:
            hash = md5.new()
            hash.update("jubatu-chess"+self.version())
            self.__filehash__ = hash.hexdigest()

            return self.__filehash__

    def name(self):
        """Name of the game implemented.
        
        Although this policy could change in future versions, by now we prefer to include the version number within
        the name string.
        """
        
        return _(u"Chess")+" "+self.version()

    def description(self):
        return _(u"Popular and ancient-rooted strategy game for 2 players.\nThis module support FIDE's rules.")

    def new_game_panel(self, parent):
        """Return a 'new game' panel specific for this game.
        
        This function will be called by the main application when the user select this game to start a new match.
        The panel must implement all the information needed to initialize the match. (This is heavily dependent of the
        game, but that can include: adversaries, colors of pieces, variants of the rules,
        players with special characteristics, etc.)
        """
        
        return newchessgame.NewChessGamePanel(self, parent=parent)
    
    def send_proposal(self, opponentJid, ownColour):
        """Send a new game proposal to out adversary.
        
        
        opponentJid -- the xmpp JID of our adversary.
        ownColour -- the colour of the pieces we will rule.
        This function will be called by the corresponding 'new game' panel when the user complete the requested
        information and ask to send the proposal.
        """
        
        iq_id = util.random_hex_string(8)
        iqStanza = pyxmpp.iq.Iq(None, None, opponentJid, "set", iq_id)
        proposalNode = iqStanza.new_query("jubatu:games", "proposal")
        
        proposalNode.setProp("engine-id", self.id())
        proposalNode.setProp("match-id", util.random_hex_string(8))
        proposalNode.setProp("colour", ownColour)
        
        logging.getLogger("chessEngine").debug(iqStanza.serialize())
        wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, self.res_proposal, self.err_proposal, self.timeout_proposal, 30))
        
        match = Match()
        match.proposalStanza = iqStanza
        self.proposedMatches.set_item(iq_id, match)
        
    ### IMPORTANT NOTE about the following handlers:
    ### It must be noted that the handlers passed to the communication thread to be called when a reply is received
    ### will be executed in the context of the communication thread. Due to that, to guarantee thread safety, they
    ### are passed through a commands' queue contained in the engine, so that they can be processed in the thread in
    ### which the engine is running.
        
    def res_proposal(self, stanza):
        """Handler for a reply for the proposal of type 'result'"""
        
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.local_proposal_accepted))
        return

    def err_proposal(self, stanza):
        """Handler for a reply for the proposal of type 'error'"""
        
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.local_proposal_error))
        return

    def timeout_proposal(self):
        """Handler for the timeout of a sended 'new game' proposal."""
        
        wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_("Chess match proposal timed-out."), _("No response"), wx.CENTRE))

    def res_local_turn(self, stanza):
        """Handler for a reply (of type 'result') of a "turn" sended by us."""
        
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.local_turn_acknowledged))
        return

    def err_local_turn(self, stanza):
        """Handler for a reply (of type 'error') of a "turn" sended by us."""
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.local_turn_rejected))
        return
    
    def make_res_resign(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        
        return lambda stanza: self.res_resign(stanza, match)
    def res_resign(self, stanza, match):
        """Handler for a reply of type 'result' to a 'resign' issued by us."""
        
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.make_resign_handler(match)))
        return

    def make_res_accept_draw(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        return lambda stanza: self.res_accept_draw(stanza, match)
    def res_accept_draw(self, stanza, match):
        """Handler for a reply of type 'result' to a 'accept draw' issued by us."""
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.make_draw_agreement_handler(match)))
        return

    def make_res_claim_draw(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        return lambda stanza: self.res_claim_draw(stanza, match)
    def res_claim_draw(self, stanza, match):
        """Handler for a reply of type 'result' to a 'draw claim' issued by us."""
        self.commandsQueue.put(commands.JuXmppRecIqStanza(stanza.copy(), self.make_draw_claim_accepted_handler(match)))
        return

    def timeout_local_turn(self):
        """Handler for the time-out of a "turn" stanza issued by us."""
        
        wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_("Chess turn sending timed-out."), _("No response"), wx.CENTRE))

    def local_proposal_accepted(self, stanza):
        """Handle the receipt of an acceptation for our sended 'new game' proposal.
        
        stanza -- the reply stanza to our proposal (a normal 'result' reply probably).
        This function will initiate the new match after checking we effectively sended that proposal.
        """
        
        logging.getLogger("chessEngine").debug(stanza.serialize())
        if self.proposedMatches.has_key(stanza.get_id()):    # This should always happen
            logging.getLogger("chessEngine").debug("match-id of the replied proposal: %s", self.proposedMatches[stanza.get_id()].proposalStanza.get_query().prop("match-id"))
            match = self.proposedMatches[stanza.get_id()]
            
            self.launch_game(match)
            
            del self.proposedMatches[stanza.get_id()]
        else:
            logging.getLogger("chessEngine").warning("Stanza's id not recognized. The proposal probably timed-out.")
            
    def launch_game(self, match):
        """Set up a new game.
        
        match -- 'Match' object containing, at this point, the proposal stanza originating the new match (that stanza
            contains all the info needed to set up the new match.)
        This function initialize the appropiate front-end and back-end objects, and create a new 'active match'.
        """
         
        match_id = match.proposalStanza.get_query().prop("match-id")
        opponentJid = self.get_opponent_jid(match)
        localColour = self.get_local_colour(match)
            
        match.gui = Chess3dGui(match_id, self.commandsQueue)
        match.gui.set_title(_(u"Chess/%s") % opponentJid.bare().as_unicode())
        
        match.game = Game()
        if not DEBUG_MODE:
            match.game.setup()
        else:
            testGame = open(os.path.join(os.path.dirname(__file__), "test.pgn"))
            match.game.import_pgn(testGame)
            testGame.close()
        logging.getLogger("chessEngine").debug(match.game.board)
        for i in range(8):
            for j in range(8):
                piece = match.game.board.square(Coord(i,j))
                match.gui.set_piece(PIECE_NAMES[piece.type].lower(), COLOUR_NAMES[piece.colour], i, j)
                
        if localColour=="white":
            match.gui.horizontalAngleSlider["value"]=7*math.pi/4
        elif localColour=="black":
            match.gui.horizontalAngleSlider["value"]=3*math.pi/4

        if localColour==("white","black")[match.game.board.get_turn()]:    
            self.give_turn(match)
        
        self.activeMatches[match_id]=match
        
    def get_local_colour(self, match):
        """Return the colour of pieces ruled by the local user in a certain match.
        
        match -- the 'Match' object containing the info for the queried match.
        """
        
        colour = match.proposalStanza.get_query().prop("colour")
        if wx.GetApp().localJid.as_unicode() == match.proposalStanza.get_to_jid():
            if colour=="white":
                localColour="black"
            elif colour=="black":
                localColour="white"
        else:
            localColour=colour

        return localColour
        
    def get_opponent_jid(self, match):
        """Return the xmpp JID of our adversary in a certain match.
        
        match -- the 'Match' object containing the info for the queried match.
        """
        
        if wx.GetApp().localJid.as_unicode() == match.proposalStanza.get_to_jid():
            opponentJid = pyxmpp.all.JID(match.proposalStanza.get_from_jid())
        else:
            opponentJid = pyxmpp.all.JID(match.proposalStanza.get_to_jid())
            
        return opponentJid
            
    def give_turn(self, match):
        """Manage the start of a turn for the local user in the given match.
        
        match - 'Match' object containing info for the corresponding match.
        Basicly, this function ask the front-end to allow the local user to move his pieces, passing it
        the allowed actions for this turn according to the back-end.
        """
        
        backendLegalMoves = match.game.board.get_legal_moves(None, None)
        frontendLegalMoves = {}
        for move in backendLegalMoves:
            position = (move.position.col, move.position.row)
            destination = (move.destination.col, move.destination.row)
            if not frontendLegalMoves.has_key(position):
                frontendLegalMoves[position] = set()
            frontendLegalMoves[position].add(destination)
            
        # check whether the local player can claim draw
        canClaimDraw = False
        if match.game.board.check_threefold_repetition(match.game.moves, match.game.initial_board()):
            canClaimDraw = True
        elif match.game.board.check_fifty_move():
            canClaimDraw = True
            
        match.gui.give_turn(frontendLegalMoves, canClaimDraw)
    
    def local_proposal_error(self, stanza):
        """Handle the receipt of an error stanza in reply to our 'new game' proposal"""
        
        logging.getLogger("chessEngine").debug(stanza.serialize())
        errorCondition = stanza.get_error().get_condition().name
        if errorCondition=="feature-not-implemented":
            wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_("%s doesn't support this specific game engine.")%stanza.get_from_jid().as_unicode(), _("Lack of support"), wx.CENTRE)|wx.ICON_ERROR)
        elif errorCondition=="not-acceptable":
            wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_("Chess match rejected. The user %s did't accept the proposal.")%(stanza.get_from_jid().as_unicode()), _("Match refused"), wx.CENTRE))
        del self.proposedMatches[stanza.get_id()]  # Eliminate the match from the list of proposed matches
        
    def local_turn_acknowledged(self, stanza):
        """Handler for a reply to our turn of type 'results'"""
        
        # We do nothing by now; it could be useful if at some point we want to resend turns after a timeout
        pass
        
            
    def local_turn_rejected(self, stanza):
        """Handle the receipt of an error stanza in reply to our "turn" stanza."""
        
        logging.getLogger("chessEngine").debug(stanza.serialize())
        if stanza.get_error().get_type()=="not-allowed":
            wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_(u"The remote client of %s has rejected the move because it is considered to be an invalid move. Check with your opponent than you both are using EXACTLY the same game engine, and report the developers about a potential bug in that case.")%stanza.get_to_jid(), _(u"Unrecoverable error"), wx.CENTRE|wx.ICON_ERROR, self.commandsQueue, stanza))
        else:
            logging.getLogger("chessEngine").error("Type of stanza error distinct from 'not-allowed'")
        pass
        
    def run_step(self):
        """Implements a single iteration of the engine's main loop."""
        
        if not self.commandsQueue.empty():
            self.process_command(self.commandsQueue.get())
        time.sleep(0.01)
        
    def run(self):
        """Engine's main loop. Currently not used.
        
        This was intended to act as the main loop for the engine with it running in an isolated thread. However,
        due to technical reasons related with the 3d-engine (Panda3d), we have had to run it in the same thread
        than the main Jubatu window. If a future version of Panda3d allowed us to use it in multi-thread mode,
        maybe we could go back to the original idea.
        """
        
        while True:
            self.run_step()
            if self.commandsQueue.empty() and not wx.GetApp().GetTopWindow():
                return
            
    def remote_proposal_received(self, stanza):
        """Handle the receipt of a 'new game' proposal.
        
        After the receipt, the local user is asked to accept/refuse the proposal. Notice that the messagebox
        is shown in the main Jubatu application. This is for convenience, as the 3d-GUI doesn't run on top of the
        wx framework, so it's more easy for us to show the info in the main window. The desirable choice would be
        that, at some point in the future, Panda3d allowed us to embed a Panda 3d-view inside a wx.Panel.
        """
        
        logging.getLogger("chessEngine").debug("'New game' proposal just received:\n%s", stanza.serialize())
        payload = stanza.get_query()
        if payload.prop("colour")=="white":
            whitePlayer = stanza.get_from_jid().as_unicode()
            blackPlayer = stanza.get_to_jid().as_unicode()
        elif payload.prop("colour")=="black":
            whitePlayer = stanza.get_to_jid().as_unicode()
            blackPlayer = stanza.get_from_jid().as_unicode()
        else:
            logging.getLogger("chessEngine").error("Inadequate 'colour' property in received 'new game' proposal:\n%s", stanza.serialize())
            return  # we should add proper error handling later
            
        wx.GetApp().GetTopWindow().AddPendingEvent(events.JuMessageBox(_(u"The user %s has invited you to play a chess match, with the following disposition:\n\nWhite: %s\nBlack: %s\n\nDo you accept?")%(stanza.get_from_jid().as_unicode(), whitePlayer, blackPlayer), _(u"Match invitation (Chess)"), wx.CENTRE|wx.ICON_QUESTION|wx.YES_NO, self.commandsQueue, stanza))
        
    def proposal_answered_by_local_player(self, stanza, answer):
        """Handle the local user's answer to a remote 'new game' proposal received.
        
        stanza -- proposal stanza to which we are replying
        answer -- the reply from the local user
        Basicly, it reply to the buddy sending the proposal in an appropriate way and, if the match have
        been accepted, ask the neccesary set-up for a new match.
        """
        
        logging.getLogger("chessEngine").debug(stanza.serialize())
        logging.getLogger("chessEngine").debug("User answer: %s", {wx.YES:"yes", wx.NO:"no"}[answer])
        if answer==wx.YES:
            reply=stanza.make_result_response()
            wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanzaReply(reply))
            
            match = Match()
            match.proposalStanza = stanza
            
            self.launch_game(match)
        elif answer==wx.NO:
            reply=stanza.make_error_response("not-acceptable")
            wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanzaReply(reply))
        else:  # error
            logging.getLogger("chessEngine").error("Unrecognized user reply.")
            return
        
    def move(self, match, move):
        """Executes a move in a given match, updating both the back-end and fron-end in a proper way.
        
        match -- 'Match' object containing info about the match.
        move -- The move to be performed.
        Notice that automatic end game conditions (checkmate, stalemate) are checked here.
        """
        
        # match the move with the one generated by the backend, as this can have additional information
        # neccesary for the backend (i.e.: special moves; castle, pawn passant, etc)
        backendLegalMoves = match.game.board.get_legal_moves(None, None)
        for legalMove in backendLegalMoves:
            if legalMove.position == move.position and legalMove.destination == move.destination:
                if legalMove.promote is not None and move.promote is None:
                    if self.get_local_colour(match) == ("white", "black")[match.game.board.get_turn()]:
                        match.moveWithoutPromotion = move
                        match.gui.request_promotion_piece()
                        raise LackPromotion()
                    else:
                        logging.getLogger("chessEngine").error("Movement out of turn.")
                if legalMove.promote == move.promote:
                    move = legalMove
                    break
        
        # do the move
        previousBoard = match.game.board.clone()
        moveResult = match.game.move(move)
        if moveResult:
            # print the move in the front-end
            if match.game.board.get_turn()==BLACK:
                moveText = "%s. %s-%s"%(match.game.board.move_count/2, str(move.position), str(move.destination))
            else:
                moveText = ", %s-%s"%(str(move.position), str(move.destination))
            match.gui.show_move_text(moveText)
        # refresh the frontend
        for i in range(8):
            for j in range(8):
                piece = match.game.board.square(Coord(i,j))
                prevPiece = previousBoard.square(Coord(i,j))
                if (piece.type != prevPiece.type) or (piece.colour != prevPiece.colour):
                    match.gui.set_piece(PIECE_NAMES[piece.type].lower(), COLOUR_NAMES[piece.colour], i, j)
                    
        result = match.game.board.check_result()
        if result == MATE:
            if match.game.board.get_turn()==WHITE:
                text = _("Checkmate. Black wins.")
            else:
                text = _("Checkmate. White wins.")
                
            match.gui.finish_game(text)
        elif result == STALEMATE:
            match.gui.finish_game(_("Stalemate. Draw."))
            
        return moveResult
            
    def make_resign_handler(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        
        return lambda stanza: self.game_resigned(stanza, match)
    def game_resigned(self, stanza, match):
        """Handle a resign, updating the front-end in an appropriate way."""
        
        if match.game.board.get_turn()==WHITE:
            text = _("White resigns. Black wins.")
        else:
            text = _("Black resigns. White wins.")
        
        match.gui.finish_game(text)
        
    def make_draw_agreement_handler(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        return lambda stanza: self.draw_agreement(stanza, match)
    def draw_agreement(self, stanza, match):
        """Handle a draw agreement, updating the front-end in an appropriate way."""
        
        match.gui.finish_game(_("Draw agreement."))
        
    def make_draw_claim_accepted_handler(self, match):
        """Return a handler with an implicit parameter 'match'
        
        match -- a 'Match' object containing the information relevant to the related match.
        """
        return lambda stanza: self.draw_claim_accepted(stanza, match)
    def draw_claim_accepted(self, stanza, match):
        """Handle the acceptance as legit of a draw claim, updating the front-end in an appropriate way."""
        
        if match.game.board.check_threefold_repetition(match.game.moves, match.game.initial_board()):
            match.gui.finish_game(_("Draw claimed. Threefold repetition rule apply."))
        elif match.game.board.check_fifty_move():
            match.gui.finish_game(_("Draw claimed. Fifty moves rule apply."))
        else:
            logging.getLogger("chessEngine").error("Unrecognition of the condition for our own draw claim.")

    def process_local_turn_action(self, action):
        """Process a 'local turn action' as returned from the front-end.
        
        action -- Dictionary containing the infor neccesary to define the action (which is game-specific and
            whose formet is simply agreed between this module and the front-end).
        """
        
        if not self.activeMatches.has_key(action["match-id"]):
            logging.getLogger("chessEngine").error("No such match is currently tracked.")
        else:
            logging.getLogger("chessEngine").debug("Action: '%s'", action)
            match = self.activeMatches[action["match-id"]]
            opponentJid = self.get_opponent_jid(match)
            
            if action["action"]=="movement":
                logging.getLogger("chessEngine").debug("From: %s,%s  To: %s,%s", action["from"][0], action["from"][1], action["to"][0], action["to"][1])
                move = Move(Coord(action["from"][0], action["from"][1]), Coord(action["to"][0], action["to"][1]))
                
                iqStanza = pyxmpp.iq.Iq(None, None, opponentJid, "set", None)
                turnNode = iqStanza.new_query("jubatu:games", "turn")
                
                turnNode.setProp("engine-id", self.id())
                turnNode.setProp("match-id", action["match-id"])
                
                moveNode = turnNode.newChild(None, "move", None)
                pos = u"%d,%d;%d,%d" % (action["from"][0],action["from"][1],+action["to"][0],+action["to"][1])
                moveNode.setProp("pos", pos)
                moveNode.setProp("ordinal", unicode(match.game.board.move_count))
                
                try:
                    self.move(match, move)
                    
                    logging.getLogger("chessEngine").debug("Draw proposal or claim: '%s'", action["draw proposal or claim"])
                    res_handler = self.res_local_turn
                    if action["draw proposal or claim"] is True:
                        if match.game.board.check_threefold_repetition(match.game.moves, match.game.initial_board()):
                            turnNode.newChild(None, "draw-claim", "threefold repetition rule")
                            res_handler = self.make_res_claim_draw(match)
                        elif match.game.board.check_fifty_move():
                            turnNode.newChild(None, "draw-claim", "fifty moves rule")
                            res_handler = self.make_res_claim_draw(match)
                        else:
                            turnNode.newChild(None, "draw-proposal", None)
                    
                    logging.getLogger("chessEngine").debug("Sending 'turn' stanza:\n%s", iqStanza.serialize())
                    
                    wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, res_handler, self.err_local_turn, self.timeout_local_turn, 30))
                except LackPromotion:
                    match.stanzaWithoutPromotion = iqStanza
                    
            elif action["action"]=="promotion":
                move = match.moveWithoutPromotion
                iqStanza = match.stanzaWithoutPromotion
                
                move.promote = BACKEND_PIECES[action["piece"]]
                # create the "promotion" node parented to the "move" node
                iqStanza.get_query().children.newChild(None, "promotion", action["piece"])
                logging.getLogger("chessEngine").debug("Sending 'turn' stanza:\n%s", iqStanza.serialize())
                
                try:
                    self.move(match, move)
                    wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, self.res_local_turn, self.err_local_turn, self.timeout_local_turn, 30))
                except LackPromotion:
                    logging.getLogger("chessEngine").error("Lack of promotion piece detected just when that is what supposedly we were reporting about.")
            elif action["action"]=="resign":
                iqStanza = pyxmpp.iq.Iq(None, None, opponentJid, "set", None)
                turnNode = iqStanza.new_query("jubatu:games", "turn")
            
                turnNode.setProp("engine-id", self.id())
                turnNode.setProp("match-id", action["match-id"])
                
                resignNode = turnNode.newChild(None, "resign", None)

                logging.getLogger("chessEngine").debug("Sending 'turn' stanza:\n%s", iqStanza.serialize())
                
                wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, self.make_res_resign(match), self.err_local_turn, self.timeout_local_turn, 30))
            elif action["action"]=="accept draw":
                iqStanza = pyxmpp.iq.Iq(None, None, opponentJid, "set", None)
                turnNode = iqStanza.new_query("jubatu:games", "turn")
            
                turnNode.setProp("engine-id", self.id())
                turnNode.setProp("match-id", action["match-id"])
                
                acceptNode = turnNode.newChild(None, "accept-draw", None)
                
                logging.getLogger("chessEngine").debug("Sending 'turn' stanza:\n%s", iqStanza.serialize())
                wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, self.make_res_accept_draw(match), self.err_local_turn, self.timeout_local_turn, 30))
            elif action["action"]=="decline draw":
                if self.get_local_colour(match)==("white","black")[match.game.board.get_turn()]:
                    self.give_turn(match)
                else:   # this shouldn't happen
                    logging.getLogger("chessEngine").error("Draw declination out of turn.")
            elif action["action"]=="claim draw":
                iqStanza = pyxmpp.iq.Iq(None, None, opponentJid, "set", None)
                turnNode = iqStanza.new_query("jubatu:games", "turn")

                turnNode.setProp("engine-id", self.id())
                turnNode.setProp("match-id", action["match-id"])
                
                if match.game.board.check_threefold_repetition(match.game.moves, match.game.initial_board()):
                    turnNode.newChild(None, "draw-claim", "threefold repetition rule")
                elif match.game.board.check_fifty_move():
                    turnNode.newChild(None, "draw-claim", "fifty moves rule")
                else:
                    logging.getLogger("chessEngine").error("Unrecognized condition for claiming draw.")
                    return
                
                wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanza(iqStanza, self.make_res_claim_draw(match), self.err_local_turn, self.timeout_local_turn, 30))

    def process_remote_turn(self, stanza):
        """Process a 'turn' stanza received from our adversary.
        
        stanza -- the iq stanza containing the information about our adversary's actions.
        """
        
        reply=stanza.make_result_response()     # default response: we accept the opponent turn action
        #wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanzaReply(reply))
        
        turnPayload = stanza.get_query()
        logging.getLogger("chessEngine").debug(turnPayload.serialize())
        match_id = turnPayload.prop("match-id")
        if self.activeMatches.has_key(match_id):
            match = self.activeMatches[match_id]
            action = turnPayload.children   # first node of the list of children
            while(action):
                if action.name=="move":
                    logging.getLogger("chessEngine").debug("front-end's 'pos': %s", action.prop("pos"))
                    fromPos, toPos = action.prop("pos").split(";")
                    row, col = fromPos.split(",")
                    fromCoord = Coord(int(row), int(col))
                    row, col = toPos.split(",")
                    toCoord = Coord(int(row), int(col))
                    
                    move = Move(fromCoord, toCoord)
                    subAction = action.children
                    if subAction and subAction.name=="promotion":
                        move.promote = BACKEND_PIECES[subAction.content]
                    logging.getLogger("chessEngine").debug("Move: %s", move)
                    # do move, and check whether it's a legal move
                    if not self.move(match, move):
                        reply=stanza.make_error_response("not-allowed")
                        
                    logging.getLogger("chessEngine").debug(match.game.board)
                    if match.game.board.check_result() == ONGOING:
                        self.give_turn(match)
                        
                        #action = action.next
                        if action.next:
                            if action.next.name=="draw-proposal":
                                action = action.next
                                match.gui.request_draw_proposal_answer()
                elif action.name=="resign":
                    self.game_resigned(stanza, match)
                elif action.name=="accept-draw":
                    self.draw_agreement(stanza, match)
                elif action.name=="draw-claim":
                    logging.getLogger("chessEngine").debug("Front-end's draw claim: %s", action.serialize())
                    # if the opponent can not claim draw according to the rules, return an error response
                    if action.content=="threefold repetition rule":
                        if not match.game.board.check_threefold_repetition(match.game.moves, match.game.initial_board()):
                            reply=stanza.make_error_response("not-allowed")
                        else:
                            self.draw_claim_accepted(stanza, match)
                    elif action.content=="fifty moves rule":
                        if not match.game.board.check_fifty_move():
                            reply=stanza.make_error_response("not-allowed")
                        else:
                            self.draw_claim_accepted(stanza, match)
                    else:
                        logging.getLogger("chessEngine").error("Unrecognized condition for claiming draw.")
                      
                action = action.next        # next node in the list of children
        else:
            logging.getLogger("chessEngine").warning("Received turn not corresponding to any active match.")
            
        # send our response
        wx.GetApp().xmppThread.commandsQueue.put(commands.JuXmppSendIqStanzaReply(reply))
        
    def process_command(self, command):
        """Process a given command.
        
        command -- The command to be processed.
        This will be called at some point during the iteration of the engine loop if there are commands
        in the commands' queue pending of be processed.
        """
        
        if command.id==commands.JU_XMPP_REC_IQ_STANZA:
            logging.getLogger("chessEngine").debug(command.stanza.serialize())
            payload = command.stanza.get_query()
            if command.stanza.get_type()=="set":
                if payload.name=="proposal":
                    self.remote_proposal_received(command.stanza)
                elif payload.name=="turn":
                    self.process_remote_turn(command.stanza)
            elif (command.stanza.get_type()=="result") or (command.stanza.get_type()=="error"):
                if command.handler is not None:
                    command.handler(command.stanza)
                else:
                    logging.getLogger("chessEngine").error("No handler attached to a reply command.")
        elif command.id==commands.JU_USER_ANSWER:
            logging.getLogger("chessEngine").debug("User answer received.")
            if command.attachedObject.get_query().name=="proposal":
                self.proposal_answered_by_local_player(command.attachedObject, command.answer)
        elif command.id==commands.JU_LOCAL_TURN_ACTION:
            self.process_local_turn_action(command.action)
            


class LackPromotion:
    """Helper class used as a signal internal to the module."""
    pass
    
gameEngine = ChessEngine()      # Main instance of the engine; will be accesed externally by the main program.
