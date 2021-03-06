"""Service for handling battle"""
import random

from app import DB
from .models import Battle, Army
from .webhooks import WebhookService
from .utils import Indenter


class ArmyAttackService:
    """
    Battle logic
    Args:
        attack_army: instance of army that attacks
    """
    def __init__(self, attack_army):
        self.attack_army = attack_army
        self.defence_army = None
        self.num_of_attacks = 0
        self.dead = False
        self.webhook_service = WebhookService()

        self.lucky_value = random.randint(1, 100)

    def __enter__(self):
        # tracking number of attacks army is making in one call
        self.num_of_attacks += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_defence_army(self, army_id):
        """Retrieving defence army"""
        self.defence_army = Army.query.filter_by(id=army_id).first()

        return self.defence_army

    def create(self):
        """
        Saving battle to DB
        Returns:
            instance of active battle
        """
        self.attack_army.is_in_active_battle()
    
        battle = Battle(attack_army_id=self.attack_army.id,
                        defence_army_id=self.defence_army.id,
                        attack_army_name=self.attack_army.name,
                        defence_army_name=self.defence_army.name,
                        defence_army_number_squads=self.defence_army.number_squads,
                        attack_army_number_squads=self.attack_army.number_squads,)
        DB.session.add(battle)
        DB.session.commit()

        with Indenter(0) as indent:
            indent.print("{} started".format(str(battle).upper()))

        return battle

    def attack(self, battle):
        """
        Making and etermining if attack was successful
        Args:
            battle: instance of active battle
        Returns:
            string 'success' or 'try_again' used to recognize outcome of attack
        """
        if self.num_of_attacks >= self.attack_army.number_squads:
            self.attack_army.is_in_active_battle()
            DB.session.commit()
            return 'max num of attacks reached'

        attack_value = random.randint(1, 100)

        with Indenter(0) as indent:
            indent.print("lucky_value is {} and {} strikes with {}".format(
                self.lucky_value, self.attack_army.name.upper(), attack_value))

        if attack_value == self.lucky_value:

            with Indenter(1) as indent:
                indent.print("{} attacked successfully".format(self.attack_army.name.upper()))

            # Calculating attack damage
            attack_damage = self._calculate_damage()
            if attack_damage >= self.defence_army.number_squads:
                attack_damage = self.defence_army.number_squads
                self.dead = True
                with Indenter(2) as indent:
                    indent.print("** {} is dead **".format(self.defence_army.name.upper()))

            # Saving changes after successful attack and triggering webhooks
            self._update_armies(attack_damage)
            self._update_battle(battle, attack_damage)
            self._trigger_webhooks()

            return 'success'

        return 'try_again'

    def _calculate_damage(self):
        """Calculating total damage of attack"""
        damage = round(self.attack_army.number_squads / self.num_of_attacks)
        return damage

    def _update_armies(self, attack_damage):
        """
        Updating values in Army table after successful attack
        Args:
            attack_damage: vlaue of damage made to defence army
        """
        DB.session.add(self.defence_army, self.attack_army)
        self.attack_army.is_in_active_battle()
        self.defence_army.set_defence_army_number_squads(attack_damage)
        DB.session.commit()

        with Indenter(1) as indent:
            indent.print("{} has {} squads left".format(
                self.defence_army.name.upper(), self.defence_army.number_squads))

    def _update_battle(self, battle, attack_damage):
        """
        Updating values in Battle table after successful attack
        Args:
            battle: instance of active battle
            attack_damge: vlaue of damage made to defence army
        """
        DB.session.add(battle)
        battle.after_battle_update(self.num_of_attacks, attack_damage)
        DB.session.commit()

    def _trigger_webhooks(self):
        """
        Triggering webhooks:
            - army.update 
            - army.leave(in case army is dead)
        """
        # Triggering army.update webhook
        self.webhook_service.create_army_update_webhook(self.attack_army)
        self.webhook_service.create_army_update_webhook(self.defence_army)

        # army.leave webhook in case army died
        if self.dead:
            self.webhook_service.create_army_leave_webhook(self.defence_army, leave_type='die')
