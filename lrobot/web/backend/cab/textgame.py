"""文字博弈主持台"""

from logic import data
from message.handler.msg import Msg
from .base import APIRouter, Depends, R, Dict, Response, FileResponse, cookie_account_get, website_logger
from config import monitor_adapter

router = APIRouter()      # 接口,挂在 /hjd 前缀下
page_router = APIRouter()  # 页面,和前端其他页一样走 /cab


async def _board():
    """取当前这场(没有进行中的就取最近一场)的全量数据"""
    game = await data.textgame_get() or await data.textgame_last()
    if not game:
        return None
    return await data.textgame_board(game["id"])


@router.get("/textgame/board")
async def textgame_board_get():
    """主持台数据,只读不鉴权"""
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    return R(status="success", data=board)


@router.put("/textgame/ops")
@monitor_adapter("#内阁_文字博弈_算分")
async def textgame_ops_put(data_: Dict, account: str = Depends(cookie_account_get)):
    """保存某题的计分式子并重算"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    game_id = board["game"]["id"]
    round = int(data_["round"])
    ops = {k.upper(): str(v).strip() for k, v in (data_.get("ops") or {}).items() if str(v).strip()}
    await data.textgame_ops_set(game_id, round, ops)
    errors = await data.textgame_recalc(game_id, 1)
    website_logger.info(f"[文字博弈]{account}-> 第{round}题算分 {ops}", extra={"event": "网页日志"})
    if errors:
        return R(status="fail", data="；".join(errors))
    return R(status="success", data=await data.textgame_board(game_id))


@router.put("/textgame/options")
@monitor_adapter("#内阁_文字博弈_改选项集")
async def textgame_options_put(data_: Dict, account: str = Depends(cookie_account_get)):
    """手动改某题的选项集,纠正自动识别的偏差"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    game_id = board["game"]["id"]
    round = int(data_["round"])
    options = await data.textgame_options_set(game_id, round, data_.get("options"))
    website_logger.info(f"[文字博弈]{account}-> 第{round}题选项集改为 {options}", extra={"event": "网页日志"})
    return R(status="success", data=await data.textgame_board(game_id))


@router.put("/textgame/choice")
@monitor_adapter("#内阁_文字博弈_改选项")
async def textgame_choice_put(data_: Dict, account: str = Depends(cookie_account_get)):
    """改某人某题的选项"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    game_id = board["game"]["id"]
    round = int(data_["round"])
    await data.textgame_choice_set(game_id, round, data_["user"], data_.get("choice"))
    await data.textgame_recalc(game_id, 1, data_["user"])
    website_logger.info(
        f"[文字博弈]{account}-> 改第{round}题 {data_['user']} 为 {data_.get('choice')}",
        extra={"event": "网页日志"},
    )
    return R(status="success", data=await data.textgame_board(game_id))


@router.put("/textgame/score")
@monitor_adapter("#内阁_文字博弈_改分")
async def textgame_score_put(data_: Dict, account: str = Depends(cookie_account_get)):
    """手动覆盖某人某题的得分"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    game_id = board["game"]["id"]
    round = int(data_["round"])
    score = data_.get("score")
    if score is None or str(score).strip() == "":
        await data.textgame_score_clear(game_id, round, data_["user"])
    else:
        await data.textgame_score_set(game_id, round, data_["user"], float(score))
    website_logger.info(
        f"[文字博弈]{account}-> 改第{round}题 {data_['user']} 得分 {data_['score']}",
        extra={"event": "网页日志"},
    )
    return R(status="success", data=await data.textgame_board(game_id))


@router.put("/textgame/absent")
@monitor_adapter("#内阁_文字博弈_未交票")
async def textgame_absent_put(data_: Dict, account: str = Depends(cookie_account_get)):
    """切换未交票是否按 A 计分"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    game_id = board["game"]["id"]
    await data.textgame_edit(game_id, absent_as_a=1 if data_.get("absent_as_a") else 0)
    await data.textgame_recalc(game_id, 1)
    return R(status="success", data=await data.textgame_board(game_id))


@router.post("/textgame/excel")
@monitor_adapter("#内阁_文字博弈_导出")
async def textgame_excel_post(data_: Dict = None, account: str = Depends(cookie_account_get)):
    """生成复盘 excel,可选直接发到开局的群"""
    if not account:
        return R(status="fail", data="未登录")
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    file = await data.textgame_excel(board["game"]["id"])
    if not file:
        return R(status="fail", data="导出失败")
    if (data_ or {}).get("send"):
        Msg(
            platform="LR5921",
            event="发送",
            kind="群聊发送",
            content=f"[文件:{file}]",
            group=board["game"]["group_id"],
        )
        website_logger.info(f"[文字博弈]{account}-> 复盘已发群", extra={"event": "网页日志"})
        return R(status="success", data="已发送到群里")
    return R(status="success", data="已生成,点下载按钮取回")


@router.get("/textgame/excel")
async def textgame_excel_get():
    """下载最近一次生成的复盘"""
    board = await _board()
    if not board:
        return R(status="fail", data="当前没有文字博弈")
    file = await data.textgame_excel(board["game"]["id"])
    return FileResponse(str(file), filename=file.name)


@page_router.get("/cab/textgame")
async def textgame_page():
    """主持台页面,和前端其他页面一样从 /cab 进"""
    return Response(content=PAGE, media_type="text/html; charset=utf-8")


PAGE = r"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>文字博弈 · 主持台</title>
<style>
:root{--bg:#f6f7f9;--fg:#1c1f23;--mut:#6b7280;--line:#e3e6ea;--card:#fff;--accent:#2f6feb;--warn:#c2410c;--ok:#15803d;--red:#dc2626}
@media (prefers-color-scheme:dark){:root{--bg:#15181c;--fg:#e6e8ea;--mut:#9aa3ad;--line:#2b3038;--card:#1c2026;--accent:#5b8cf5;--warn:#fb923c;--ok:#4ade80;--red:#f87171}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--card);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center}
h1{font-size:15px;margin:0;font-weight:600}
.tag{color:var(--mut)}
.tag b{color:var(--fg);font-weight:600}
button{font:inherit;padding:5px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer}
button:hover{border-color:var(--accent);color:var(--accent)}
button.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
main{padding:16px;display:grid;gap:16px}
section{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
h2{font-size:14px;margin:0 0 10px;font-weight:600;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.pill{font-size:12px;padding:1px 8px;border-radius:99px;border:1px solid var(--line);color:var(--mut)}
.pill.live{color:var(--ok);border-color:var(--ok)}
.pill.done{color:var(--mut)}
.title{color:var(--mut);margin:0 0 10px;font-size:13px;word-break:break-all}
.ops{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.ops label{display:flex;align-items:center;gap:4px;font-weight:600}
.pill input.optfix{width:52px;border:1px solid var(--line);border-radius:4px;background:var(--bg);color:var(--fg);text-align:center;font:inherit;padding:1px 4px}
.ops input{width:92px;padding:4px 6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font-family:ui-monospace,Menlo,Consolas,monospace}
.dist{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;font-size:13px;white-space:nowrap}
th,td{border:1px solid var(--line);padding:3px 6px;text-align:center}
th{background:var(--bg);position:sticky;top:0}
td.name{text-align:left;position:sticky;left:0;background:var(--card);font-weight:600;max-width:150px;overflow:hidden;text-overflow:ellipsis}
th.name{left:0;z-index:2}
td input{width:46px;border:1px solid transparent;background:transparent;color:inherit;text-align:center;font:inherit;border-radius:4px}
td input:hover{border-color:var(--line)}
td input:focus{border-color:var(--accent);outline:none;background:var(--bg)}
td.manual{background:color-mix(in srgb,var(--red) 12%,transparent)}
td.manual input{color:var(--red);font-weight:700}
td.absent input{color:var(--mut)}
.sum{color:var(--mut)}
.err{color:var(--warn)}
.hint{color:var(--mut);font-size:12px;margin-top:8px}
#toast{position:fixed;right:16px;bottom:16px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px;opacity:0;transition:.2s;pointer-events:none}
#toast.on{opacity:1}
</style></head><body>
<header>
  <h1>文字博弈 · 主持台</h1>
  <span class="tag" id="state"></span>
  <span class="tag" id="count"></span>
  <label class="tag"><input type="checkbox" id="absent"> 未交票按 A 计分</label>
  <button id="dl">下载复盘</button>
  <button id="send" class="primary">发复盘到群</button>
</header>
<main>
  <section id="rounds"></section>
  <section>
    <h2>总表 <span class="pill">选项和得分都可以直接改，改完自动重算后面所有累计</span></h2>
    <div class="scroll" id="table"></div>
    <div class="hint">
  <b style="color:var(--red)">标红的分数 = 你手动改过的</b>，一律按加法计入累计，不再被上面的式子覆盖；
  改任何一格，这个人整行都会从第 1 题起、按各轮的式子重算一遍，标红的格子原样保留。
  想让某个标红格回到自动计算，把它清空即可。
</div>
  </section>
</main>
<div id="toast"></div>
<script>
const $=s=>document.querySelector(s);
let board=null, busy=false, sig="";

// 只把"结构性变化"纳入签名:新一轮、状态变了、有人交票、名单变动
function signature(b){
  return JSON.stringify([b.game.round,b.game.status,b.game.signup_open,b.game.absent_as_a,b.players.length,
    b.rounds.map(r=>[r.round,r.status,r.options,r.dist,r.absent.length])]);
}
function apply(b){board=b;sig=signature(b);render()}

function toast(t,bad){const e=$("#toast");e.textContent=t;e.style.color=bad?"var(--warn)":"var(--fg)";e.classList.add("on");clearTimeout(e._t);e._t=setTimeout(()=>e.classList.remove("on"),2600)}

async function api(url,method,body){
  busy=true;
  try{
    const r=await fetch(url,{method,headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):null});
    const j=await r.json();
    if(j.status!=="success"){toast(j.data||"操作失败",true);return null}
    if(j.data&&j.data.game){apply(j.data)}
    return j.data;
  }catch(e){toast(""+e,true);return null}
  finally{busy=false}
}

async function load(){
  if(busy)return;
  const r=await fetch("/hjd/textgame/board");const j=await r.json();
  if(j.status!=="success"){$("#state").textContent=j.data||"无数据";return}
  const now=signature(j.data);
  const typing=document.activeElement&&document.activeElement.tagName==="INPUT";
  // 正在输入且没有结构性变化就别打扰;新一轮之类的变化则强制刷新,并把焦点还回去
  if(typing&&now===sig)return;
  apply(j.data);
}

function render(){
  // 记住正在编辑的那一格,渲染完还回去,免得自动刷新打断输入
  const act=document.activeElement, key=act&&act.dataset?act.dataset.key:null;
  const keep=key?{val:act.value,pos:act.selectionStart}:null;
  const g=board.game,ps=board.players,rs=board.rounds;
  $("#state").innerHTML=`<b>${g.status}</b>　当前第 <b>${g.round||0}</b> 题　报名 <b>${g.signup_open?"开放":"已关闭"}</b>`;
  $("#count").innerHTML=`玩家 <b>${ps.length}</b> 人`;
  $("#absent").checked=g.absent_as_a;

  // 题块，当前题在最上
  $("#rounds").innerHTML=rs.length?[...rs].reverse().map(r=>{
    const live=r.status==="收集中";
    const done=ps.length-r.absent.length;
    const opts=(r.options||"").split("")||[];
    return `<div style="padding:6px 0;border-bottom:1px solid var(--line)">
      <h2>第 ${r.round} 题
        <span class="pill ${live?"live":"done"}">${r.status}</span>
        <span class="pill">选项 ${r.options?opts.join("/"):"未识别"}</span>
        <span class="pill">识别错了就填最后一个选项 <input class="optfix" data-key="f${r.round}" value="${r.options?r.options.slice(-1):""}"
          maxlength="8" placeholder="F" onchange="setOptions(${r.round},this.value)"></span>
        <span class="pill">已交 ${done}/${ps.length}</span>
        ${r.dist?`<span class="pill dist">${r.dist}</span>`:""}
      </h2>
      ${r.title?`<p class="title">${esc(r.title)}</p>`:""}
      <div class="ops" data-round="${r.round}">
        ${opts.map(o=>`<label>${o}<input data-op="${o}" data-key="o${r.round}-${o}" value="${esc(r.ops[o]||"")}" placeholder="+2"></label>`).join("")}
        ${opts.length?`<button class="primary" onclick="saveOps(${r.round})">保存并算分</button>`:'<span class="tag">题面里没识别出选项，请在总表里手动填分</span>'}
      </div>
    </div>`;
  }).join(""):'<span class="tag">还没有开始任何一题</span>';

  // 总表
  let h="<table><thead><tr><th class='name'>玩家</th>";
  rs.forEach(r=>h+=`<th colspan="3">第${r.round}题</th>`);
  h+="<th>总分</th><th>排名</th></tr><tr><th class='name'></th>";
  rs.forEach(()=>h+="<th>选</th><th>分</th><th class='sum'>累计</th>");
  h+="<th></th><th></th></tr></thead><tbody>";
  const rank={};board.rank.forEach(r=>rank[r.user]=r);
  ps.forEach(p=>{
    h+=`<tr><td class="name" title="${esc(p.user)}">${esc(p.name||p.user)}</td>`;
    rs.forEach(r=>{
      const c=(board.votes[r.round]||{})[p.user]||{};
      const absent=!c.choice?" absent":"";
      h+=`<td class="${absent}"><input data-key="c${r.round}-${p.user}" value="${c.choice||""}" maxlength="1"
            onchange="setChoice(${r.round},'${p.user}',this.value)"></td>`;
      h+=`<td class="${c.manual?"manual":""}"><input data-key="s${r.round}-${p.user}" value="${c.score??""}"
            onchange="setScore(${r.round},'${p.user}',this.value)"></td>`;
      h+=`<td class="sum">${c.total??""}</td>`;
    });
    h+=`<td><b>${rank[p.user]?fmt(rank[p.user].total):""}</b></td><td>${rank[p.user]?rank[p.user].rank:""}</td></tr>`;
  });
  $("#table").innerHTML=h+"</tbody></table>";

  if(keep){
    const el=document.querySelector(`[data-key="${key}"]`);
    if(el){el.value=keep.val;el.focus();try{el.setSelectionRange(keep.pos,keep.pos)}catch(e){}}
  }
}

const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt=n=>Number.isInteger(n)?n:n;

function saveOps(round){
  const box=document.querySelector(`.ops[data-round="${round}"]`);
  const ops={};box.querySelectorAll("input[data-op]").forEach(i=>ops[i.dataset.op]=i.value);
  api("/hjd/textgame/ops","PUT",{round,ops}).then(d=>d&&toast(`第${round}题已算分`));
}
function setOptions(round,options){
  api("/hjd/textgame/options","PUT",{round,options}).then(d=>d&&toast("选项集已改"));
}
function setChoice(round,user,choice){
  api("/hjd/textgame/choice","PUT",{round,user,choice}).then(d=>d&&toast("已改选项"));
}
function setScore(round,user,score){
  api("/hjd/textgame/score","PUT",{round,user,score})
    .then(d=>d&&toast(score===""?"已恢复自动算分":"已改分"));
}

$("#absent").onchange=e=>api("/hjd/textgame/absent","PUT",{absent_as_a:e.target.checked}).then(d=>d&&toast("已重算"));
$("#dl").onclick=()=>location.href="/hjd/textgame/excel";
$("#send").onclick=()=>api("/hjd/textgame/excel","POST",{send:true}).then(d=>d&&toast(d));

load();setInterval(load,3000);
</script></body></html>
"""
