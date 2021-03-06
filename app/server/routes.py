"""server routes"""
import json
import time

from flask import request, jsonify, make_response

from app import APP

from .attack_service import ArmyAttackService
from .join_service import ArmyJoinService
from .utils import calculate_reload_time, validate_army_access_token
from .webhooks import WebhookService



@APP.route('/starwars/api/join', methods=['POST'])
@calculate_reload_time
def join(reload_time):
    """
    Join army route
    """
    request_json = request.get_json()
    access_token = request.args.get('accessToken')
    join_service = ArmyJoinService(access_token, request_json)

    errors = join_service.validate_army_create()
    if errors:
        return jsonify({"errors": errors}), 400

    army = join_service.create()

    result = join_service.create_join_response(army)

    response = make_response(json.dumps(result), 200)
    response.mimetype = "application/json"

    time.sleep(reload_time)
    return response


@APP.route('/starwars/api/attack/<int:army_id>', methods=['PUT'])
@validate_army_access_token
@calculate_reload_time
def attack(attack_army, army_id, reload_time):
    """
    Attack army route
    """
    attack_service = ArmyAttackService(attack_army)

    # check if army exists
    defence_army = attack_service.get_defence_army(army_id)
    if defence_army is None or defence_army.status != 'alive':
        return jsonify({"error": "army not found or dead"}), 404

    if attack_army.in_battle == 1:
        return jsonify({"error": "you are already in active battle"}), 400
    if attack_army.status != 'alive':
        return jsonify({"error": "only alive armys can attack"}), 400

    # saving battle in the db
    battle = attack_service.create()

    # repeating the battle until success or max number of retries is reached
    for _ in range(attack_army.number_squads):
        with attack_service:
            response = attack_service.attack(battle)
            time.sleep(reload_time)
            if response == 'success':
                return 'success'
            elif response == 'max num of attacks reached':
                return jsonify({"error": "your reched the max num of attacks"}), 429

    return 'fail'


@APP.route('/starwars/api/leave', methods=['POST'])
@validate_army_access_token
@calculate_reload_time
def leave(army, reload_time):
    """
    Leave army route
    """
    webhook_service = WebhookService()

    if army.status == 'left':
        return jsonify({"error": "you already left the game"}), 200

    army.leave(leave_type='left')

    # trigger army.leave webhook
    webhook_service.create_army_leave_webhook(army, leave_type='left')

    time.sleep(reload_time)

    return jsonify({"success": "you have left the game"}), 200
