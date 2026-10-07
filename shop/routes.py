import hmac
import json
import os
import re
from pathlib import Path

from flask import Response, abort, jsonify, render_template, request

from shop import app, config, db, kaspi
from shop.i18n import JS_KEYS, TEXTS
from shop.models import Order

PHOTO_DIR = Path(app.static_folder) / "images" / "photos"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def photos():
    """Real product photos dropped into static/images/photos/, sorted by name."""
    if not PHOTO_DIR.is_dir():
        return []
    return sorted(f"images/photos/{p.name}" for p in PHOTO_DIR.iterdir() if p.suffix.lower() in PHOTO_EXTENSIONS)


def render(template, lang, **context):
    t = TEXTS[lang]
    return render_template(
        template,
        lang=lang,
        t=t,
        texts=TEXTS,
        cfg=config,
        brand=config.BRAND,
        price=config.format_tenge,
        **context,
    )


def landing(lang):
    t = TEXTS[lang]
    js = {
        "lang": lang,
        "priceOne": config.PRICE_ONE,
        "priceTwo": config.PRICE_TWO,
        "maxQuantity": config.MAX_QUANTITY,
        "t": {key: t[key] for key in JS_KEYS},
    }
    return render("landing.html", lang, photos=photos(), js=js)


@app.route("/")
def index():
    return landing(config.DEFAULT_LANGUAGE)


@app.route("/<any(ru, en):lang>")
def index_lang(lang):
    return landing(lang)


def normalize_phone(raw):
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits[0] in "78":
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return "+7" + digits


@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    lang = data.get("lang") if data.get("lang") in config.LANGUAGES else config.DEFAULT_LANGUAGE
    t = TEXTS[lang]

    items = {}
    for color, qty in (data.get("items") or {}).items():
        if color in config.COLORS and isinstance(qty, int) and qty > 0:
            items[color] = qty
    quantity = sum(items.values())
    if quantity < 1 or quantity > config.MAX_QUANTITY:
        return jsonify(error=t["err_items"]), 400

    fields = {key: str(data.get(key) or "").strip() for key in ("name", "phone", "city", "address")}
    if not all(fields.values()) or any(len(v) > 300 for v in fields.values()):
        return jsonify(error=t["err_fields"]), 400
    phone = normalize_phone(fields["phone"])
    if not phone:
        return jsonify(error=t["err_phone"]), 400

    order = Order(
        items=json.dumps(items),
        quantity=quantity,
        total=config.total_price(quantity),
        name=fields["name"][:120],
        phone=phone,
        city=fields["city"][:120],
        address=fields["address"],
        lang=lang,
    )
    db.session.add(order)
    db.session.commit()

    invoice = kaspi.create_invoice(
        amount=order.total,
        product_name=f"{config.BRAND} MagSafe card holder × {quantity}",
        account=str(order.id),
    )
    if not invoice or not invoice.get("paymentUrl"):
        return jsonify(error=t["err_payment"]), 502

    order.invoice_id = invoice.get("_id")
    order.payment_url = invoice["paymentUrl"]
    db.session.commit()
    return jsonify(order_url=f"/order/{order.token}", payment_url=order.payment_url)


def get_order(token):
    order = Order.query.filter_by(token=token).first()
    if not order:
        abort(404)
    return order


def refresh_status(order):
    if order.status != "paid" and order.invoice_id and kaspi.invoice_is_paid(order.invoice_id):
        order.mark_paid()
        db.session.commit()


@app.route("/order/<token>")
def order_page(token):
    order = get_order(token)
    refresh_status(order)
    lang = request.args.get("lang", order.lang)
    if lang not in config.LANGUAGES:
        lang = order.lang
    return render("order.html", lang, order=order)


@app.route("/api/order/<token>/status")
def order_status(token):
    order = get_order(token)
    refresh_status(order)
    return jsonify(status=order.status)


@app.route("/kaspi_webhook", methods=["POST"])
def kaspi_webhook():
    if not kaspi.webhook_is_authentic(request.headers):
        return "Unauthorized", 401
    data = request.get_json(silent=True) or {}
    order = Order.query.filter_by(invoice_id=str(data.get("invoiceId", ""))).first()
    if not order:
        return "Order not found", 404
    try:
        paid_sum = int(float(data.get("sum", 0)))
    except (TypeError, ValueError):
        paid_sum = 0
    if paid_sum < order.total:
        app.logger.warning("Order %s: paid %s < total %s", order.id, paid_sum, order.total)
        return "Wrong amount", 400
    order.mark_paid()
    db.session.commit()
    return "OK", 200


@app.route("/admin")
def admin():
    """Order list for the seller. Basic auth with ADMIN_PASSWORD (any username)."""
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        abort(404)
    auth = request.authorization
    if not auth or not hmac.compare_digest(auth.password or "", password):
        return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="admin"'})
    orders = Order.query.order_by(Order.created_at.desc()).limit(500).all()
    return render("admin.html", "ru", orders=orders)
