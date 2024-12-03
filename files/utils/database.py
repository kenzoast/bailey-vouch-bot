import sqlite3

# Connect to the SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('bot_database.db')
c = conn.cursor()

# Initialize the database tables
def init_db():
    c.execute('''
        CREATE TABLE IF NOT EXISTS vouches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            voucher_id INTEGER,
            message TEXT,
            stars INTEGER,
            attachment_url TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            guild_id INTEGER PRIMARY KEY,
            vouch_channel_id INTEGER,
            vouch_role_id INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS embed_settings (
            guild_id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            color TEXT
        )
    ''')

    conn.commit()

def set_embed_setting(guild_id, key, value):
    c.execute('SELECT guild_id FROM embed_settings WHERE guild_id = ?', (guild_id,))
    if c.fetchone():
        c.execute(f'UPDATE embed_settings SET {key} = ? WHERE guild_id = ?', (value, guild_id))
    else:
        c.execute(f'INSERT INTO embed_settings (guild_id, {key}) VALUES (?, ?)', (guild_id, value))
    conn.commit()

def get_embed_settings(guild_id):
    c.execute('SELECT title, description, color FROM embed_settings WHERE guild_id = ?', (guild_id,))
    row = c.fetchone()
    if row:
        return {
            'title': row[0],
            'description': row[1],
            'color': row[2]
        }
    else:
        return {}


def set_vouch_role(guild_id, role_id):
    c.execute('SELECT guild_id FROM config WHERE guild_id = ?', (guild_id,))
    if c.fetchone():
        c.execute('UPDATE config SET vouch_role_id = ? WHERE guild_id = ?', (role_id, guild_id))
    else:
        c.execute('INSERT INTO config (guild_id, vouch_role_id) VALUES (?, ?)', (guild_id, role_id))
    conn.commit()

def get_vouch_role(guild_id):
    c.execute('SELECT vouch_role_id FROM config WHERE guild_id = ?', (guild_id,))
    result = c.fetchone()
    # Since only one column is fetched, result[0] contains the value
    return result[0] if result else None


# Save a vouch to the database
def save_vouch(user_id, voucher_id, message, stars, attachment_url):
    c.execute('''
        INSERT INTO vouches (user_id, voucher_id, message, stars, attachment_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, voucher_id, message, stars, attachment_url))
    conn.commit()

# Set the vouch channel for a guild
def set_vouch_channel(guild_id, channel_id):
    c.execute('''
        INSERT OR REPLACE INTO config (guild_id, vouch_channel_id)
        VALUES (?, ?)
    ''', (guild_id, channel_id))
    conn.commit()

# Get the vouch channel for a guild
def get_vouch_channel(guild_id):
    c.execute('SELECT vouch_channel_id FROM config WHERE guild_id = ?', (guild_id,))
    result = c.fetchone()
    return result[0] if result else None

# Get the vouch count.
def get_vouch_count(user_id):
    c.execute('SELECT COUNT(*) FROM vouches WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    return result[0] if result else 0

def get_user_vouches(user_id):
    c.execute('''
        SELECT voucher_id, message, stars
        FROM vouches
        WHERE user_id = ?
    ''', (user_id,))
    rows = c.fetchall()
    vouches = []
    for row in rows:
        vouches.append({
            'voucher_id': row[0],
            'message': row[1],
            'stars': row[2]
        })
    return vouches


def get_all_vouches():
    c.execute('''
        SELECT v.user_id, v.voucher_id, v.message, v.stars
        FROM vouches v
    ''')
    rows = c.fetchall()
    vouches = []
    for row in rows:
        vouches.append({
            'user_id': row[0],
            'voucher_id': row[1],
            'message': row[2],
            'stars': row[3]
        })
    return vouches



# Initialize the database when the module is imported
init_db()
