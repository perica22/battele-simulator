"""Database Model"""
from uuid import uuid1

from app import DB



def generate_hash():
    '''
    This is generating hash for Army model
    '''
    token_hash = str(uuid1())
    return token_hash


class Army(DB.Model):
    """
    Army table model
    """
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True, unique=True)
    name = DB.Column(DB.String(64))
    number_squads = DB.Column(DB.Integer)
    webhook_url = DB.Column(DB.String(120))
    access_token = DB.Column(DB.String(120), default=lambda: generate_hash(), unique=True)
    status = DB.Column(DB.String(64), default='alive')
    join_type = DB.Column(DB.String(64), default='new')
    in_battle = DB.Column(DB.Integer, default=0)

    def __repr__(self):
        return '<Army {}>'.format(self.name)

    def leave(self, leave_type):
        """
        Changing leave status of army
        Args:
            leave_type: in case army left the battle or died
        """
        self.status = leave_type

    def join_type_update(self):
        """Changing join_type of army"""
        self.join_type = 'returned'

    def is_in_active_battle(self):
        """Changing battle status for army which is attacking"""
        if self.in_battle == 1:
            self.in_battle = 0
        else:
            self.in_battle = 1

    def set_defence_army_number_squads(self, damage):
        """Changing number of squads for defeated army"""
        self.number_squads = self.number_squads - damage


class Battle(DB.Model):
    """
    Battle table model
    """
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    attack_army_id = DB.Column(DB.Integer)
    attack_army_name = DB.Column(DB.String(64))
    attack_army_number_squads = DB.Column(DB.Integer)
    defence_army_id = DB.Column(DB.Integer)
    defence_army_name = DB.Column(DB.String(64))
    defence_army_number_squads = DB.Column(DB.Integer)
    defence_army_numer_squads_after = DB.Column(DB.Integer)
    num_of_attacks = DB.Column(DB.Integer)

    def __repr__(self):
        return '<Battle {} - {}'.format(self.attack_army_name, self.defence_army_name)

    def after_battle_update(self, num_of_attacks, damage):
        """Updating battle data after successful battle"""
        self.num_of_attacks = num_of_attacks
        self.defence_army_numer_squads_after = self.defence_army_number_squads - damage
