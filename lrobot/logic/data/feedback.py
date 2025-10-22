"""反馈相关"""

import json

from config import database_update, database_query


async def feedback_reorder():
    """重新计算 seq"""
    # 未过期
    query_valid = """
        SELECT id FROM system_feedback
        WHERE period > NOW()
        ORDER BY period, id
    """
    rows_valid = await database_query(query_valid)
    for idx, row in enumerate(rows_valid, start=1):
        await database_update("UPDATE system_feedback SET seq=%s WHERE id=%s", (idx, row["id"]))

    # 已过期
    query_expired = """
        SELECT id FROM system_feedback
        WHERE period <= NOW()
        ORDER BY period DESC, id
    """
    rows_expired = await database_query(query_expired)
    for idx, row in enumerate(rows_expired, start=1):
        await database_update("UPDATE system_feedback SET seq=%s WHERE id=%s", (-idx, row["id"]))

async def feedback_set(name, period, questions):
    """设置收集表"""
    questions_json = json.dumps(questions, ensure_ascii=False)
    responses_json = json.dumps({}, ensure_ascii=False)
    query = """
    INSERT INTO system_feedback (name, questions, responses, period)
    VALUES (%s, %s, %s, %s)
    """
    await database_update(query, (name, questions_json, responses_json, period))
    await feedback_reorder()


async def feedback_delete(seq):
    """删除收集表"""
    rows = await database_query("SELECT 1 FROM system_feedback WHERE seq=%s", (seq))
    if not rows:
        return False
    await database_update("DELETE FROM system_feedback WHERE seq=%s", (seq,))
    await feedback_reorder()
    return True

async def feedback_list(history=False):
    """获取收集表列表"""
    await feedback_reorder()
    if history:
        query = """SELECT seq, name FROM system_feedback ORDER BY seq"""
    else:
        query = """SELECT seq, name FROM system_feedback WHERE seq > 0 ORDER BY seq"""

    rows = await database_query(query)
    result_list = [f"{row['seq']}:{row['name']}" for row in rows]
    return "\n".join(result_list)


async def feedback_start(seq):
    """获取收集表中第一个问题"""
    query = "SELECT seq, questions FROM system_feedback WHERE seq = %s AND period > NOW()"
    rows = await database_query(query, (seq,))

    if not rows:
        return None

    questions = json.loads(rows[0]["questions"])

    if not questions:
        return None
    return f"{questions[0]['id']}.{questions[0]['text']}"


async def feedback_write(seq, num, user, text):
    """记录当前回答并取出下一个问题"""
    query = "SELECT seq,responses, questions FROM system_feedback WHERE seq=%s"
    rows = await database_query(query, (seq,))
    if not rows:
        return None
    responses = json.loads(rows[0]["responses"] or "{}")
    questions = json.loads(rows[0]["questions"])
    if str(num) not in responses:
        responses[str(num)] = {}
    responses[str(num)][user] = text
    update_sql = "UPDATE system_feedback SET responses=%s WHERE seq=%s"
    await database_update(update_sql, (json.dumps(responses, ensure_ascii=False), seq))
    nextnum = num + 1
    question = None
    for q in questions:
        if q["id"] == nextnum:
            question = q
            break
    if question:
        return f"{question['id']}.{question['text']}"
    else:
        return None


async def feedback_export(seq):
    """导出收集表结果为文字"""
    query = "SELECT questions, responses FROM system_feedback WHERE seq=%s"
    rows = await database_query(query, (seq,))
    if not rows:
        return None

    questions = json.loads(rows[0]["questions"])
    responses = json.loads(rows[0]["responses"] or "{}")

    result_lines = []
    for q in questions:
        qid, qtext = q["id"], q["text"]
        result_lines.append(f"问题{qid}: {qtext}")
        if str(qid) in responses:
            for user, ans in responses[str(qid)].items():
                result_lines.append(f"{user}: {ans}")
        else:
            result_lines.append("（暂无回答）")
        result_lines.append("")

    return "\n".join(result_lines)
