import sqlalchemy
import threading
from sqlalchemy.sql.expression import func
import random
from application import Cards, application

'''Simulate average prices for packs'''


def sum_prices():
    pack_code = 'tmp'
    normal_sets = ['lea', 'leb', '2ed', 'ced', 'cei', 'arn', 'atq', '3ed', 'leg', 'sum', 'drk', 'fem', '4ed', 'ice',
                   'chr', 'rin', 'ren', 'hml', 'ptc', 'all', 'mir', 'itp', 'vis', '5ed', 'por', 'wth', 'tmp']
    token_sets = []
    promo_sets = ['pmei', 'pvan', 'olep']
    set_cards = Cards.query.filter(Cards.set == pack_code)
    cards = []

    if pack_code in normal_sets:
        '''NORMAL PACK'''
        common_cards = set_cards.filter_by(rarity='common').order_by(func.random()).limit(10).all()
        uncommon_cards = set_cards.filter_by(rarity='uncommon').order_by(func.random()).limit(4).all()
        rare_cards = []
        mythic_cards = []
        serialized_card = []
        if random.random() <= 0.875:
            rare_cards = set_cards.filter_by(rarity='rare').order_by(func.random()).limit(1).all()
            if not rare_cards:
                rare_cards = set_cards.filter_by(rarity='uncommon').order_by(func.random()).limit(1).all()
        else:
            if random.random() > 0.001:
                mythic_cards = set_cards.filter(Cards.rarity == 'mythic') \
                    .filter(sqlalchemy.not_(Cards.promo_types.contains('serialized'))) \
                    .order_by(func.random()).limit(1).all()
                if not mythic_cards:
                    rare_cards = set_cards.filter_by(rarity='rare').order_by(func.random()).limit(1).all()
                if not rare_cards:
                    rare_cards = set_cards.filter_by(rarity='uncommon').order_by(func.random()).limit(1).all()
            else:
                serialized_card = set_cards.filter(Cards.promo_types.contains('serialized')).order_by(
                    func.random()).limit(1).all()
                if not serialized_card:
                    serialized_card = set_cards.filter_by(rarity='mythic').order_by(func.random()).limit(1).all()
                if not serialized_card:
                    serialized_card = set_cards.filter_by(rarity='rare').order_by(func.random()).limit(1).all()
                if not serialized_card:
                    serialized_card = set_cards.filter_by(rarity='uncommon').order_by(func.random()).limit(1).all()

        cards = common_cards + uncommon_cards + rare_cards + mythic_cards + serialized_card

    elif pack_code in promo_sets:
        '''PROMO PACK'''
        co_un_ra_cards = set_cards.filter((Cards.rarity == 'common') | (Cards.rarity == 'uncommon') |
                                          (Cards.rarity == 'rare')).order_by(func.random()).limit(5).all()

        mythic_cards = set_cards.filter_by(rarity='mythic').order_by(func.random()).limit(3).all()
        if not mythic_cards:
            mythic_cards = set_cards.filter_by(rarity='rare').order_by(func.random()).limit(3).all()

        cards = co_un_ra_cards + mythic_cards

    elif pack_code in token_sets:
        '''TOKEN PACK'''
        cards = set_cards.order_by(func.random()).limit(3).all()

    total_price = 0.0
    for card in cards:
        total_price += float(card.price)
    return round(total_price, 2)


def simulate(n):
    trials = []
    for i in range(n):
        with application.app_context():
            trials.append(sum_prices())
    print(f'simulate: {sum(trials) / n}')


t1 = threading.Thread(target=simulate, args=(10000,))
t2 = threading.Thread(target=simulate, args=(10000,))
t3 = threading.Thread(target=simulate, args=(10000,))
t4 = threading.Thread(target=simulate, args=(10000,))
t5 = threading.Thread(target=simulate, args=(10000,))

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()

print('Done')
