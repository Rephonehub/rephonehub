import os, asyncio, random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_NEW_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # <-- Put your Telegram ID here

# Crypto - Put your REAL wallet here, bot will show it to buyer
USDT_WALLET = os.getenv("USDT_WALLET", "YOUR_USDT_TRC20_WALLET_HERE")
BTC_WALLET = os.getenv("BTC_WALLET", "YOUR_BTC_WALLET_HERE")

# Stripe - Create Payment Links in Stripe Dashboard and paste here
STRIPE_LINKS = {
    "default": "https://buy.stripe.com/your-link"
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# PRODUCTS - Price is ALREADY 20% OFF Back Market price
PRODUCTS = [
    {"id": "ip11_64_good", "name": "iPhone 11", "storage": "64GB", "grade": "Good", "battery": "86%", "color": "Black", "market": 179, "price": 143, "stock": 8, "sold_today": 12},
    {"id": "ip12_128_good", "name": "iPhone 12", "storage": "128GB", "grade": "Good", "battery": "87%", "color": "Blue", "market": 259, "price": 207, "stock": 6, "sold_today": 18},
    {"id": "ip12pro_128_good", "name": "iPhone 12 Pro", "storage": "128GB", "grade": "Good", "battery": "88%", "color": "Gold", "market": 329, "price": 263, "stock": 5, "sold_today": 9},
    {"id": "ip13_128_exc", "name": "iPhone 13", "storage": "128GB", "grade": "Excellent", "battery": "93%", "color": "Blue", "market": 339, "price": 271, "stock": 3, "sold_today": 27},
    {"id": "ip13_128_good", "name": "iPhone 13", "storage": "128GB", "grade": "Good", "battery": "89%", "color": "Starlight", "market": 299, "price": 239, "stock": 7, "sold_today": 15},
    {"id": "ip14_128_exc", "name": "iPhone 14", "storage": "128GB", "grade": "Excellent", "battery": "94%", "color": "Purple", "market": 429, "price": 343, "stock": 4, "sold_today": 11},
    {"id": "ip14pro_256_exc", "name": "iPhone 14 Pro", "storage": "256GB", "grade": "Excellent", "battery": "95%", "color": "Deep Purple", "market": 599, "price": 479, "stock": 2, "sold_today": 7},
    {"id": "s21_128_good", "name": "Samsung Galaxy S21", "storage": "128GB", "grade": "Good", "battery": "85%", "color": "Gray", "market": 199, "price": 159, "stock": 9, "sold_today": 8},
    {"id": "s22_128_exc", "name": "Samsung Galaxy S22", "storage": "128GB", "grade": "Excellent", "battery": "91%", "color": "White", "market": 279, "price": 223, "stock": 2, "sold_today": 14},
    {"id": "s22u_256_exc", "name": "Samsung Galaxy S22 Ultra", "storage": "256GB", "grade": "Excellent", "battery": "90%", "color": "Black", "market": 399, "price": 319, "stock": 3, "sold_today": 6},
    {"id": "pixel7_128_exc", "name": "Google Pixel 7", "storage": "128GB", "grade": "Excellent", "battery": "92%", "color": "Snow", "market": 239, "price": 191, "stock": 6, "sold_today": 10},
    {"id": "pixel8_128_exc", "name": "Google Pixel 8", "storage": "128GB", "grade": "Excellent", "battery": "94%", "color": "Hazel", "market": 329, "price": 263, "stock": 5, "sold_today": 9},
]

carts = {} # user_id -> product_id
orders = {}

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Shop All Phones - 20% OFF", callback_data="shop")],
        [InlineKeyboardButton(text="🔥 Today's Hot Deals", callback_data="hot")],
        [InlineKeyboardButton(text="💰 Sell Your Phone", callback_data="sell")],
        [InlineKeyboardButton(text="🛡️ Warranty & Returns", callback_data="warranty")],
        [InlineKeyboardButton(text="📦 Track Order", callback_data="track")],
    ])

def product_text(p):
    save = p['market'] - p['price']
    urgency = ""
    if p['stock'] <= 3:
        urgency = f"\n📦 Only {p['stock']} left in {p['grade']} - {p['color']}"
    # Countdown to midnight - REAL timer
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    left = midnight - now
    h, m = divmod(int(left.total_seconds() // 60), 60)
    return (
        f"{p['name']} - {p['storage']} - {p['color']} - Unlocked\n"
        f"Grade: {p['grade']} | Battery: {p['battery']} | IMEI: Clean ✅\n"
        f"Market Price: ${p['market']} ❌\n"
        f"OUR PRICE: ${p['price']} ✅ -20% OFF\n"
        f"You Save ${save} TODAY\n"
        f"⚡ {p['sold_today']} sold in last 24h{urgency}\n"
        f"⏰ 20% OFF ends in {h}h {m}m - Then back to ${p['market']}\n\n"
        f"✅ 1 Year Warranty Included\n"
        f"✅ 30 Days Free Return\n"
        f"✅ Ships From USA - Delivery 2-4 Days"
    )

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "Welcome to **RePhoneHub** - Refurbished Phones 20% Cheaper Than Back Market 🔥\n\n"
        "⚡ TODAY'S HOT DEALS - 20% OFF ENDS TONIGHT\n\n"
        "1. iPhone 13 128GB Excellent - $271 (was $339) - Only 3 left\n"
        "2. iPhone 12 128GB Good - $207 (was $259) - 18 sold today\n"
        "3. Samsung S22 Excellent - $223 (was $279) - Only 2 left\n\n"
        "**HOW TO BUY:**\n"
        "1. Tap phone you want\n"
        "2. Choose Grade + Color\n"
        "3. Tap Buy Now\n"
        "4. Pay with Card / Crypto\n"
        "5. Enter address - Get tracking in 24h",
        reply_markup=main_kb(), parse_mode="Markdown"
    )

@dp.callback_query(F.data == "shop")
async def shop(c: types.CallbackQuery):
    kb = []
    for p in PRODUCTS:
        kb.append([InlineKeyboardButton(text=f"{p['name']} {p['storage']} {p['grade']} - ${p['price']} (was ${p['market']})", callback_data=f"view_{p['id']}")])
    kb.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back")])
    await c.message.edit_text("📱 Shop All Phones - All Prices 20% OFF - USD\n\nTap a phone to see details:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "hot")
async def hot(c: types.CallbackQuery):
    hot_items = sorted(PRODUCTS, key=lambda x: x['sold_today'], reverse=True)[:3]
    text = "🔥 TODAY'S HOT DEALS - Fast Moving:\n\n"
    kb = []
    for p in hot_items:
        text += f"{p['name']} {p['storage']} {p['grade']} - ${p['price']} - {p['sold_today']} sold today - Only {p['stock']} left\n\n"
        kb.append([InlineKeyboardButton(text=f"Buy {p['name']} - ${p['price']}", callback_data=f"view_{p['id']}")])
    kb.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back")])
    await c.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("view_"))
async def view(c: types.CallbackQuery):
    pid = c.data.replace("view_", "")
    p = next(x for x in PRODUCTS if x['id'] == pid)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"⚡ Buy Now - ${p['price']}", callback_data=f"buy_{pid}")],
        [InlineKeyboardButton(text="➕ Add Bundle Case+Glass+Charger $29", callback_data=f"bundle_{pid}")],
        [InlineKeyboardButton(text="⬅️ Back to Shop", callback_data="shop")],
    ])
    await c.message.edit_text(product_text(p), reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def buy(c: types.CallbackQuery):
    pid = c.data.replace("buy_", "")
    p = next(x for x in PRODUCTS if x['id'] == pid)
    carts[c.from_user.id] = pid
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pay With Card (Stripe)", callback_data=f"pay_card_{pid}")],
        [InlineKeyboardButton(text="₿ Pay With Crypto (USDT / BTC)", callback_data=f"pay_crypto_{pid}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"view_{pid}")],
    ])
    await c.message.edit_text(
        f"You picked: {p['name']} {p['storage']} {p['grade']} - ${p['price']} USD\n\n"
        f"Choose Payment:\n\n"
        f"💳 Card - Secure Stripe link, Apple Pay / Visa / Mastercard\n"
        f"₿ Crypto - USDT (TRC20) or BTC - Manual confirmation\n\n"
        f"Next: After payment, send your Full Name + Address + ZIP",
        reply_markup=kb
    )

@dp.callback_query(F.data.startswith("pay_card_"))
async def pay_card(c: types.CallbackQuery):
    pid = c.data.replace("pay_card_", "")
    p = next(x for x in PRODUCTS if x['id'] == pid)
    order_id = f"RPH-{random.randint(10000,99999)}"
    await c.message.edit_text(
        f"✅ Order {order_id} Created\n"
        f"Product: {p['name']} {p['storage']} - ${p['price']} USD\n\n"
        f"**PAY WITH CARD:**\n"
        f"Click this secure Stripe link to pay:\n{STRIPE_LINKS['default']}\n\n"
        f"After paying, send:\n"
        f"1. Screenshot of payment\n"
        f"2. Full Name\n"
        f"3. Address, City, State, ZIP\n\n"
        f"Tracking in 24h. Delivery 2-4 days. 1 Year Warranty.",
        parse_mode="Markdown"
    )
    try:
        await bot.send_message(ADMIN_ID, f"🆕 NEW CARD ORDER {order_id} - {p['name']} ${p['price']} from @{c.from_user.username} ID {c.from_user.id}")
    except:
        pass

@dp.callback_query(F.data.startswith("pay_crypto_"))
async def pay_crypto(c: types.CallbackQuery):
    pid = c.data.replace("pay_crypto_", "")
    p = next(x for x in PRODUCTS if x['id'] == pid)
    order_id = f"RPH-{random.randint(10000,99999)}"
    orders[order_id] = pid
    await c.message.edit_text(
        f"✅ Order {order_id} Created - Crypto Payment\n"
        f"Product: {p['name']} {p['storage']} - ${p['price']} USD\n\n"
        f"**HOW TO PAY WITH CRYPTO:**\n\n"
        f"1. Send EXACTLY ${p['price']} USD worth of crypto to:\n\n"
        f"USDT (TRC20):\n`{USDT_WALLET}`\n\n"
        f"BTC:\n`{BTC_WALLET}`\n\n"
        f"2. After sending, reply here with:\n"
        f"Order ID: {order_id}\n"
        f"TX Hash / Transaction ID\n"
        f"Full Name + Address + ZIP\n\n"
        f"3. Admin will verify on blockchain and confirm your order. Do NOT send to any other wallet - scammers DM fake wallets.\n\n"
        f"Delivery 2-4 days after confirmation. 1 Year Warranty.",
        parse_mode="Markdown"
    )
    try:
        await bot.send_message(ADMIN_ID, f"🆕 NEW CRYPTO ORDER {order_id} - {p['name']} ${p['price']} from @{c.from_user.username}")
    except:
        pass

@dp.callback_query(F.data == "warranty")
async def warranty(c: types.CallbackQuery):
    await c.message.edit_text("🛡️ RePhoneHub Warranty\n\n✅ 1 Year Warranty - Free repair or replacement\n✅ 30 Days Free Return - No questions\n✅ 50-Point Tested - Battery, Screen, FaceID, Camera, IMEI Clean\n✅ Unlocked - Works Verizon, AT&T, T-Mobile, Mint Mobile\n\nQuestions? Message Admin.", reply_markup=main_kb())

@dp.callback_query(F.data == "sell")
async def sell(c: types.CallbackQuery):
    await c.message.edit_text("💰 Sell Your Phone\n\nSend us:\n1. Photo of phone front + back\n2. Model + Storage + Condition\n3. Your ZIP\n\nWe reply in 10 mins with instant offer. We send prepaid USPS label. You ship, we pay via CashApp / Zelle / Crypto.", reply_markup=main_kb())

@dp.callback_query(F.data == "track")
async def track(c: types.CallbackQuery):
    await c.message.edit_text("📦 Track Order\n\nSend your Order ID like RPH-12345 and we will check tracking for you.", reply_markup=main_kb())

@dp.callback_query(F.data == "back")
async def back(c: types.CallbackQuery):
    await c.message.edit_text("Welcome back to RePhoneHub - 20% OFF 🔥", reply_markup=main_kb())

async def main():
    print("Starting RePhoneHub Bot - USD...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
