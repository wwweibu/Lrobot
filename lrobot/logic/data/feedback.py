"""反馈相关"""

import json

from config import database_update, database_query


async def feedback_set(name, period, questions):
    """设置收集表"""
    questions_json = json.dumps(questions, ensure_ascii=False)
    responses_json = json.dumps({}, ensure_ascii=False)
    query = """
    INSERT INTO system_feedback (name, questions, responses, period)
    VALUES (%s, %s, %s, %s)
    """
    await database_update(query, (name, questions_json, responses_json, period))


async def feedback_list(history=False):
    """获取收集表列表"""
    if history:
        query = """ SELECT id, name FROM system_feedback ORDER BY id DESC"""
    else:
        query = """
            SELECT id, name FROM system_feedback
            WHERE period > NOW()
            ORDER BY id DESC
        """
    rows = await database_query(query)

    result_list = [f"{row['id']}:{row['name']}" for row in rows]
    return "\n".join(result_list)


async def feedback_start(id):
    """获取收集表中第一个问题"""
    query = "SELECT id, questions FROM system_feedback WHERE id = %s AND period > NOW()"
    rows = await database_query(query, (id,))

    if not rows:
        return None

    questions = json.loads(rows[0]["questions"])

    if not questions:
        return None
    return str(questions[0]["id"]) + questions[0]["text"]


async def feedback_write(id, num, user, text):
    """记录当前回答并取出下一个问题"""
    query = "SELECT id,responses, questions FROM system_feedback WHERE id=%s"
    rows = await database_query(query, (id,))
    if not rows:
        return None
    responses = json.loads(rows[0]["responses"] or "{}")
    questions = json.loads(rows[0]["questions"])
    if str(num) not in responses:
        responses[str(num)] = {}
    responses[str(num)][user] = text
    update_sql = "UPDATE system_feedback SET responses=%s WHERE id=%s"
    await database_update(update_sql, (json.dumps(responses, ensure_ascii=False), id))
    nextnum = num + 1
    question = None
    for q in questions:
        if q["id"] == nextnum:
            question = q
            break
    if question:
        return str(question["id"]) + question["text"]
    else:
        return None


async def feedback_export(id):
    """导出收集表结果为文字"""
    query = "SELECT questions, responses FROM system_feedback WHERE id=%s"
    rows = await database_query(query, (id,))
    if not rows:
        return None

    questions = json.loads(rows[0]["questions"])
    responses = json.loads(rows[0]["responses"] or "{}")

    result_lines = []
    for q in questions:
        qid, qtext = q["id"], q["text"]
        result_lines.append(f"问题{qid}：{qtext}")
        if str(qid) in responses:
            for user, ans in responses[str(qid)].items():
                result_lines.append(f"{user}: {ans}")
        else:
            result_lines.append("（暂无回答）")
        result_lines.append("")

    return "\n".join(result_lines)
