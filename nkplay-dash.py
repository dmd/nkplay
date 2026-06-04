#!/usr/bin/python3
"""Single-page dashboard for nkplay jukebox stats.

Reads nkplay-log.csv (iso_utc_timestamp, playlist, hostname) and an optional
nkplay-names.json (playlist id -> {label, tracks}) from this directory, and
renders a self-contained HTML page. No external dependencies.

Regenerate nkplay-names.json from the music dir whenever playlists change.
"""
import csv
import html
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, 'nkplay-log.csv')
NAMES_PATH = os.path.join(HERE, 'nkplay-names.json')
LOCAL_TZ = ZoneInfo('America/New_York')

# Stable colors per host (sorted): capy = sunflower yellow, platy = orchid
# purple, picked for roughly equal luminance on the dark background.
HOST_COLORS = ['#e6b13c', '#c7a4ec', '#46b97a', '#d64f6f', '#3a8ee8']


def load_names():
    try:
        with open(NAMES_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def load_rows():
    rows = []
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            for r in csv.reader(f):
                if len(r) < 3:
                    continue
                ts, pid, host = r[0], r[1], r[2]
                try:
                    dt = datetime.fromisoformat(ts).astimezone(LOCAL_TZ)
                except Exception:
                    continue
                rows.append((dt, pid.strip(), host.strip()))
    except FileNotFoundError:
        pass
    rows.sort(key=lambda x: x[0])
    return dedupe(rows)


# Collapse rapid repeats: re-selecting the same playlist in the same room
# within this window (keypad mashing, headache replays) counts as one play.
DEDUPE_WINDOW = timedelta(minutes=30)


def dedupe(rows):
    out = []
    last = {}  # (host, pid) -> datetime of last kept play
    for dt, pid, host in rows:
        prev = last.get((host, pid))
        if prev is not None and dt - prev <= DEDUPE_WINDOW:
            continue
        out.append((dt, pid, host))
        last[(host, pid)] = dt
    return out


def pretty_host(h):
    return h[:-3] if h.endswith('-pi') else h


def esc(s):
    return html.escape(str(s))


def bar(frac, color, label_html='', value_html=''):
    pct = max(0.0, min(1.0, frac)) * 100
    return (
        f'<div class="barrow">'
        f'<div class="barlabel">{label_html}</div>'
        f'<div class="bartrack"><div class="barfill" '
        f'style="width:{pct:.1f}%;background:{color}"></div></div>'
        f'<div class="barval">{value_html}</div>'
        f'</div>'
    )


def main():
    sys.stdout.write('Content-Type: text/html; charset=utf-8\r\n\r\n')

    names = load_names()
    rows = load_rows()

    def label_of(pid):
        info = names.get(pid)
        if info and info.get('label'):
            label = info['label']
            # we know these by date, not "capyland <date>"
            if label.startswith('capyland '):
                return label[len('capyland '):]
            return label
        return ''

    total = len(rows)
    hosts = sorted({h for _, _, h in rows})
    host_color = {h: HOST_COLORS[i % len(HOST_COLORS)] for i, h in enumerate(hosts)}

    # --- aggregates ---
    per_host = Counter(h for _, _, h in rows)
    per_pid = Counter(p for _, p, _ in rows)
    per_pid_host = defaultdict(Counter)  # pid -> host -> count
    for _, p, h in rows:
        per_pid_host[p][h] += 1

    per_day = Counter(dt.date() for dt, _, _ in rows)
    per_hour = Counter(dt.hour for dt, _, _ in rows)

    first_dt = rows[0][0] if rows else None
    last_dt = rows[-1][0] if rows else None
    active_days = len(per_day)

    now_local = datetime.now(LOCAL_TZ)

    # ---------------- HTML ----------------
    out = []
    w = out.append
    w('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w('<title>nkplay dashboard</title>')
    w('<style>')
    w('''
:root{--bg:#14110f;--panel:#1f1b18;--panel2:#272220;--ink:#f3ece4;--mut:#9b9189;--line:#332d29;--accent:#e8833a;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
a{color:var(--accent)}
.wrap{max-width:980px;margin:0 auto;padding:24px 18px 60px}
header{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:6px}
h1{font-size:24px;margin:0;letter-spacing:.3px}
h1 .em{font-size:30px}
.sub{color:var(--mut);font-size:13px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:1.2px;color:var(--mut);
 margin:34px 0 14px;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.card .n{font-size:28px;font-weight:700;line-height:1.1}
.card .k{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.8px;margin-top:4px}
.card .x{color:var(--mut);font-size:12px;margin-top:6px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.barrow{display:grid;grid-template-columns:200px 1fr 64px;align-items:center;gap:12px;margin:7px 0}
.barlabel{font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.num{font-weight:700;font-variant-numeric:tabular-nums}
.barlabel .num{font-size:18px;margin-right:8px}
.barlabel .nm{color:var(--mut);font-size:12px}
.bartrack{border-radius:6px;height:18px;overflow:hidden;display:flex}
.barfill{height:100%;border-radius:6px}
.barseg{height:100%}
.barseg:last-child{border-radius:0 6px 6px 0}
.barval{text-align:right;font-variant-numeric:tabular-nums;color:var(--mut);font-size:13px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:2px 0 14px;font-size:13px;color:var(--mut)}
.dot{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:middle}
.hours{display:flex;align-items:flex-end;gap:3px;height:120px;margin-top:6px}
.hcol{flex:1;height:100%;display:flex;align-items:flex-end}
.hbar{width:100%;background:var(--accent);border-radius:3px 3px 0 0;min-height:2px}
.hticks{display:flex;gap:3px;margin-top:5px}
.htick{flex:1;text-align:center;font-size:9px;color:var(--mut)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.6px}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
.recent{table-layout:fixed}
.recent col.daycol{width:120px}
.recent td,.recent th{vertical-align:top}
.recent .day{color:var(--mut);white-space:nowrap}
.recent .cell .num{font-size:17px;margin-right:12px;display:inline-block;line-height:1.7}
.recent .mult{color:var(--mut);font-size:11px;font-weight:600;margin-left:1px}
.recent .empty{color:var(--line)}
.foot{color:var(--mut);font-size:12px;margin-top:36px;text-align:center}
@media(max-width:680px){.barrow{grid-template-columns:110px 1fr 48px}}
''')
    w('</style></head><body><div class="wrap">')

    # header
    w('<header><h1>&#127925; nkplay <span class="em"></span>jukebox</h1>')
    if last_dt:
        w(f'<div class="sub">{total} plays &middot; '
          f'{esc(first_dt.strftime("%b %-d, %Y"))} &ndash; '
          f'{esc(last_dt.strftime("%b %-d, %Y"))}</div>')
    w('</header>')
    w(f'<div class="sub">Generated {esc(now_local.strftime("%a %b %-d, %Y %-I:%M %p %Z"))}</div>')

    if not rows:
        w('<p style="margin-top:40px">No plays logged yet.</p>')
        w('</div></body></html>')
        sys.stdout.write(''.join(out))
        return

    # summary cards
    w('<div class="cards">')
    w(f'<div class="card"><div class="n">{total}</div><div class="k">Total plays</div></div>')
    w(f'<div class="card"><div class="n">{active_days}</div><div class="k">Active days</div>'
      f'<div class="x">{total/active_days:.1f} plays / active day</div></div>')
    top_pid, top_n = per_pid.most_common(1)[0]
    tname = esc(label_of(top_pid))
    w(f'<div class="card"><div class="n">{esc(top_pid)}</div><div class="k">Top playlist</div>'
      f'<div class="x">{top_n} plays{" &middot; " + tname if tname else ""}</div></div>')
    w('</div>')

    # per-host
    w('<h2>By room</h2><div class="panel">')
    hmax = max(per_host.values())
    for h, c in per_host.most_common():
        lbl = (f'<span style="font-weight:600">{esc(pretty_host(h))}</span>')
        w(bar(c / hmax, host_color[h], lbl, f'{c} ({c*100//total}%)'))
    w('</div>')

    # top playlists with host breakdown
    w('<h2>Most played playlists</h2>')
    if len(hosts) > 1:
        w('<div class="legend">')
        for h in hosts:
            w(f'<span><span class="dot" style="background:{host_color[h]}"></span>'
              f'{esc(pretty_host(h))}</span>')
        w('</div>')
    w('<div class="panel">')
    pmax = per_pid.most_common(1)[0][1]
    for pid, c in per_pid.most_common(15):
        nm = esc(label_of(pid))
        lbl = (f'<span class="num">{esc(pid)}</span>'
               f'<span class="nm">{nm}</span>')
        # stacked segments per host
        segs = []
        for h in hosts:
            hc = per_pid_host[pid].get(h, 0)
            if hc:
                segs.append(f'<div class="barseg" style="width:{hc/pmax*100:.1f}%;'
                            f'background:{host_color[h]}"></div>')
        track = (f'<div class="barlabel">{lbl}</div>'
                 f'<div class="bartrack">{"".join(segs)}</div>'
                 f'<div class="barval">{c}</div>')
        w(f'<div class="barrow">{track}</div>')
    w('</div>')

    # time of day -- bars and tick labels are separate rows so the labels
    # never push individual bars off the baseline
    w('<h2>Time of day</h2><div class="panel"><div class="hours">')
    hourmax = max(per_hour.values()) if per_hour else 1
    disps = []
    for hr in range(24):
        c = per_hour.get(hr, 0)
        pct = c / hourmax * 100
        disp = '12a' if hr == 0 else ('12p' if hr == 12 else
               (f'{hr}a' if hr < 12 else f'{hr-12}p'))
        disps.append(disp)
        w(f'<div class="hcol" title="{disp}: {c}">'
          f'<div class="hbar" style="height:{pct:.0f}%"></div></div>')
    w('</div><div class="hticks">')
    for hr in range(24):
        w(f'<div class="htick">{disps[hr] if hr % 3 == 0 else ""}</div>')
    w('</div></div>')

    # recent plays: one row per day, a column per room, numbers in each cell
    day_plays = defaultdict(lambda: defaultdict(list))  # date -> host -> [pid...]
    for dt, pid, h in rows:
        day_plays[dt.date()][h].append(pid)

    def cell(pids):
        if not pids:
            return '<span class="empty">&middot;</span>'
        counts = Counter(pids)
        seen = list(dict.fromkeys(pids))  # first-seen order
        parts = []
        for p in seen:
            mult = f'<span class="mult">&times;{counts[p]}</span>' if counts[p] > 1 else ''
            parts.append(f'<span class="num">{esc(p)}{mult}</span>')
        return ''.join(parts)

    w('<h2>Recent plays</h2><div class="panel"><table class="recent">')
    w('<colgroup><col class="daycol">' + '<col>' * len(hosts) + '</colgroup>')
    w('<tr><th>Day</th>' +
      ''.join(f'<th>{esc(pretty_host(h))}</th>' for h in hosts) + '</tr>')
    for day in sorted(day_plays, reverse=True)[:45]:
        w(f'<tr><td class="day">{esc(day.strftime("%a %b %-d"))}</td>' +
          ''.join(f'<td class="cell">{cell(day_plays[day].get(h, []))}</td>'
                  for h in hosts) +
          '</tr>')
    w('</table></div>')

    w('<div class="foot">nkplay &middot; auto-generated from play log</div>')
    w('</div></body></html>')

    sys.stdout.write(''.join(out))


if __name__ == '__main__':
    main()
