from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import sqlite3
import secrets
import hashlib
import os
import threading
import time
import html

HOST = "127.0.0.1"
PORT = 8000
DB_FILE = "gagan_world.db"
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>GAGAN WORLD | Gamer Chat</title>
<style>
:root{--bg:#06111f;--panel:#0d1e31;--panel2:#102942;--line:#23445f;--cyan:#62dcff;--text:#edf7ff;--muted:#94aec7;--blue:#168bff}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 15% 0%,#123b61,transparent 38%),var(--bg);color:var(--text);font:15px/1.45 system-ui,Segoe UI,sans-serif}
button,input,textarea{font:inherit}button{cursor:pointer}.hidden{display:none!important}.top{height:72px;padding:0 5%;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);background:#071525e8;position:sticky;top:0}
.brand{font-size:21px;font-weight:950;letter-spacing:1px}.brand b{color:var(--cyan)}.symbol{color:var(--cyan);margin-right:8px}.tag{color:#8cf2d0;font-size:10px;letter-spacing:1.5px}
.wrap{width:min(1050px,94%);margin:36px auto}.hero{text-align:center;margin-bottom:27px}.eyebrow{color:var(--cyan);font-size:10px;letter-spacing:2px;font-weight:900}.hero h1{font-size:clamp(35px,6vw,58px);line-height:1.04;margin:10px 0;background:linear-gradient(90deg,#fff,#62dcff);color:transparent;background-clip:text}.hero p{color:var(--muted);margin:8px auto;max-width:550px}
.card{background:linear-gradient(145deg,var(--panel),#091727);border:1px solid var(--line);border-radius:16px;overflow:hidden}.login{max-width:420px;margin:0 auto;padding:24px}.login h2{margin:0 0 5px}.muted{color:var(--muted);font-size:12px}.field{display:block;color:#c4d8e8;font-size:12px;font-weight:700;margin-top:15px}.field input,.field textarea,.composer input,.roomform input{width:100%;margin-top:7px;background:#061321;color:white;border:1px solid #31516b;border-radius:9px;padding:12px;outline:none}.field input:focus,.composer input:focus{border-color:var(--cyan)}.btn{border:0;border-radius:9px;padding:11px 15px;font-weight:850;font-size:12px;background:linear-gradient(100deg,#1178c7,#278fff);color:white}.wide{width:100%;margin-top:18px}.switch{border:0;background:none;color:var(--cyan);font-weight:800}.notice{color:#ffcf91;font-size:12px;margin-top:12px;overflow-wrap:anywhere}
.app{display:grid;grid-template-columns:230px 1fr;gap:16px}.sidebar{padding:17px}.sidehead{font-size:10px;letter-spacing:1.5px;color:var(--muted);font-weight:900;margin:5px 0 12px}.room{width:100%;padding:10px;border:1px solid transparent;border-radius:8px;background:transparent;color:#cfe5f7;text-align:left;margin:2px 0}.room.active{background:#103754;border-color:#28688b;color:white}.roomform{display:flex;gap:5px;margin:9px 0 23px}.roomform input{min-width:0;padding:9px;font-size:11px}.roomform button{border:1px solid #28688b;background:#103754;color:var(--cyan);border-radius:8px}.chat{min-height:500px;display:flex;flex-direction:column}.chathead{padding:17px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:10px}.chathead h2{margin:0;font-size:17px}.chathead p{margin:4px 0 0;color:var(--muted);font-size:11px}.msgs{padding:17px;flex:1;min-height:260px;max-height:50vh;overflow:auto}.msg{padding:10px 12px;margin:10px 0;background:#152c43;border-radius:10px;overflow-wrap:anywhere}.msg strong{color:var(--cyan);font-size:12px}.msg p{margin:4px 0 0;white-space:pre-wrap}.msg time{font-size:9px;color:#8da8bf;float:right}.empty{text-align:center;color:var(--muted);padding:55px 10px}.composer{display:flex;gap:8px;padding:12px;border-top:1px solid var(--line)}.composer input{margin:0;min-width:0;flex:1}.lower{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.inner{padding:17px}.inner h3{margin:0 0 12px}.inner input,.inner textarea{width:100%;background:#061321;color:white;border:1px solid #31516b;border-radius:8px;padding:10px;margin:5px 0 10px}.friendline{padding:8px 0;border-bottom:1px solid #203c54;font-size:12px;display:flex;justify-content:space-between;gap:8px}.tiny{font-size:10px;color:var(--muted)}.logout{border:1px solid #31516b;background:transparent;color:#cfe5f7;border-radius:8px;padding:7px 10px;font-size:11px}.footer{text-align:center;color:#65819b;font-size:10px;letter-spacing:1.5px;padding:25px}
@media(max-width:720px){.app{grid-template-columns:1fr}.sidebar{padding:12px}.roomlist{display:flex;overflow:auto}.room{white-space:nowrap;width:auto}.roomform{max-width:320px;margin-bottom:12px}.lower{grid-template-columns:1fr}.msgs{max-height:45vh}.wrap{margin:20px auto}.top{padding:0 4%}}
</style></head>
<body>
<header class="top"><div class="brand"><span class="symbol">◈</span>GAGAN <b>WORLD</b></div><span class="tag">● BLUE CYBER LOBBY</span></header>
<main class="wrap">
<section id="auth">
<div class="hero"><div class="eyebrow">YOUR GAME. YOUR SQUAD.</div><h1>GAGAN WORLD</h1><p>A simple gamer hangout. Create a username, join a room, and chat.</p></div>
<div class="card login"><h2 id="authTitle">Welcome, gamer</h2><p class="muted" id="authSub">Log in to enter the lobby.</p>
<form id="authForm"><label class="field" id="userLabel" hidden>Gamer username<input id="username" minlength="2" maxlength="20" autocomplete="username"></label><label class="field">Username<input id="loginName" minlength="2" maxlength="20" required autocomplete="username" placeholder="e.g. NovaGG"></label><label class="field">Password<input id="password" type="password" minlength="6" required autocomplete="current-password" placeholder="At least 6 characters"></label><button class="btn wide" id="authSubmit">LOG IN →</button></form>
<p class="muted" id="switchText">New here? <button class="switch" id="switchMode" type="button">Create an account</button></p><div id="authNotice" class="notice"></div>
<p class="tiny">This starter runs on your computer. To chat with friends on different devices, it must be hosted online and the database/server configured for public access.</p></div>
</section>
<section id="workspace" class="hidden">
<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:15px"><div><div class="eyebrow">COMMUNITY / LOBBY</div><h2 style="margin:5px 0">Welcome, <span id="welcome" style="color:var(--cyan)"></span></h2></div><button class="logout" id="logout">Log out ↗</button></div>
<div class="app">
<aside class="card sidebar"><div class="sidehead">CHAT ROOMS</div><div class="roomlist" id="rooms"></div><form id="roomForm" class="roomform"><input id="roomName" maxlength="28" placeholder="new-room-name" required><button title="Create room">+</button></form><div class="sidehead">FRIENDS</div><p class="tiny">Add a gamer by exact username.</p><form id="friendForm" class="roomform"><input id="friendName" maxlength="20" placeholder="Gamer username" required><button>+</button></form><div id="friends"></div></aside>
<section class="card chat"><div class="chathead"><div><h2 id="roomTitle"># general</h2><p>Be kind. Have fun. Find your squad.</p></div><span class="tag">● CHAT</span></div><div class="msgs" id="messages"><div class="empty">Loading messages...</div></div><form id="messageForm" class="composer"><input id="messageInput" maxlength="500" placeholder="Type a message..." required autocomplete="off"><button class="btn">SEND ↗</button></form></section>
</div>
<div class="lower"><section class="card inner"><h3>🎮 Gamer profile</h3><form id="profileForm"><label class="field">Display name<input id="displayName" maxlength="20" required></label><label class="field">Bio<textarea id="bio" maxlength="140" rows="3" placeholder="Tell your squad about yourself"></textarea></label><button class="btn">SAVE PROFILE</button></form></section><section class="card inner"><h3>🎙️ Voice chat</h3><p class="muted">This Python-only version includes text chat. Voice chat requires a WebRTC/signaling service or an external voice provider; it is not included in this simple starter.</p><p class="tiny">Tip: don't share your password, real address, or other private information in public rooms.</p></section></div>
<div id="appNotice" class="notice"></div>
</section>
</main><footer class="footer">GAGAN WORLD © · YOUR GAME. YOUR SQUAD.</footer>
<script>
let currentUser=null, selectedRoom='general', pollHandle=null, isSignup=false, lastMessageId=0;
const $=id=>document.getElementById(id);
async function api(path, options={}){const res=await fetch(path,{headers:{'Content-Type':'application/json'},...options});const data=await res.json();if(!res.ok)throw new Error(data.error||'Something went wrong');return data}
function notice(id,msg){$(id).textContent=msg||''}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
$('switchMode').onclick=()=>{isSignup=!isSignup;$('authTitle').textContent=isSignup?'Create your gamer account':'Welcome, gamer';$('authSub').textContent=isSignup?'Choose a username and password.':'Log in to enter the lobby.';$('authSubmit').textContent=isSignup?'CREATE ACCOUNT →':'LOG IN →';$('switchText').firstChild.textContent=isSignup?'Already registered? ':'New here? ';$('switchMode').textContent=isSignup?'Log in':'Create an account';$('userLabel').hidden=!isSignup;$('username').required=isSignup;$('password').autocomplete=isSignup?'new-password':'current-password';notice('authNotice','')};
$('authForm').onsubmit=async e=>{e.preventDefault();notice('authNotice','Please wait...');try{const data=await api(isSignup?'/api/signup':'/api/login',{method:'POST',body:JSON.stringify({username:$('loginName').value.trim(),password:$('password').value,display_name:$('username').value.trim()})});currentUser=data.user;await enterApp()}catch(err){notice('authNotice',err.message)}};
async function enterApp(){ $('auth').classList.add('hidden');$('workspace').classList.remove('hidden');$('welcome').textContent=currentUser.username;await refreshRooms();await refreshProfile();await refreshFriends();await refreshMessages();if(pollHandle)clearInterval(pollHandle);pollHandle=setInterval(async()=>{if(currentUser){await refreshMessages(true);await refreshFriends()}},2500)}
$('logout').onclick=async()=>{if(pollHandle)clearInterval(pollHandle);try{await api('/api/logout',{method:'POST'})}catch{}currentUser=null;$('workspace').classList.add('hidden');$('auth').classList.remove('hidden');$('password').value='';notice('authNotice','You have logged out.')};
async function refreshRooms(){const d=await api('/api/rooms');$('rooms').innerHTML=d.rooms.map(r=>`<button class="room ${r.name===selectedRoom?'active':''}" data-room="${esc(r.name)}">${r.name==='general'?'🌐':r.name==='squad-finder'?'⚔️':'#'} &nbsp; ${esc(r.name)}</button>`).join('');document.querySelectorAll('[data-room]').forEach(b=>b.onclick=async()=>{selectedRoom=b.dataset.room;lastMessageId=0;await refreshRooms();await refreshMessages()});$('roomTitle').textContent='# '+selectedRoom}
$('roomForm').onsubmit=async e=>{e.preventDefault();try{const d=await api('/api/rooms',{method:'POST',body:JSON.stringify({name:$('roomName').value.trim()})});selectedRoom=d.room.name;$('roomName').value='';lastMessageId=0;await refreshRooms();await refreshMessages();notice('appNotice','Room created.')}catch(err){notice('appNotice',err.message)}};
async function refreshMessages(silent=false){try{const d=await api('/api/messages?room='+encodeURIComponent(selectedRoom)+'&after='+lastMessageId);const box=$('messages');if(!d.messages.length&&lastMessageId===0){box.innerHTML='<div class="empty">It is quiet in here. Say hello 👋</div>';return}if(d.messages.length){if(lastMessageId===0)box.innerHTML='';for(const m of d.messages){const div=document.createElement('div');div.className='msg';div.innerHTML=`<time>${esc(m.time)}</time><strong>${esc(m.username)}</strong><p>${esc(m.content)}</p>`;box.appendChild(div);lastMessageId=Math.max(lastMessageId,m.id)}box.scrollTop=box.scrollHeight}}catch(err){if(!silent)notice('appNotice',err.message)}}
$('messageForm').onsubmit=async e=>{e.preventDefault();const content=$('messageInput').value.trim();if(!content)return;try{await api('/api/messages',{method:'POST',body:JSON.stringify({room:selectedRoom,content})});$('messageInput').value='';await refreshMessages()}catch(err){notice('appNotice',err.message)}};
async function refreshProfile(){const d=await api('/api/profile');$('displayName').value=d.profile.display_name||currentUser.username;$('bio').value=d.profile.bio||''}
$('profileForm').onsubmit=async e=>{e.preventDefault();try{await api('/api/profile',{method:'POST',body:JSON.stringify({display_name:$('displayName').value.trim(),bio:$('bio').value.trim()})});notice('appNotice','Profile saved!')}catch(err){notice('appNotice',err.message)}};
async function refreshFriends(){const d=await api('/api/friends');$('friends').innerHTML=d.friends.map(f=>`<div class="friendline"><span>${esc(f.username)}</span><span class="tiny">${esc(f.status)}</span></div>`).join('')||'<p class="tiny">No friends yet.</p>'}
$('friendForm').onsubmit=async e=>{e.preventDefault();try{await api('/api/friends',{method:'POST',body:JSON.stringify({username:$('friendName').value.trim()})});$('friendName').value='';await refreshFriends();notice('appNotice','Friend request sent.')}catch(err){notice('appNotice',err.message)}};
</script></body></html>"""

def connect():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE COLLATE NOCASE,
          password_hash TEXT NOT NULL,
          salt TEXT NOT NULL,
          display_name TEXT NOT NULL,
          bio TEXT NOT NULL DEFAULT '',
          created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rooms(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE COLLATE NOCASE,
          created_by INTEGER NOT NULL,
          created_at INTEGER NOT NULL,
          FOREIGN KEY(created_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS messages(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          room TEXT NOT NULL,
          user_id INTEGER NOT NULL,
          content TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS friends(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          requester INTEGER NOT NULL,
          addressee INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'pending',
          created_at INTEGER NOT NULL,
          UNIQUE(requester,addressee),
          FOREIGN KEY(requester) REFERENCES users(id),
          FOREIGN KEY(addressee) REFERENCES users(id)
        );
        """)
        now = int(time.time())
        for name in ("general", "squad-finder", "gaming-talk"):
            c.execute("INSERT OR IGNORE INTO rooms(name,created_by,created_at) VALUES(?,0,?)", (name, now))

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 250_000).hex()
    return salt, hashed

class Handler(BaseHTTPRequestHandler):
    server_version = "GaganWorld/1.0"
    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
    def body(self):
        length = min(int(self.headers.get("Content-Length", "0")), 20000)
        return json.loads(self.rfile.read(length) or b"{}")
    def current_user(self):
        token = self.cookies.get("gw_session") if hasattr(self, "cookies") else None
        if not token:
            from http.cookies import SimpleCookie
            cookie = SimpleCookie(self.headers.get("Cookie", ""))
            token = cookie["gw_session"].value if "gw_session" in cookie else None
        return getattr(self.server, "sessions", {}).get(token)
    def do_GET(self):
        path = urlparse(self.path)
        if path.path == "/":
            body = PAGE.encode()
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body); return
        user = self.current_user()
        if path.path == "/api/me":
            return self.send_json(200, {"user": self.public_user(user)} if user else {"user": None})
        if not user:
            return self.send_json(401, {"error":"Please log in again."})
        if path.path == "/api/rooms":
            with connect() as c:
                rows = c.execute("SELECT name FROM rooms ORDER BY id").fetchall()
            return self.send_json(200, {"rooms":[{"name":r["name"]} for r in rows]})
        if path.path == "/api/messages":
            from urllib.parse import parse_qs
            q = parse_qs(path.query)
            room = q.get("room", ["general"])[0]
            try: after = max(0, int(q.get("after", ["0"])[0]))
            except ValueError: after = 0
            with connect() as c:
                rows = c.execute("""SELECT m.id,m.content,m.created_at,u.username FROM messages m JOIN users u ON u.id=m.user_id WHERE m.room=? AND m.id>? ORDER BY m.id ASC LIMIT 100""", (room,after)).fetchall()
            msgs = [{"id":r["id"],"content":r["content"],"username":r["username"],"time":time.strftime("%H:%M",time.localtime(r["created_at"]))} for r in rows]
            return self.send_json(200, {"messages":msgs})
        if path.path == "/api/profile":
            with connect() as c: row = c.execute("SELECT username,display_name,bio FROM users WHERE id=?", (user["id"],)).fetchone()
            return self.send_json(200, {"profile":dict(row)})
        if path.path == "/api/friends":
            with connect() as c:
                rows = c.execute("""SELECT u.username,f.status FROM friends f JOIN users u ON u.id=CASE WHEN f.requester=? THEN f.addressee ELSE f.requester END WHERE f.requester=? OR f.addressee=? ORDER BY f.id DESC""", (user["id"],user["id"],user["id"])).fetchall()
            return self.send_json(200, {"friends":[dict(r) for r in rows]})
        return self.send_json(404, {"error":"Not found."})
    def public_user(self, user):
        if not user: return None
        return {"id":user["id"],"username":user["username"]}
    def do_POST(self):
        path = urlparse(self.path).path
        try: data = self.body()
        except Exception: return self.send_json(400, {"error":"Invalid request."})
        if path in ("/api/signup","/api/login"):
            username = str(data.get("username","")).strip()
            password = str(data.get("password",""))
            if not (2 <= len(username) <= 20) or not username.replace("_","").replace("-","").isalnum():
                return self.send_json(400, {"error":"Username must be 2–20 characters using letters, numbers, _ or -."})
            if len(password) < 6 or len(password) > 200:
                return self.send_json(400, {"error":"Password must be at least 6 characters."})
            with connect() as c:
                row = c.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username,)).fetchone()
                if path.endswith("signup"):
                    if row: return self.send_json(409, {"error":"That username is already taken."})
                    salt, hashed = hash_password(password)
                    display = str(data.get("display_name") or username).strip()[:20] or username
                    cur = c.execute("INSERT INTO users(username,password_hash,salt,display_name,created_at) VALUES(?,?,?,?,?)",(username,hashed,salt,display,int(time.time())))
                    uid = cur.lastrowid
                    row = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
                else:
                    if not row: return self.send_json(401, {"error":"Wrong username or password."})
                    _, hashed = hash_password(password,row["salt"])
                    if not secrets.compare_digest(hashed,row["password_hash"]):
                        return self.send_json(401, {"error":"Wrong username or password."})
            token = secrets.token_urlsafe(32)
            self.server.sessions[token] = {"id":row["id"],"username":row["username"]}
            body = json.dumps({"user":self.public_user(self.server.sessions[token])}).encode()
            self.send_response(200); self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Set-Cookie",f"gw_session={token}; HttpOnly; SameSite=Lax; Path=/")
            self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body); return
        user = self.current_user()
        if not user: return self.send_json(401, {"error":"Please log in."})
        if path == "/api/logout":
            from http.cookies import SimpleCookie
            cookie=SimpleCookie(self.headers.get("Cookie","")); token=cookie["gw_session"].value if "gw_session" in cookie else None
            if token: self.server.sessions.pop(token,None)
            self.send_response(200); self.send_header("Set-Cookie","gw_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}'); return
        if path == "/api/messages":
            room = str(data.get("room",""))
            content = str(data.get("content","")).strip()
            if not room or len(content)<1 or len(content)>500: return self.send_json(400, {"error":"Message must be 1–500 characters."})
            with connect() as c:
                exists = c.execute("SELECT 1 FROM rooms WHERE name=? COLLATE NOCASE",(room,)).fetchone()
                if not exists: return self.send_json(404, {"error":"Room not found."})
                c.execute("INSERT INTO messages(room,user_id,content,created_at) VALUES(?,?,?,?)",(room,user["id"],content,int(time.time())))
            return self.send_json(201, {"ok":True})
        if path == "/api/rooms":
            name = str(data.get("name","")).strip().lower()
            if not (1<=len(name)<=28) or not all(ch.isalnum() or ch in "-_" for ch in name):
                return self.send_json(400, {"error":"Room names use only letters, numbers, - or _ (max 28)."})
            try:
                with connect() as c:
                    c.execute("INSERT INTO rooms(name,created_by,created_at) VALUES(?,?,?)",(name,user["id"],int(time.time())))
            except sqlite3.IntegrityError: return self.send_json(409, {"error":"That room already exists."})
            return self.send_json(201, {"room":{"name":name}})
        if path == "/api/profile":
            display = str(data.get("display_name","")).strip()[:20]
            bio = str(data.get("bio","")).strip()[:140]
            if not display: return self.send_json(400, {"error":"Display name cannot be blank."})
            with connect() as c: c.execute("UPDATE users SET display_name=?,bio=? WHERE id=?",(display,bio,user["id"]))
            return self.send_json(200, {"ok":True})
        if path == "/api/friends":
            name = str(data.get("username","")).strip()
            with connect() as c:
                target = c.execute("SELECT id,username FROM users WHERE username=? COLLATE NOCASE",(name,)).fetchone()
                if not target: return self.send_json(404, {"error":"Gamer not found. They need to create an account first."})
                if target["id"] == user["id"]: return self.send_json(400, {"error":"You cannot add yourself."})
                try:
                    c.execute("INSERT INTO friends(requester,addressee,status,created_at) VALUES(?,?,?,?)",(user["id"],target["id"],"pending",int(time.time())))
                except sqlite3.IntegrityError:
                    return self.send_json(409, {"error":"A friend request already exists."})
            return self.send_json(201, {"ok":True})
        return self.send_json(404, {"error":"Not found."})

def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.sessions = {}
    print(f"\nGAGAN WORLD is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop. This starter is local-only; it is not public internet hosting.\n")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nStopping GAGAN WORLD.")
    finally: server.server_close()

if __name__ == "__main__":
    main()
