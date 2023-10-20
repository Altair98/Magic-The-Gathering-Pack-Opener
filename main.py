import sqlalchemy
import os
from sqlalchemy import desc
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from sqlalchemy.sql import text
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap5(app)
db = SQLAlchemy(app)

'''TABLE MODELS'''


class Cards(db.Model):
    id = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    released_at = db.Column(db.String, nullable=False)
    image_uris = db.Column(db.String, nullable=False)
    color_identity = db.Column(db.String, nullable=True)
    set_id = db.Column(db.String, nullable=False)
    set = db.Column(db.String, nullable=False)
    set_name = db.Column(db.String, nullable=False)
    set_type = db.Column(db.String, nullable=False)
    collector_number = db.Column(db.String, nullable=False)
    rarity = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    border_color = db.Column(db.String, nullable=False)
    frame = db.Column(db.String, nullable=False)
    frame_effects = db.Column(db.String, nullable=False)
    full_art = db.Column(db.Boolean, nullable=False)
    promo_types = db.Column(db.String, nullable=True)
    card_faces = db.Column(db.String, nullable=True)
    price = db.Column(db.String, nullable=True)
    price_foil = db.Column(db.String, nullable=True)


class Sets(db.Model):
    id = db.Column(db.String, primary_key=True, nullable=False)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    released_at = db.Column(db.String, nullable=False)
    set_type = db.Column(db.String, nullable=False)
    card_count = db.Column(db.BigInteger, nullable=False)
    icon_svg_uri = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/data", methods=['GET', 'POST'])
def data():
    global owned_cards, inventory_packs, inventory_cards
    data_dic = request.get_json()
    owned_cards = data_dic['owned_cards']
    inventory_packs = data_dic['inventory_packs']
    inventory_cards = data_dic['inventory_cards']
    return data_dic


@app.route("/currency")
def currency():
    return render_template("money.html")


@app.route("/pack_shop", methods=['POST', 'GET'])
def pack_shop():
    sets = Sets.query.order_by(Sets.name).all()
    if request.method == 'POST':
        if 'Filter' in request.form:
            name_search = request.form.get("name_search")
            set_type = request.form.get("settype_dropdown")
            sort_by = request.form.get("sort_dropdown")
            if set_type is None and sort_by is None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)).order_by(Sets.name)
                sets = query_filter

            elif sort_by is None and set_type is not None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)) \
                    .filter(Sets.set_type == set_type).order_by(Sets.name)
                sets = query_filter

            elif set_type is None and sort_by is not None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)).order_by(text(sort_by))
                sets = query_filter

            else:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)) \
                    .filter(Sets.set_type == set_type).order_by(text(sort_by))
                sets = query_filter

        if 'Reset' in request.form:
            sets = Sets.query.order_by(Sets.name).all()

    return render_template("pack_shop.html", sets=sets)


@app.route("/inventory", methods=['POST', 'GET'])
def inventory():
    global inventory_packs, inventory_cards, owned_cards

    cards = [Cards.query.filter_by(id=id).one() for id in inventory_cards]
    sets = [Sets.query.filter_by(code=code).one() for code in inventory_packs]

    if request.method == 'POST':
        if 'Filter_cards' in request.form:
            name_search = request.form.get("name_search")
            artist_search = request.form.get("artist_search")
            rarity = request.form.get("rarity_dropdown")
            if rarity is None:
                cards = []
                for i in inventory_cards:
                    card = Cards.query.filter(Cards.id == i).filter(Cards.name.contains(name_search))\
                                                .filter(Cards.artist.contains(artist_search)).first()
                    if card is not None:
                        cards.append(card)

            elif rarity is not None:
                cards = []
                for i in inventory_cards:
                    card = Cards.query.filter(Cards.id == i).filter(Cards.name.contains(name_search))\
                                                .filter(Cards.artist.contains(artist_search))\
                                                .filter(Cards.rarity == rarity).first()
                    if card is not None:
                        cards.append(card)

        if 'Reset_cards' in request.form:
            cards = [Cards.query.filter_by(id=id).one() for id in inventory_cards]

        if 'Filter_packs' in request.form:
            set_name_search = request.form.get("name_search")
            set_type = request.form.get("settype_dropdown")
            if set_type is None:
                sets = []
                for i in inventory_packs:
                    pack = Sets.query.filter(Sets.code == i).filter(Sets.name.contains(set_name_search)).first()
                    if pack is not None:
                        sets.append(pack)

            elif set_type is not None:
                sets = []
                for i in inventory_packs:
                    pack = Sets.query.filter(Sets.code == i).filter(Sets.name.contains(set_name_search))\
                        .filter(Sets.set_type == set_type).first()
                    if pack is not None:
                        sets.append(pack)

        if 'Reset_packs' in request.form:
            sets = [Sets.query.filter_by(code=code).one() for code in inventory_packs]

    return render_template("inventory.html", cards=cards, sets=sets, owned_cards=owned_cards)


@app.route("/open/<pack_code>")
def open_pack(pack_code):
    global inventory_packs

    normal_sets = ['lea', 'leb', '2ed', 'ced', 'cei', 'arn', 'atq', '3ed', 'leg', 'sum', 'drk', 'fem', '4ed', 'ice',
                   'chr', 'rin', 'ren', 'hml', 'ptc', 'all', 'mir', 'itp', 'vis', '5ed', 'por', 'wth', 'tmp']
    token_sets = []
    promo_sets = ['pmei', 'pvan', 'olep']
    set_cards = Cards.query.filter(Cards.set == pack_code)
    cards = []

    if pack_code in inventory_packs:
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

        return render_template("open.html", cards=cards, pack_code=pack_code)

    elif pack_code not in inventory_packs:

        return redirect(url_for('inventory'))


@app.route("/collection", methods=['POST', 'GET'])
def collection():
    global owned_cards
    cards = Cards.query.all()
    sets = Sets.query.order_by(Sets.name).all()
    if request.method == 'POST':
        if 'Filter' in request.form:
            name_search = request.form.get("name_search")
            set_type = request.form.get("settype_dropdown")
            sort_by = request.form.get("sort_dropdown")
            if set_type is None and sort_by is None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)).order_by(Sets.name)
                sets = query_filter

            elif sort_by is None and set_type is not None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)) \
                    .filter(Sets.set_type == set_type).order_by(Sets.name)
                sets = query_filter

            elif set_type is None and sort_by is not None:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)).order_by(text(sort_by))
                sets = query_filter

            else:
                query_filter = Sets.query.filter(Sets.name.contains(name_search)) \
                    .filter(Sets.set_type == set_type).order_by(text(sort_by))
                sets = query_filter

        if 'Reset' in request.form:
            sets = Sets.query.order_by(Sets.name).all()

    '''function to count owned cards by set'''
    def set_owned(set_code):
        cards = Cards.query.all()
        set_ids = []
        for card in cards:
            if card.set == set_code:
                set_ids.append(card.id)

        count = 0
        for card in owned_cards:
            if card in set_ids:
                count += 1

        return count

    return render_template("collection.html", sets=sets, owned_cards=owned_cards, cards=cards, set_owned=set_owned)


@app.route("/collection/<setname>", methods=['POST', 'GET'])
def collection_cards(setname):
    global owned_cards
    cards = Cards.query.filter(Cards.set_name == setname)
    if request.method == 'POST':
        if 'Filter' in request.form:
            name_search = request.form.get("name_search")
            artist_search = request.form.get("artist_search")
            rarity = request.form.get("rarity_dropdown")
            sort_by = request.form.get("sort_dropdown")
            if rarity is None and sort_by is None:
                query_filter = Cards.query.filter(Cards.name.contains(name_search)) \
                    .filter(Cards.artist.contains(artist_search)) \
                    .filter(Cards.set_name == setname)
                cards = query_filter

            elif rarity is not None and sort_by is None:
                query_filter = Cards.query.filter(Cards.name.contains(name_search)) \
                    .filter(Cards.artist.contains(artist_search)) \
                    .filter(Cards.set_name == setname) \
                    .filter(Cards.rarity == rarity)
                cards = query_filter

            elif sort_by is not None and rarity is None:
                query_filter = Cards.query.filter(Cards.name.contains(name_search)) \
                    .filter(Cards.artist.contains(artist_search)) \
                    .filter(Cards.set_name == setname).order_by(text(sort_by))
                cards = query_filter

            else:
                query_filter = Cards.query.filter(Cards.name.contains(name_search)) \
                    .filter(Cards.artist.contains(artist_search)) \
                    .filter(Cards.set_name == setname) \
                    .filter(Cards.rarity == rarity).order_by(text(sort_by))
                cards = query_filter

        if 'Reset' in request.form:
            cards = Cards.query.filter(Cards.set_name == setname)

    return render_template("collection_cards.html", cards=cards, setname=setname, owned_cards=owned_cards)


'''
    Sets that may be updated: 
    - Media Insterts pmei 50
'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)
